from .micronutrients import micronutrients
import pandas as pd
import asciichartpy
import shutil
from rich.console import Console
from rich.table import Table


def filter_complete(data):
    return data[data['Completed'] == True]


def filter_out_under(data, under):
    under = float(under)
    return data[data["Energy (kcal)"] > under]


def filter_out_over(data, over):
    over = float(over)
    return data[data["Energy (kcal)"] < over]


def filter_since(data, since, filter_by="Date"):
    return data[data[filter_by] >= since]


def filter_by_nutrient(data, nutrients, date_column_name="Date"):
    keep_columns = [*nutrients, date_column_name]
    return data.filter(items=keep_columns)


def merge_summary_and_foods_data(summary_df, servings_df):
    merged_df = summary_df.copy()
    merged_df['_foods'] = merged_df['Date'].apply(
        lambda date: servings_df[servings_df['Day'] == date].to_dict(orient='records')
    )
    return merged_df


def calculate_total_avg(data):
    invalid_fieldnames = ["Date", "Completed", "_foods"]
    valid_columns = [col for col in data.columns if col not in invalid_fieldnames]
    
    total_avgs = round(data[valid_columns].mean(), 2).to_dict()
    return total_avgs


def normalize_nutrient_name(input):
    try:
        normalized = micronutrients[input.lower()]
        return normalized
    except KeyError:
        print(f"Failed to find {input}.")
        exit(1)


def plot_nutrients(data, nutrients):
    terminal_size = shutil.get_terminal_size((80, 20))
    width = terminal_size.columns - 20 
    height = terminal_size.lines - 5 

    for nutrient in nutrients:
        dates = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d').tolist()
        values = data[nutrient].tolist()
        
        if len(values) > width:
            factor = len(values) // width
            condensed_values = values[::factor]
        else:
            condensed_values = values
        
        print(f"\n{nutrient} over time ({dates[0]} - {dates[-1]})")

        print(asciichartpy.plot(condensed_values, {'height': height}))


def identify_nutrient_density(data, nutrient, per="Energy (kcal)", top=5):
    foods = {}

    for _, row in data.iterrows():
        food_name = row["Food Name"]
        nutrient_value = row[nutrient]
        units = row[per]
        day = row["Day"]

        if (
            pd.notna(nutrient_value) 
            and nutrient_value > 0 
            and pd.notna(units) 
            and units > 0
        ):
            density = round(nutrient_value / units, 3)
            """
            if the new density exists in the map and the value 
            differs by more than 1% of the existing value, 
            then add it in with the date to differentiate the two.
            """
            if food_name not in foods:
                foods[food_name] = density
            elif abs(density - foods[food_name]) > (density * 0.01):
                foods[f"{food_name} ({day})"] = density

    sorted_items = sorted(foods.items(), key=lambda item: item[1], reverse=True)
    top_items = [{"name": key, f"{nutrient} per calorie": value} for key, value in sorted_items[:top]]

    return top_items


def print_table(data, title, type):
    table = Table(title=title)

    if type == "averages":
        table.add_column("Nutrient")
        table.add_column("Average/day")

        for k, v in data.items():
            table.add_row(k, str(v))

    if type == "density":
        table.add_column("Food")
        table.add_column(list(data[0].keys())[1])

        for i in data:
            table.add_row(i["name"], str(i[list(i.keys())[1]]))

    console = Console()
    console.print(table)