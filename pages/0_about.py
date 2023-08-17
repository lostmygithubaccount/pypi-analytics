# imports
import toml
import ibis

import streamlit as st
import plotly.io as pio
import plotly.express as px
import ibis.selectors as s

from datetime import datetime, timedelta

# options
## config.toml
config = toml.load("config.toml")["app"]

## streamlit config
st.set_page_config()

f"""
# Demo: Ibis + DuckDB + MotherDuck + Streamlit + GitHub

**Work in progress**

## What?

This project is a demo of an analysis project with Ibis and other cool projects.

## Why?

A [great datset on PyPI downloads](https://github.com/sethmlarson/pypi-data) was shared [including some code](ihttps://github.com/gforsyth/ibis-tutorial/blob/main/03%20-%20Playing%20with%20PyPI.ipynb) that was used in the EuroSciPy tutorial on Ibis.

I wanted to automate it and make it a dynamic app with Python and a cool OSS software stack + free cloud services.

## How?

The source code can be found here: https://github.com/lostmygithubaccount/pypi-analytics.

The tools and services used include:

- Ibis (dataframe library)
- GitHub releases (source data)
- DuckDB (database and query engine)
- MotherDuck (cloud service for DuckDB)
- Streamlit (dashboard)
- Streamlit Community Cloud (cloud service for Streamlit)
- GitHub (source control, CI/CD)
- justfile (command runner)
- TOML (configuration)

The Python requirements are:
"""

with open("requirements.txt") as f:
    requirements_code = f.read()

with st.expander("Show requirements.txt", expanded=False):
    st.code(requirements_code, line_numbers=True, language="text")

"""

The `justfile` defines the commands -- let's get an overview and dig into how the project is used:

"""

with open("justfile") as f:
    justfile_code = f.read()

with st.expander("Show justfile", expanded=False):
    st.code(justfile_code, line_numbers=True, language="makefile")

"""
The `config.toml` file defines the configuration for the project:
"""

with open("config.toml") as f:
    config_code = f.read()

with st.expander("Show config.toml", expanded=False):
    st.code(config_code, line_numbers=True, language="toml")


"""
### Ingesting data

The data lives in GitHub releases on [sethmlarson/pypi-data](https://github.com/sethmlarson/pypi-data). We use the GitHub CLI (locally and in an Action) to download and unzip the data into a local SQLite database.

The `just download` command above handles that for us.

### Loading into DuckDB

Ibis with the DuckDB backend is used to transfer the data efficiently from SQLite into DuckDB. While DuckDB can attach to SQLite databases (shown in the code), a copy is created for easy synchronization with MotherDuck for use in the Streamlit dashboard here.
"""

with open("transform.py") as f:
    transform_code = f.read()

with st.expander("Show transform.py", expanded=False):
    st.code(transform_code, line_numbers=True, language="python")
"""

### Exploratory data analysis

Having a quick iteration roop for exploring and analyzing the data, then transforming it into the proper shape for BI and ML, is critical. To achieve this, I setup an `eda.py` file that contains code I run every new Python session:
"""

with open("eda.py") as f:
    eda_code = f.read()

with st.expander("Show eda.py", expanded=False):
    st.code(eda_code, line_numbers=True, language="python")

"""

I can then run `ipython -i eda.py` to get a Python REPL with all the data loaded and ready to go. This makes it easy to explore and visualize the data.

### Defining metrics

Metrics are easily defined (and reusable) as Ibis expressions. Since we're deploying this with Streamlit and the project isn't huge, we simply keep the metrics definition in the BI layer:

"""
with open("metrics.py") as f:
    metrics_code = f.read()

with st.expander("Show metrics.py", expanded=False):
    st.code(metrics_code, line_numbers=True, language="python")
"""

Notice it was easy to iterate with EDA, transform and cache the data into a local database, and take my exploration and visualization directly to a locally deployed dashboard.

### Deploying and automating

Now, I need to automate the data pipeline and create a public dashboard. Time to move to a hybrid local + cloud approach.

Fortunately, this is easy with GitHub, Ibis, DuckDB, MotherDuck, Streamlit, and Streamlit Community Cloud.

We first copy over local DuckDB tables to MotherDuck:
"""

with open("export_md.py") as f:
    export_md_code = f.read()

with st.expander("Show export_md.py", expanded=False):
    st.code(export_md_code, line_numbers=True, language="python")

"""
 Notice that we can just switch the value in the `config.toml` to switch between a local DuckDB cache and the production MotherDuck database.

Since our tasks are defined in the `justfile` and we have a `requirements.txt` file, we can easily automate the end-to-end pipeline in a simple GitHub Action:
"""

with open(".github/workflows/cicd.yaml") as f:
    cicd_code = f.read()

with st.expander("Show cicd.yaml", expanded=False):
    st.code(cicd_code, line_numbers=True, language="yaml")
"""

This checks out the repository, sets up the Python environment, ingests the data source, transforms the data into DuckDB tables, and syncs those tables to MotherDuck.

It runs on PRs (that change relevant files), every day, and on a manual trigger.

With that, data ingestion and transformation is automated. All that's left is to deploy with app to Streamlit Community Cloud, which is just a few clicks in their GUI!

## Next steps

???
"""
