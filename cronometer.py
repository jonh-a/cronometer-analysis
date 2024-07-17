import pandas as pd
from rich import print_json
import argparse
import json


def get_args():
    parser = argparse.ArgumentParser(
        prog="cronometer analyzer",
        description="analyzes your cronometer data",
    )

    parser.add_argument('--summary', required=True, help="path to dailysummary.csv")
    parser.add_argument('--foods', required=False, help="path to servings.csv")
    parser.add_argument('--complete-only', action='store_true', help="calculate using complete days only")
    parser.add_argument('--disregard-under', help="disregard days under N calories", type=int)
    parser.add_argument('--disregard-above', help="disregard days over N calories", type=int)
    parser.add_argument('--since', help="calculate using days since (YYYY-MM-DD)")
    parser.add_argument('--json', action='store_true', help="return json output", default=True)

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


def calculate_daily_avg(data):
    invalid_fieldnames = ["Date", "Completed", "_foods"]
    valid_columns = [col for col in data.columns if col not in invalid_fieldnames]
    
    daily_avgs = round(data[valid_columns].mean(), 2).to_dict()
    return daily_avgs


if __name__ == "__main__":
    args = get_args()

    data = parse_csv(args.summary)

    if args.foods:
        servings_df = parse_csv(args.foods)
        data = merge_summary_and_foods_data(data, servings_df)
    
    if args.complete_only:
        data = filter_complete(data)

    if args.disregard_under:
        data = filter_out_under(data, args.disregard_under)

    if args.disregard_above:
        data = filter_out_over(data, args.disregard_above)

    if args.since:
        data = filter_since(data, args.since)

    daily_avgs = calculate_daily_avg(data)

    parsed_data = {
        "averages": {
            "daily_averages": daily_avgs,
        }
    }

    if args.json:
        print_json(json.dumps(parsed_data))
        exit(0)
