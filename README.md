# Cronometer Analysis

CLI tool that provides an analysis of your Cronometer data.

## Setup

Clone the repo and install the project dependencies.
```bash
pip install -r requirements.txt
pip install .
```

Next, export your nutrition data from Cronometer. You can do this by logging into [cronometer.com](https://www.cronometer.com), navigating to More > Account, and exporting your Daily Nutrition and Food & Recipe entires for the desired timeframe. 

<img src="img/cronometer_export.png" width=250>

If you've been logging for a while, you may not be able to export the Food & Recipe entires for all time, so you may have to settle for a year.

## Average micronutrients/day

Returns your average quantity of each tracked micronutrient (glorified average of all columns).

```
cronometer average --summary path/to/dailysummary.csv
```

Optionally, set a time frame (`--since="2023-12-25"`) or exclude outlier days under or over certain calorie threshold (`--disregard-under=1000 --disregard-above=2600`). Additionally, you can disregard days that were not marked as "complete" (`--complete-only`).

```
cronometer average --summary path/to/dailysummary.csv --disregard-under=1000 --disregard-above=2600 --complete-only
```

## Micronutrients over time

Returns a line graph displaying the daily micronutrient over time. Provide the micronutrient you wish to track with the `--track` argument.

```
cronometer time --summary path/to/dailysummary.csv --track="Energy (kcal)"
```

<img src="img/over_time.png" width=350>

## Macronutrient density

Returns a list of the food items with the highest quantity of a particular micro-/macro-nutrient per calorie.

```
cronometer density --foods path/to/services.csv --since="2023-08-01" --top=10 --nutrient="protein"
```

# Local development

Run `python3 -m cronometer.main` followed by the appropriate command line args.