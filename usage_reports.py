import pandas as pd

df = pd.read_csv('reporting_views_dependencies.csv')

new_df = df.pivot_table(index=['schema', 'table'], columns='view', aggfunc=lambda x: 1)

reports_usage = new_df.reset_index()
