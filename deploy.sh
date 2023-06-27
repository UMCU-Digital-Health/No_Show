#!/bin/bash
if [ -f .env ]; then
  export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi

for VAR in RSC_KEY
do
    if [[ -z ${!VAR+x} ]]; then
        echo "env variable" $VAR "missing"
        exit 1
    fi
done

# Create clean temp copy of repo from which to upload to RStudio Connect
rm -rf test_env_rsconnect
mkdir test_env_rsconnect
mkdir -p test_env_rsconnect/data/raw/
for VAR in src run output requirements.txt setup.cfg pyproject.toml data/raw/NL.txt
do
    cp -R $VAR test_env_rsconnect/$VAR
done

cd test_env_rsconnect


rsconnect deploy fastapi \
    --server https://rsc.ds.umcutrecht.nl/ \
    --insecure \
    --exclude "**/__pycache__/*" \
    --entrypoint run.app:app \
    --app-id $TEST_ENDPOINT \
    .
    

# Update manifest file
rsconnect write-manifest api \
    --exclude "**/__pycache__/*" \
    --entrypoint run.app:app \
    --overwrite \
    .

cd ..

#pytest --deploy tests/api/ | tee tests.log

#status=${PIPESTATUS[0]} # status of run_tests.py
#if [ $status -ne 0 ]; then
#    echo 'ERROR: pytest failed, exiting ...'
#    exit $status
#fi

rm -rf production_env_rsconnect
mkdir production_env_rsconnect
mkdir -p production_env_rsconnect/data/raw/
for VAR in src run output requirements.txt setup.cfg pyproject.toml data/raw/NL.txt
do
    cp -R $VAR production_env_rsconnect/$VAR
done

cd production_env_rsconnect

rsconnect deploy fastapi \
    --server https://rsc.ds.umcutrecht.nl/ \
    --insecure \
    --exclude "**/__pycache__/*" \
    --entrypoint run.app:app \
    --app-id $PRODUCTION_ENDPOINT \
    .

# Update manifest file
rsconnect write-manifest api \
    --exclude "**/__pycache__/*" \
    --entrypoint run.app:app \
    --overwrite \
    .