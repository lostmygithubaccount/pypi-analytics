# imports
import toml
import ibis

import logging as log

from dotenv import load_dotenv

# configure logger
log.basicConfig(level=log.INFO)

# config.toml
config = toml.load("config.toml")["motherduck"]
eda_config = toml.load("config.toml")["eda"]
exclude_tables = config["exclude_tables"] if "exclude_tables" in config else []

# load env vars
load_dotenv()

# connect to motherduck
log.info(f"Export database: {config['database']}")
log.info(f"EDA database: {eda_config['target']}")
assert f"md:{config['database']}" != eda_config["target"]
con = ibis.connect(f"duckdb://md:{config['database']}")
eda_con = ibis.connect(f"duckdb://{eda_config['target']}")

# overwrite tables
for t in eda_con.list_tables():
    if t not in exclude_tables:
        log.info(f"Copying {t}...")
        try:
            con.create_table(t, eda_con.table(t).to_pyarrow(), overwrite=True)
        except Exception as e:
            log.warning(f"Failed to copy {t}...")
            log.warning(e)
