#!/usr/bin/env sh

aws --profile minio --endpoint-url http://${MINIO_ENDPOINT} s3 sync ${PATH_GENERATED_DATA}/$1 s3://${S3_BUCKET_NAME}/${PATH_IN_BUCKET}/$1
