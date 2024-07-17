import pandas as pd
from rich import print_json
import argparse
import json
import asciichartpy
import shutil


def get_args():
    parser = argparse.ArgumentParser(
        prog="cronometer analyzer",
        description="analyzes your cronometer data",
    )
    
    subparsers = parser.add_subparsers(dest='subcommand')
    average_parser = subparsers.add_parser('get-average')
    average_parser.add_argument('--summary', required=True, help="path to dailysummary.csv")
    average_parser.add_argument('--complete-only', action='store_true', help="calculate using complete days only")
    average_parser.add_argument('--disregard-above', help="disregard days over N calories", type=int)
    average_parser.add_argument('--disregard-under', help="disregard days under N calories", type=int)
    average_parser.add_argument('--since', help="calculate using days since (YYYY-MM-DD)")
    average_parser.add_argument('--json', action='store_true', help="return json output", default=True)

    time_parser = subparsers.add_parser('time')
    time_parser.add_argument('--summary', required=True, help="path to dailysummary.csv")
    time_parser.add_argument('--complete-only', action='store_true', help="calculate using complete days only")
    time_parser.add_argument('--since', help="calculate using days since (YYYY-MM-DD)")
    time_parser.add_argument('--track', help="nutrient to track", action='append', required=True)

    return parser.parse_args()


def parse_csv(file_path):
    try:
        return pd.read_csv(file_path, delimiter=',')
    except Exception as e:
        print(e)
        exit(1)


def merge_summary_and_foods_data(summary_df, servings_df):
    merged_df = summary_df.copy()
    merged_df['_foods'] = merged_df['Date'].apply(
        lambda date: servings_df[servings_df['Day'] == date].to_dict(orient='records')
    )
    return merged_df


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


def calculate_total_avg(data):
    invalid_fieldnames = ["Date", "Completed", "_foods"]
    valid_columns = [col for col in data.columns if col not in invalid_fieldnames]
    
    total_avgs = round(data[valid_columns].mean(), 2).to_dict()
    return total_avgs


def get_average(args):
    data = parse_csv(args.summary)
    
    if args.complete_only:
        data = filter_complete(data)
    if args.disregard_under:
        data = filter_out_under(data, args.disregard_under)
    if args.disregard_above:
        data = filter_out_over(data, args.disregard_above)
    if args.since:
        data = filter_since(data, args.since)

    total_avgs = calculate_total_avg(data)

    parsed_data = {"total_avgs": total_avgs}

    if args.json:
        print_json(json.dumps(parsed_data))
        exit(0)


def track_nutrients_over_time(args):
    data = parse_csv(args.summary)
    
    if args.complete_only:
        data = filter_complete(data)
    if args.since:
        data = filter_since(data, args.since)

    filtered_data = filter_by_nutrient(data, args.track)
    
    plot_nutrients(filtered_data, args.track)


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


if __name__ == "__main__":
    args = get_args()
    
    if args.subcommand == 'get-average':
        get_average(args)
    elif args.subcommand == 'time':
        track_nutrients_over_time(args)
