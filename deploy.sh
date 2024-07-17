for VAR in API_KEY ADMIN_DASH_ID ADMIN_DASH_NAME ADMIN_DASH_MANIFEST_FILE DASH_ID DASH_NAME DASH_TEST_ID DASH_TEST_NAME DASH_MANIFEST_FILE API_ID API_NAME API_TEST_ID API_TEST_NAME API_MANIFEST_FILE 
do
    if [[ -z ${!VAR+x} ]]; then
        echo "env variable" $VAR "missing"
        exit 1
    fi
done

read -p "What do you want to deploy? Options: 'admin-dash'/1 ; 'calling-dash'/2 ; 'calling-dash-test'/3 ; 'api'/4 ; 'api-test'/5 " APPLICATION
APPLICATION=${APPLICATION:-N}

if [[ $APPLICATION == 'admin-dash' || $APPLICATION == "1" ]]; then
    echo "Deploying Admin dashboard"
    cp $ADMIN_DASH_MANIFEST_FILE manifest.json
    APP_ID=$ADMIN_DASH_ID
    APP_NAME=$ADMIN_DASH_NAME
elif [[ $APPLICATION == 'calling-dash' || $APPLICATION == "2" ]]; then
    echo "Deploying Calling dashboard production"
    cp $DASH_MANIFEST_FILE manifest.json
    APP_ID=$DASH_ID
    APP_NAME=$DASH_NAME
elif [[ $APPLICATION == 'calling-dash-test' || $APPLICATION == "3" ]]; then
    echo "Deploying Calling dashboard test"
    cp $DASH_MANIFEST_FILE manifest.json
    APP_ID=$DASH_TEST_ID
    APP_NAME=$DASH_TEST_NAME
elif [[ $APPLICATION == 'api' || $APPLICATION == "4" ]]; then
    echo "Deploying API production"
    cp $API_MANIFEST_FILE manifest.json
    APP_ID=$API_ID
    APP_NAME=$API_NAME
elif [[ $APPLICATION == 'api-test' || $APPLICATION == "5" ]]; then
    echo "Deploying API test"
    cp $API_MANIFEST_FILE manifest.json
    APP_ID=$API_TEST_ID
    APP_NAME=$API_TEST_NAME
else
    echo "Invalid option"
    return
fi

rsconnect deploy manifest \
    --server https://rsc.ds.umcutrecht.nl/ \
    --api-key $API_KEY \
    --app-id $APP_ID \
    --title "$APP_NAME" \
    manifest.json

rm manifest.json
