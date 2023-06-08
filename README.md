# RSD Academies DB migration

The Academies database has grown into something containing around 945 tables, and 45 different schemas. A number of different services all use it as their primary database, some sharing tables amongst themselves, and others used just for that single service.

In order for the services to function, a number of other data sources are required, and are imported into the Academies database via data pipelines, and then used by those services—effectively being used as a cache or mirror—mostly due to the lack of modern performant APIs (for example, GIAS) offered by those other data sources.
Data from the Academies database is also used as a source for a number of different business reports which are used to help make decisions and monitor the various services.

## Current issues

- Lack of visibility; who and what is reading and writing data from the database?
- Lack of ownership of data; who is responsible for what?
- Data quality; what data is redundant? Duplicate data? Outdated data?
- Open boundaries; mostly anyone can import data into the database, or use it as a data source for existing or new services or reporting. No clearly defined access controls which makes it hard to control, manage and support for the long term.
- Processes and standards; no structure, standards or processes; how are migrations handled? If I want to add a new table, how should I name it? etc.

## Objectives

Tame the beast that is the Academies database, and solve the issues outlined above:

- Gain visibility; we need to understand clearly how the existing Academies database is being used, and by who.
- Ownership; we need services to own the data that only they care about so that it can be removed as a shared concern/risk for the wider programme. Shared data also needs ownership.
- Ongoing development; we need to ensure that the ongoing development of services is only minimally affected by the work being done to improve the Academies database.
- Supportability; identify options to make the database more supportable, by splitting out concerns into multiple databases, providing that ownership to individual services, to reduce the overall database footprint.
- Standards and processes; have clear standards and processes in place for shared data, so that tools and libraries can be built on top of these for simple reusability and support amongst services that will use them.
- Trustworthiness; trust in the data presented in various RDS systems (in particular FIAT) has emerged as a particular issue for the services. One of the main reasons for this is redundant and/or duplicate data in the system, often stemming from more than one data source being used for any particular data point. This and other sources of distrust need to be explored further and addressed.

## Development

GitHub Actions secrets:

- `DATABASE_STRUCTURE_CONTENTS` - CSV contents of database structure CSV from Akhtar
- `FLY_API_TOKEN` - for deploying of HTML to fly
- `NGINX_AUTH` - http auth credentials for nginx
