# Justfile

# load environment variables
set dotenv-load

# aliases

# list justfile recipes
default:
    just --list

# run
run:
    @time python eda.py run

# download source data
download:
    gh release download --clobber -R sethmlarson/pypi-data -p 'pypi.db.gz'
    gunzip pypi.db.gz -f

# cleanup data
clean:
    -rm *.ddb* || true
