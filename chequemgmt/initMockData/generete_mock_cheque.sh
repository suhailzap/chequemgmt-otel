#!/bin/bash

RETRY_INTERVAL=5

while true; do
  chequeNo=$(head -c 64 /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 10)
  approvalGranted=$(shuf -e true false -n 1)

  http_code=$(curl -s -o /tmp/resp.json -w "%{http_code}" \
    -X POST "http://localhost:8085/cheques/add" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "chequeNo=${chequeNo}&approvalGranted=${approvalGranted}")

  if [ "$http_code" -eq 200 ]; then
    echo "SUCCESS: Cheque ${chequeNo} inserted"
  else
    echo "FAILURE: HTTP $http_code"
    cat /tmp/resp.json
  fi

  sleep $RETRY_INTERVAL
done
