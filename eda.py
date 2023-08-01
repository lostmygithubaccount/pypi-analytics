# imports
import os
import sys
import toml
import ibis
import ibis.selectors as s
import logging as log
import seaborn as sns
import plotly.io as pio
import plotly.express as px
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from datetime import datetime, timedelta, date

# configuration
## logger
log.basicConfig(level=log.INFO)

## config.toml
config = toml.load("config.toml")["eda"]

## matplotlib config
plt.style.use("dark_background")

## seaborn config
sns.set(style="darkgrid")
sns.set(rc={"figure.figsize": (12, 10)})

## plotly config
pio.templates.default = "plotly_dark"

## variables

# load in data
if len(sys.argv) == 1:
    load_dotenv()
    database = config["target"]
    log.info(f"database: {database}")
    con = ibis.connect(f"duckdb://{database}")
    ibis.options.interactive = True

# produce data
else:
    datbase = config["target"]
    con = ibis.connect(f"duckdb://{database}")
    ibis.options.interactive = False

    ## scratch
