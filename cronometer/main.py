import pandas as pd
from rich import print_json
import argparse
import json

from .utils import (
    filter_by_nutrient, 
    filter_complete, 
    filter_out_over, 
    filter_out_under, 
    filter_since, 
    calculate_total_avg, 
    normalize_nutrient_name,
    plot_nutrients,
    identify_nutrient_density,
    print_table,
)


def get_args():
    parser = argparse.ArgumentParser(
        prog="cronometer analyzer",
        description="analyzes your cronometer data",
    )
    
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    average_parser = subparsers.add_parser("average", help="average daily intake of each tracked micronutrient")
    average_parser.add_argument("--summary", required=True, help="path to dailysummary.csv")
    average_parser.add_argument("--complete-only", action="store_true", help="calculate using complete days only")
    average_parser.add_argument("--disregard-above", help="disregard days over N calories", type=int)
    average_parser.add_argument("--disregard-under", help="disregard days under N calories", type=int)
    average_parser.add_argument("--since", help="calculate using days since (YYYY-MM-DD)")
    average_parser.add_argument("--json", action="store_true", help="return json output", default=False)

    time_parser = subparsers.add_parser("time", help="daily intake of a specified micronutrient over time")
    time_parser.add_argument("--summary", required=True, help="path to dailysummary.csv")
    time_parser.add_argument("--complete-only", action="store_true", help="calculate using complete days only")
    time_parser.add_argument("--since", help="calculate using days since (YYYY-MM-DD)")
    time_parser.add_argument("--nutrient", help="nutrient to track", action="append", required=True)

    density_parser = subparsers.add_parser("density", help="top N items by specified micronutrient density")
    density_parser.add_argument("--foods", required=True, help="path to servings.csv")
    density_parser.add_argument("--since", help="calculate using days since (YYYY-MM-DD)")
    density_parser.add_argument("--nutrient", help="nutrient to track", action="append", required=True)
    density_parser.add_argument("--top", type=int, help="number of items")
    density_parser.add_argument("--json", action="store_true", help="return json output", default=False)

    return parser.parse_args()
    

def parse_csv(file_path):
    try:
        return pd.read_csv(file_path, delimiter=",")
    except Exception as e:
        print(e)
        exit(1)


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
    parsed_data = total_avgs

    if args.json:
        print_json(json.dumps(parsed_data))
    else:
        print_table(parsed_data, title="Averages", type="averages")


def track_nutrients_over_time(args):
    data = parse_csv(args.summary)
    
    if args.complete_only:
        data = filter_complete(data)
    if args.since:
        data = filter_since(data, args.since)

    normalized_nutrient_names = []
    for nutrient in args.nutrient:
        normalized_nutrient_names.append(normalize_nutrient_name(nutrient.lower()))

    filtered_data = filter_by_nutrient(data, normalized_nutrient_names)
    
    plot_nutrients(filtered_data, normalized_nutrient_names)


def density(args):
    data = parse_csv(args.foods)

    top = 5
    if args.top:
        top = args.top

    if args.since:
        data = filter_since(data, args.since, "Day")

    per = "Energy (kcal)"

    normalized_nutrient_names = []
    for nutrient in args.nutrient:
        normalized_nutrient_names.append(normalize_nutrient_name(nutrient.lower()))

    for nutrient in normalized_nutrient_names:
        nutrient_density = identify_nutrient_density(data, nutrient, per, top)
        if args.json:
            print_json(json.dumps(nutrient_density))
        else:
            print_table(nutrient_density, title=f"", type="density")


def main():
    args = get_args()
    
    if args.subcommand == "average":
        get_average(args)
    elif args.subcommand == "time":
        track_nutrients_over_time(args)
    elif args.subcommand == "density":
        density(args)

    
if __name__ == "__main__":
    main()