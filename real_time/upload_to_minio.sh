#!/usr/bin/env sh

aws --profile minio --endpoint-url http://localhost:19000 s3 sync generated_data/$1 s3://gdc-tiger-test-data/real_time/$1
