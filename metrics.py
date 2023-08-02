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
st.set_page_config(layout="wide")

## ibis config
con = ibis.connect(f"duckdb://{config['database']}", read_only=True)

# us tables
packages = con.table("packages")
deps = con.table("deps")
wheels = con.table("wheels")
maintainers = con.table("maintainers")
package_urls = con.table("package_urls")
scorecard_checks = con.table("scorecard_checks")

top_maintainers_by_downloads = (
    maintainers.join(packages, [("package_name", "name")])
    .group_by("name")
    .aggregate(ibis._["downloads"].sum().name("downloads"))
    .select("name", "downloads")
    .order_by(ibis.desc("downloads"))
    .limit(1000)
)
# display metrics
"""
# PyPI metrics
"""
# variables
with st.form(key="metrics"):
    package_name = st.text_input(
        "package",
        value="ibis-framework",
    )
    maintainer = st.text_input(
        "maintainer",
        value=top_maintainers_by_downloads["name"].topk(1)["name"].to_pandas()[0],
    )
    update_button = st.form_submit_button(label="update")


# top-level metrics
total_packages = packages.select("name").nunique().to_pandas()
st.metric("total_packages", f"{total_packages:,}")

"""
## release days

where 0 is Sunday
"""
release_days = (
    packages.dropna("last_uploaded_at")
    .group_by(ibis._["last_uploaded_at"].day_of_week.index().name("day"))
    .agg(ibis._.count().name("count"))
)

c0 = px.bar(
    release_days,
    x="day",
    y="count",
    color="day",
)
st.plotly_chart(c0, use_container_width=True)

"""
## top packages by downloads (top 1000)
"""
top_packages_by_downloads = (
    packages.group_by("name")
    .aggregate(ibis._["downloads"].sum().name("downloads"))
    .select("name", "downloads")
    .order_by(ibis.desc("downloads"))
    .limit(1000)
)
st.dataframe(top_packages_by_downloads, use_container_width=True)

"""
## top maintainers by downloads (top 1000)
"""
st.dataframe(top_maintainers_by_downloads, use_container_width=True)

f"""
## dependents of {package_name} 
"""
dependents = (
    deps.filter(ibis._["dep_name"] == package_name).select("package_name").distinct()
)
st.dataframe(dependents, use_container_width=True)

f"""
## packages maintained by {maintainer}
"""
maintained_packages = (
    maintainers.filter(ibis._["name"] == maintainer)
    .join(packages, [("package_name", "name")])
    .select("package_name")
    .distinct()
)
st.dataframe(maintained_packages, use_container_width=True)
