for VAR in API_KEY APP_ID APP_NAME MANIFEST_FILE
do
    if [[ -z ${!VAR+x} ]]; then
        echo "env variable" $VAR "missing"
        exit 1
    fi
done

cp $MANIFEST_FILE manifest.json

rsconnect deploy manifest \
    --server https://rsc.ds.umcutrecht.nl/ \
    --api-key $API_KEY \
    --app-id $APP_ID \
    --title "$APP_NAME" \
    manifest.json

rm manifest.json
