#!/bin/bash

RETRY_INTERVAL=60

while true; do
  echo "Sending mock data to backend"

  chequeNo=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
  approvalGranted=$(shuf -e true false -n 1)  # Randomly pick true or false

  response=$(curl -X POST "http://localhost:8085/cheques/add" \
    -d "chequeNo=${chequeNo}&approvalGranted=${approvalGranted}" \
    --write-out "%{http_code}" --silent --output /dev/null)

  if [ "$response" -eq 200 ]; then
    echo "Success! Cheque ${chequeNo} added."
    sleep $RETRY_INTERVAL
  else
    echo "Failed (HTTP $response)! Retrying in $RETRY_INTERVAL seconds..."
  fi
done