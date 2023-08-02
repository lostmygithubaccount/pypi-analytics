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
if len(sys.argv) == 1:
    ibis.options.interactive = True

    # get tables
    packages = con.table("packages")
    deps = con.table("deps")
    wheels = con.table("wheels")
    maintainers = con.table("maintainers")
    package_urls = con.table("package_urls")
    scorecard_checks = con.table("scorecard_checks")
else:
    ibis.options.interactive = False

    # get tables
    packages = memcon.table("packages")
    deps = memcon.table("deps")
    wheels = memcon.table("wheels")
    maintainers = memcon.table("maintainers")
    package_urls = memcon.table("package_urls")
    scorecard_checks = memcon.table("scorecard_checks")

    # TODO: fix pending issue (https://github.com/duckdblabs/sqlite_scanner/issues/47)
    packages = packages.drop("yanked", "has_binary_wheel", "has_vulnerabilities").drop(
        "in_google_assured_oss"
    )

    con.create_table("packages", packages.to_pyarrow(), overwrite=True)
    con.create_table("deps", deps.to_pyarrow(), overwrite=True)
    con.create_table("wheels", wheels.to_pyarrow(), overwrite=True)
    con.create_table("maintainers", maintainers.to_pyarrow(), overwrite=True)
    con.create_table("package_urls", package_urls.to_pyarrow(), overwrite=True)
    con.create_table("scorecard_checks", scorecard_checks.to_pyarrow(), overwrite=True)
