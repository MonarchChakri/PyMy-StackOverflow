#!/bin/bash

POD_INSTANCE_NAME=`oc get pods \
  -l "name=${POD_NAME:-django-frontend}" \
  -t "{{ with index .items ${POD_INDEX:-0} }}{{ .metadata.name }}{{ end }}"`

oc exec -p "$POD_INSTANCE_NAME" -it -- bash -c "${@:-echo}"
