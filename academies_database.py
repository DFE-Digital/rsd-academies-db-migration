import pandas as pd
import panel as pn
import json
from usage_reports import reports_usage
from pipelines import pipelines_usage

pn.extension('tabulator')

"""
Grab data about the different web services. This JSON file is manually kept
up-to-date with the latest information gathered.
"""
with (open("./services.json")) as services_file:
    services = json.load(services_file)

"""
Retrieve the list of schemas and tables from the CSV file (see README) and:

- rename columns to 'schema' and 'table'
- lowercase all values

For the latter point, we do this as SQL Server is case insensitive and we
need to be able to match based on values without worrying about case.
"""
prod_structure = pd.read_csv("database_structure.csv")
schema_tables = prod_structure[["TABLE_SCHEMA", "TABLE_NAME"]].drop_duplicates()
schema_tables = schema_tables.rename(columns={"TABLE_SCHEMA": "schema", "TABLE_NAME": "table"})
schema_tables['schema'] = schema_tables['schema'].apply(str.lower)
schema_tables['table'] = schema_tables['table'].apply(str.lower)

"""
For each of the web services, and with the extracted usage CSVs:

- rename the column "repo_name" to "name"
- lowercase schema and table values (as above)
- merge the usage of the service into our primary data frame based on schema and table
- blank out empty values (rather than the default "None" value from pandas)
"""
for service in services:
    data = pd.read_csv(f"services-usage/{service['repo_name']}.csv")
    data = data.rename(columns={service["repo_name"]: service["name"]})
    data['schema'] = data['schema'].apply(str.lower)
    data['table'] = data['table'].apply(str.lower)
    schema_tables = schema_tables.merge(data, how="outer", on=["schema", "table"])
    schema_tables[service["name"]].fillna('')

"""
Similarly to the service usage, we then want to merge in SQL view reports and
Azure Data Factory Pipeline usages into our primary data frame
"""
schema_tables = schema_tables.merge(reports_usage, how="outer", on=["schema", "table"])
schema_tables = schema_tables.merge(pipelines_usage, how="left", on=["schema", "table"])

"""
Sort the data frame alphabetically ascending based on schema and table
"""
schema_tables = schema_tables.sort_values(["schema", "table"], ignore_index = True, key=lambda col: col.str.lower())

"""
For each of the services, reports and pipeline names, we want to hold an array of each
that we will use later for the column grouping under the respective headings.
"""
service_names = [service["name"] for service in services]
report_names = [col for col in reports_usage.columns if col not in ['schema', 'table']]
pipeline_names = [col for col in pipelines_usage.columns if col not in ['schema', 'table']]

"""
For all of the usages, we want to count the number for each, and put into a
Total column for services, reports and pipelines. And then also, an overall
total count column.
"""
schema_tables['Services'] = schema_tables[service_names].count(axis=1)
schema_tables['Reports'] = schema_tables[report_names].count(axis=1)
schema_tables['Pipelines'] = schema_tables[pipeline_names].count(axis=1)
schema_tables['Total'] = schema_tables[['Services', 'Reports', 'Pipelines']].sum(axis=1)

"""
We have now prepared all of the various columns that we want to display, so
now we need to group columns based on type (services, reports and pipelines)
"""
db_headers = ["schema", "table"]
count_headers = ["Total", "Services", "Reports", "Pipelines"]
service_headers = service_names
report_headers = report_names
pipeline_headers = pipeline_names

schema_tables = schema_tables[db_headers + count_headers + service_headers + report_headers + pipeline_headers]

"""
Prepare the services table, including a count of the tables that are referenced
This will be visible in the top table of the web page
"""
services_data = pd.read_json("./services.json")
counts = [schema_tables[service["name"]].count() for service in services]
services_data["counts"] = counts
services_data["notes"].fillna('')

services_table = pn.widgets.Tabulator(
    services_data,
    disabled=True,
    show_index = False,
)

"""
Blank out any remaining values with an empty string rather than default "None"
"""
schema_tables = schema_tables.fillna("")

"""
Configuration for the Tabulator widget to render the data, including:

- column groupings
- freeze columns
- sizing
"""
db_usage_matrix = pn.widgets.Tabulator(
    schema_tables,
    groups={"Academies DB": db_headers, "Totals": count_headers, "Services": service_headers, "Reports": report_headers, "Pipelines": pipeline_headers},
    show_index = False,
    frozen_columns=["Academies DB", "Totals"],
    pagination=None,
    disabled=True,
    header_filters=True,
    configuration={
        "maxHeight": "100vh",
        "virtualDomHoz": True,
    },
)

"""
https://getbootstrap.com/docs/5.3/customize/color/#all-colors

Row highlighting logic
"""
def highlight_row(row):
    style = ''

    if row['Total'] == 0:
        style = 'color: #adb5bd;' # grey

    if row['Total'] == 1:
        style = 'background-color: #198754; color: white;' # green

    if row['Total'] > 1:
        style = 'background-color: #ffc107;' # yellow

    if row['Services'] > 0 and row['Reports'] > 0:
        style = 'background-color: #fd7e14;' # orange

    if row['Services'] > 0 and row['Pipelines'] > 0:
        style = 'background-color: #dc3545;' # red

    return [style] * len(row)

db_usage_matrix.style.apply(highlight_row, axis=1)

"""
Render to page
"""
app = pn.FlexBox(services_table, db_usage_matrix)
app.servable(title="Academies DB")

"""
If run directly, save the output to a static HTML file
"""
if __name__ == "__main__":
    app.save("index.html", title="Academies DB")
