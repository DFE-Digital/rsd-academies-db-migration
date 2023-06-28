import pandas as pd
import panel as pn
import json
from usage_reports import reports_usage

pn.extension('tabulator')

with (open("./services.json")) as services_file:
    services = json.load(services_file)

prod_structure = pd.read_csv("database_structure.csv")
schema_tables = prod_structure[["TABLE_SCHEMA", "TABLE_NAME"]].drop_duplicates()
# schema_tables.to_csv("reduced_database_structure.csv", index=False)
schema_tables = schema_tables.rename(columns={"TABLE_SCHEMA": "schema", "TABLE_NAME": "table"})

for service in services:
    data = pd.read_csv(f"services-usage/{service['repo_name']}.csv")
    data = data.rename(columns={service["repo_name"]: service["name"]})
    schema_tables = schema_tables.merge(data, how="outer", on=["schema", "table"])
    schema_tables[service["name"]].fillna('')

schema_tables = schema_tables.merge(reports_usage, how="outer", on=["schema", "table"])

schema_tables = schema_tables.sort_values(["schema", "table"], ignore_index = True, key=lambda col: col.str.lower())

service_names = [service["name"] for service in services]
report_names = [col for col in reports_usage.columns if col not in ['schema', 'table']]

schema_tables['Services'] = schema_tables[service_names].count(axis=1)
schema_tables['Reports'] = schema_tables[report_names].count(axis=1)
schema_tables['Total'] = schema_tables[['Services', 'Reports']].sum(axis=1)

# unused_tables = schema_tables[schema_tables['Services'] == 0]
used_tables = schema_tables[schema_tables['Services'] >= 1]

db_headers = ["schema", "table"] #[("Academies DB", x) for x in ["schema", "table"]]
count_headers = ["Total", "Services", "Reports"] #[("Usage", "Services Count")]
service_headers = service_names #[("Services", x) for x in services.keys()]
report_headers = report_names

schema_tables = schema_tables[db_headers + count_headers + service_headers + report_headers]

services_data = pd.read_json("./services.json")


counts = [schema_tables[service["name"]].count() for service in services]
services_data["counts"] = counts

def highlight_single_use(value):
    if value == 1:
        return 'background-color: green'
    elif value > 1:
        return 'background-color: orange'
    else:
        return ''

schema_tables = schema_tables.fillna("")

df_tab = pn.widgets.Tabulator(
    schema_tables,
    groups={"Academies DB": db_headers, "Totals": count_headers, "Services": service_headers, "Reports": report_headers},
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

    return [style] * len(row)

# df_tab.style.applymap(highlight_single_use, subset=["Services"])
df_tab.style.apply(highlight_row, axis=1)

services_data["notes"].fillna('')
services_table = pn.widgets.Tabulator(
    services_data,
    disabled=True,
    show_index = False,
)

reports_table = pn.widgets.Tabulator(reports_usage, disabled=True, show_index=False)

dial = pn.indicators.Dial(name='Tables in use', format="{value}", value=len(used_tables.index), bounds=(0, len(schema_tables.index)))

# app = pn.FlexBox(dial, services_table, df_tab)
app = pn.FlexBox(services_table, df_tab)
app.servable(title="Academies DB")

if __name__ == "__main__":
    app.save("index.html", title="Academies DB")
