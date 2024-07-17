import argparse
import pandas as pd
import numpy as np
import json


def get_args():
    parser = argparse.ArgumentParser(
        prog="cronometer analyzer",
        description="analyzes your cronometer data",
    )

    parser.add_argument('daily_summary_csv')
    parser.add_argument('servings_csv')
    parser.add_argument('-c', '--complete-only', action='store_true', default=False)
    parser.add_argument('-u', '--disregard-under')
    parser.add_argument('-a', '--disregard-above')
    parser.add_argument('-s', '--since')

    return parser.parse_args()


def parse_csv(file_path):
    try:
        return pd.read_csv(file_path, delimiter=',')
    except Exception as e:
        print(e)
        exit(1)


def merge_data(summary_df, servings_df):
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
    
    daily_avgs = data[valid_columns].mean().to_dict()
    return daily_avgs


if __name__ == "__main__":
    args = get_args()


    daily_summary_csv = args.daily_summary_csv
    servings_csv = args.servings_csv
    complete_only = args.complete_only
    disregard_under = args.disregard_under
    disregard_above = args.disregard_above
    since = args.since

    summary_df = parse_csv(daily_summary_csv)
    servings_df = parse_csv(servings_csv)

    merged_data = merge_data(summary_df, servings_df) 
    
    if complete_only:
        merged_data = filter_complete(merged_data)

    if disregard_under:
        merged_data = filter_out_under(merged_data, disregard_under)

    if since:
        merged_data = filter_since(merged_data, since)

    daily_avgs = calculate_daily_avg(merged_data)

    print(json.dumps(daily_avgs))
