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
        value="jcrist",
    )
    update_button = st.form_submit_button(label="update")


# top-level metrics
total_packages = packages.select("name").nunique().to_pandas()
max_last_uploaded_at = (
    packages["last_uploaded_at"].max().to_pandas().strftime("%m/%d/%Y")
)
minimum_downloads = packages.filter(ibis._["downloads"] > 0).downloads.min().to_pandas()
max_downloads = packages.downloads.max().to_pandas()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("latest data", max_last_uploaded_at)
with col2:
    st.metric("total packages", f"{total_packages:,}")
with col3:
    st.metric("min (>0) downloads", f"{minimum_downloads:,}")
with col4:
    st.metric("max downloads", f"{max_downloads:,}")

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
top_maintainers_by_downloads = (
    maintainers.join(packages, [("package_name", "name")])
    .group_by("name")
    .aggregate(ibis._.downloads.sum().name("downloads"))
    .select("name", "downloads")
    .order_by(ibis._["downloads"].desc())
    .limit(1000)
)
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

f"""
## packages used by test* extras (top 1000)
"""
top_test_deps = (
    deps.filter(ibis._.extra.startswith("test"))
    .group_by("dep_name")
    .agg(ibis._.count().name("count"))
    .order_by(ibis._["count"].desc())
    .limit(1000)
)
st.dataframe(top_test_deps, use_container_width=True)

f"""
## top pytest extensions (top 1000)
"""
top_pytest_extensions = (
    deps.filter(ibis._.dep_name.startswith("pytest-"))
    .select("package_name", "dep_name")
    .distinct()
    .group_by("dep_name")
    .agg(ibis._.count().name("count"))
    .order_by(ibis._["count"].desc())
    .limit(1000)
)
st.dataframe(top_pytest_extensions, use_container_width=True)

f"""
## most depended on packages (top 1000)
"""
most_dependents = (
    deps.select("package_name", "dep_name")
    .distinct()
    .group_by("dep_name")
    .agg(ibis._.count().name("dep_count"))
    .order_by(ibis._["dep_count"].desc())
    .limit(1000)
)
st.dataframe(most_dependents, use_container_width=True)

f"""
## maintainer count
"""

maintainer_counts = (
    maintainers.group_by("package_name")
    .agg(ibis._.count().name("maintainers"))
    .group_by("maintainers")
    .agg(ibis._.count().name("count"))
)
c1 = px.bar(
    maintainer_counts,
    x="maintainers",
    y="count",
    color="maintainers",
    log_y=True,
)
st.plotly_chart(c1, use_container_width=True)

f"""
## top package prefixes (top 1000)
"""
common_prefixes = (
    maintainers.group_by("package_name")
    .agg(ibis._.count().name("maintainers"))
    .filter(ibis._.maintainers == 12)
    .mutate(ibis._["package_name"].re_extract(r"^(\w*)-?", 1).name("prefix"))
    .order_by(ibis._["prefix"].desc())
    .limit(1000)
)
st.dataframe(common_prefixes, use_container_width=True)

f"""
## find "clubs"
"""

# These prefixes are all "zope" related, and are so prolific that they mask anything interesting.
# Zope used to be really popular, but downloads have waned. We'll ignore them for now since they
# mask anything else interesting.
ignore_prefixes = ["zope", "zc", "z3c", "collective", "plone", "products"]

clubs = (
    maintainers.group_by("package_name")
    .agg(ibis._.count().name("maintainers"))
    .join(
        packages.filter(
            [
                ibis._["downloads"] == 0,
                ibis._["last_uploaded_at"] > (datetime.now() - timedelta(days=365)),
                *(~ibis._["name"].startswith(p) for p in ignore_prefixes),
            ]
        ),
        [("package_name", "name")],
    )
    .order_by(ibis._["maintainers"].desc())
    .select("package_name", "maintainers", "downloads")
    .limit(1000)
)
st.dataframe(clubs, use_container_width=True)


f"""
## top packages with one maintainer (top 1000)
"""

bus_factor_1 = (
    maintainers.group_by("package_name")
    .agg(ibis._.count().name("maintainer_count"))
    .filter(ibis._["maintainer_count"] == 1)
    .join(maintainers, "package_name")
    .join(
        (
            deps.select("package_name", "dep_name")
            .distinct()
            .group_by("dep_name")
            .agg(ibis._.count().name("dep_count"))
        ),
        [("package_name", "dep_name")],
    )
    .select("package_name", "name", "dep_count")
    .relabel({"name": "maintainer"})
    .order_by(ibis._["dep_count"].desc())
    .limit(1000)
)
st.dataframe(bus_factor_1, use_container_width=True)

f"""
## most distinct collaborators
"""

most_collaborators = (
    maintainers.join(maintainers, "package_name")
    .select("name", "name_right")
    .filter(ibis._["name"] != ibis._["name_right"])
    .distinct()
    .group_by("name")
    .agg(ibis._.count().name("n_collaborators"))
    .order_by(ibis.desc("n_collaborators"))
    .limit(1000)
)
st.dataframe(most_collaborators, use_container_width=True)

f"""
## most popular transitive dependencies
"""

transitive_deps = con.sql(
    """
    WITH RECURSIVE
    direct_deps(package, dependency) AS (
      SELECT
        package_name,
        dep_name
      FROM deps
      WHERE
        extra IS NULL
    ),
    transitive_deps(package, intermediate, dependency) AS (
      SELECT
        package,
        package,
        dependency
      FROM direct_deps
      UNION
      SELECT
        transitive_deps.package,
        direct_deps.package,
        direct_deps.dependency
      FROM direct_deps
      JOIN transitive_deps
        ON direct_deps.package = transitive_deps.dependency
    )
    SELECT package, dependency FROM transitive_deps
    """,
    schema={"package": "string", "dependency": "string"},
    dialect="sqlite",
)
top_transitive_deps = (
    transitive_deps
    .group_by("dependency")
    .agg(ibis._["package"].nunique().name("n_dependents"))
    .order_by(ibis._["n_dependents"].desc())
    .limit(1000)
)
st.dataframe(top_transitive_deps, use_container_width=True)
