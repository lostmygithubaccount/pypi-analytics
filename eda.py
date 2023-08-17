# imports
import os
import sys
import toml
import ibis
import ibis.selectors as s
import logging as log
import plotly.io as pio
import plotly.express as px

from dotenv import load_dotenv
from datetime import datetime, timedelta, date

# configuration
## logger
log.basicConfig(level=log.INFO)

## config.toml
config = toml.load("config.toml")["eda"]

## plotly config
pio.templates.default = "plotly_dark"

# load .env file
load_dotenv()

# setup stuff
source = config["source"]
target = config["target"]
log.info(f"source: {source}")
log.info(f"target: {target}")
memcon = ibis.connect("duckdb://")
con = ibis.connect(f"duckdb://{target}")
memcon.attach_sqlite(f"{source}", overwrite=True)

# load in data
ibis.options.interactive = True

# get tables
packages = con.table("packages")
deps = con.table("deps")
wheels = con.table("wheels")
maintainers = con.table("maintainers")
package_urls = con.table("package_urls")
scorecard_checks = con.table("scorecard_checks")
