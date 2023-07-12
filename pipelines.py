import json
import re
import pandas as pd

pipeline_references = []

with open("./pipeline_dependencies.json") as json_file:
    data = json.load(json_file)

    for pipeline in data:
        procedures = list(filter(None, pipeline['procedures']))

        if len(procedures) > 0:
            print("🚚 " + pipeline['name'])

        for activity in procedures:
            file = re.sub(r"\[(.*)\]\.\[(.*)\]", r"\1/Stored Procedures/\2.sql", activity)

            try:
                with open("./sip-adb-academies-datastore/sip-adb-acadamies-datastore/" + file) as proc_file:
                    print("\t 🔍 " + file)
                    matches = re.findall(r"(FROM|INTO|UPDATE)\s+\[(\w+)\]\.\[(\w+)\]", proc_file.read())

                    for match in matches:
                        _, schema, table = match
                        print("\t\t" + schema + "." + table)
                        pipeline_references.append((pipeline['name'], schema.lower(), table.lower()))
            except FileNotFoundError:
                print("\t 🚨 File not found: " + file)

if len(pipeline_references) > 0:
    pipeline_references = list(set(pipeline_references))

df = pd.DataFrame(pipeline_references, columns=['pipeline', 'schema', 'table'])

new_df = df.pivot_table(index=['schema', 'table'], columns='pipeline', aggfunc=lambda x: 1)

pipelines_usage = new_df.reset_index()
