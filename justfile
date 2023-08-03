# Justfile

# load environment variables
set dotenv-load

# aliases

# list justfile recipes
default:
    just --list

setup:
    pip install -r requirements.txt

# run
run:
    @time python eda.py run

# export data
export:
    @time python export_md.py

# app
app:
    streamlit run metrics.py

# download source data
download:
    gh release download --clobber -R sethmlarson/pypi-data -p 'pypi.db.gz' -O pypi.db.gz
    gunzip pypi.db.gz -f

# cleanup data
clean:
    -rm *.ddb* || true
