# RSD Academies DB migration

This repository contains the code files to manage the academies database map, used to identify opportunities to improve its structure, support and management. Currently it:

- Extracts database usage directly from the projects (using `dotnet-ef` for the .NET projects, and the Rails console for `complete` project)
- Scans the source code for extra database usage (using a mixture of grep and regexes)
- Compiles this into tabular format for review (using python with pandas)

The academies database map is located here: https://rsd-academies-db-migration.fly.dev/

It is protected with HTTP authentication, and this can be requested in the DfE Slack in the #rsd-academies-db-working-group channel.

## Background to the Academies database

The Academies database has grown into something containing around 945 tables, and 45 different schemas. A number of different services all use it as their primary database, some sharing tables amongst themselves, and others used just for that single service.

In order for the services to function, a number of other data sources are required, and are imported into the Academies database via data pipelines, and then used by those services—effectively being used as a cache or mirror—mostly due to the lack of modern performant APIs (for example, GIAS) offered by those other data sources.
Data from the Academies database is also used as a source for a number of different business reports which are used to help make decisions and monitor the various services.

### Current issues

- Lack of visibility; who and what is reading and writing data from the database?
- Lack of ownership of data; who is responsible for what?
- Data quality; what data is redundant? Duplicate data? Outdated data?
- Open boundaries; mostly anyone can import data into the database, or use it as a data source for existing or new services or reporting. No clearly defined access controls which makes it hard to control, manage and support for the long term.
- Processes and standards; no structure, standards or processes; how are migrations handled? If I want to add a new table, how should I name it? etc.

### Objectives

Tame the beast that is the Academies database, and solve the issues outlined above:

- Gain visibility; we need to understand clearly how the existing Academies database is being used, and by who.
- Ownership; we need services to own the data that only they care about so that it can be removed as a shared concern/risk for the wider programme. Shared data also needs ownership.
- Ongoing development; we need to ensure that the ongoing development of services is only minimally affected by the work being done to improve the Academies database.
- Supportability; identify options to make the database more supportable, by splitting out concerns into multiple databases, providing that ownership to individual services, to reduce the overall database footprint.
- Standards and processes; have clear standards and processes in place for shared data, so that tools and libraries can be built on top of these for simple reusability and support amongst services that will use them.
- Trustworthiness; trust in the data presented in various RDS systems (in particular FIAT) has emerged as a particular issue for the services. One of the main reasons for this is redundant and/or duplicate data in the system, often stemming from more than one data source being used for any particular data point. This and other sources of distrust need to be explored further and addressed.

## Development

For local development, there are a number of scripts that you can use:

- `./scripts/bootstrap` will get python dependencies installed via poetry
- `./scripts/generate-data-usage-csvs` will scan service repos for database usage and create csv files used by pandas
- `./scripts/server` will start a web server for local development
- `./scripts/build` will generate an `index.html` file which can be used for deployments
- `./scripts/clean` will remove git repos for services and generated csv files

When changes are pushed to GitHub, it will run a workflow to build the HTML file and then deploy this to fly.io, protected by HTTP basic auth, served over HTTPS.

There are a number of required GitHub Actions secrets:

- `DATABASE_STRUCTURE_CONTENTS` - CSV contents of database structure CSV from Akhtar
- `REPORTING_VIEWS_DEPENDENCIES_CONTENTS` - CSV contents of report dependencies on schemas and tables
- `FLY_API_TOKEN` - for deploying of HTML to fly
- `NGINX_AUTH` - http auth credentials for nginx (`htpasswd` format)

### DATABASE_STRUCTURE_CONTENTS

This can be generated with the following SQL:

```sql
SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
```

### REPORTING_VIEWS_DEPENDENCIES_CONTENTS

This can be generated with the following SQL:

```sql
SELECT
    OBJECT_NAME(d.referencing_id) AS [view],
    d.referenced_schema_name AS [schema],
    d.referenced_entity_name AS [table]
FROM
    sys.sql_expression_dependencies AS d
    JOIN sys.views AS v ON d.referencing_id = v.object_id
WHERE
    v.schema_id = SCHEMA_ID('reports');
```

### PIPELINE_DEPENDENCIES_CONTENTS

This can be generated with the Azure CLI tool, using the following when authenticated:

```sh
az datafactory pipeline list \
    --subscription "DFE T1 Production" \
    --factory-name "adf-t1pr-sips-dataflow" \
    --resource-group "RG-T1PR-SIPS" | \
        jq '[ .[] | {name, procedures: [ .activities[] | .storedProcedureName ]} ]' > \
    pipeline_dependencies.json
```

### AZURE_DEVOPS_PAT

A personal access token (PAT) can be generated on this page:

https://dfe-gov-uk.visualstudio.com/_usersSettings/tokens

It only needs `Code (Read)` scope.
