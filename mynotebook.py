import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

input_folder = Path('X:/EonLabs_TTA/input')
output_folder = Path('X:/EonLabs_TTA/output')

hourly_data_filename = 'hourly_data.csv'
weekly_data_filename = 'weekly_data.csv'
monthly_data_filename = 'monthly_data.csv'

output_filename = 'consistent_hourly_data.csv'

"""## 1.0 Read the data"""

hourly_df = pd.read_csv(input_folder/hourly_data_filename)
weekly_df = pd.read_csv(input_folder/weekly_data_filename)
monthly_df = pd.read_csv(input_folder/monthly_data_filename)

# format the date values
hourly_df['date'] = pd.to_datetime(hourly_df['date'])
weekly_df['date'] = pd.to_datetime(weekly_df['date'])
monthly_df['date'] = pd.to_datetime(monthly_df['date'])

"""## 2.0 Deriviation - consistent hourly data

What I am going to do is to:
1. use the monthly data to calculate the consistent weekly data (year by year)
2. use the result from step 1 to calculate consistent hourly data (week by week)

### 2.1 Make the weekly data consistent
"""

# extract the year value from the date
# weekly_df['year'] = weekly_df['date'].dt.isocalendar().year # this returns the ISO year which is different from what people commonly use
weekly_df['year'] = weekly_df['date'].dt.year
monthly_df['year'] = monthly_df['date'].dt.year

# calculate the conversion ratios in year by year levels
value_year_consistent = monthly_df[['year', 'value_month']].groupby(['year'])\
    .sum().reset_index().rename(columns={'value_month': 'value_year_consistent'})

value_year_shares = weekly_df[['year', 'value_week']].groupby(['year'])\
    .sum().reset_index().rename(columns={'value_week': 'value_year_shares'})

stage2_1_ratio = value_year_consistent.merge(value_year_shares)
stage2_1_ratio['ratio2_1'] = stage2_1_ratio['value_year_consistent']/stage2_1_ratio['value_year_shares']

# apply the ratio to get consistent weekly data
weekly_df = weekly_df.merge(stage2_1_ratio[['year','ratio2_1']])
weekly_df['value_week_consistent'] = weekly_df['value_week'] * weekly_df['ratio2_1'] * (52/12) # compensate for 52 weeks and 12 months per year

"""### 2.2 Make the hourly data consistent"""

# extract the year and week values from the date
hourly_df['year'] = hourly_df['date'].dt.year
hourly_df['week_of_year'] = hourly_df['date'].dt.isocalendar().week # ISO week is 1 week off from the common weeks, but (month, week) pair is still a unique key...

weekly_df['year'] = weekly_df['date'].dt.year
weekly_df['week_of_year'] = weekly_df['date'].dt.isocalendar().week

# calculate the conversion ratios in week by week levels
value_week_consistent = weekly_df[['year', 'week_of_year','value_week_consistent']].groupby(['year', 'week_of_year'])\
    .sum().reset_index()

value_week_shares = hourly_df[['year', 'week_of_year', 'value_hour']].groupby(['year', 'week_of_year'])\
    .sum().reset_index().rename(columns={'value_hour': 'value_week_shares'})

stage2_2_ratio = value_week_consistent.merge(value_week_shares)
stage2_2_ratio['ratio2_2'] = stage2_2_ratio['value_week_consistent']/stage2_2_ratio['value_week_shares']

# apply the ratio to get consistent hourly data
hourly_df = hourly_df.merge(stage2_2_ratio[['year','week_of_year','ratio2_2']])
hourly_df['value_hour_consistent'] = hourly_df['value_hour'] * hourly_df['ratio2_2'] * (24*7) # compensate for 7*24 hours per week

## 4.0 Save the result

consistent_hourly_df = hourly_df[['time_hour', 'value_hour_consistent', 'date']].copy()\
    .rename(columns={'value_hour_consistent': 'value_hour'})

consistent_hourly_df.to_csv(output_folder/output_filename, index=False)

## do a plot
consistent_hourly_df.plot(x='date', y='value_hour', figsize=(18,6))
plt.show()

