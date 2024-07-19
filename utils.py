from micronutrients import micronutrients

def filter_complete(data):
    return data[data['Completed'] == True]


def filter_out_under(data, under):
    under = float(under)
    return data[data["Energy (kcal)"] > under]


def filter_out_over(data, over):
    over = float(over)
    return data[data["Energy (kcal)"] < over]


def filter_since(data, since):
    return data[data["Date"] >= since]


def filter_by_nutrient(data, nutrients):
    keep_columns = [*nutrients, "Date"]
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