#!/bin/sh

gcloud auth activate-service-account $GCLOUD_EMAIL_SERVICE_ACCOUNT --key-file /keys/$GCLOUD_KEY_FILE
gcloud config set project $GCLOUD_PROJECT 

if [ "$1" = 'start' ]; then
    exec python gce-cluster-control.py -g $CLOUDCONTROL_INSTANCE_GROUP_NAME -n $CLOUDCONTROL_INSTANCE_GROUP_SIZE -z $GCLOUD_ZONE -s /status 
fi

if [ "$1" = 'stop' ]; then
    exec python gce-cluster-control.py -g $CLOUDCONTROL_INSTANCE_GROUP_NAME -n 0 -z $GCLOUD_ZONE -s /status 
fi
exec "$@"