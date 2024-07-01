#!/usr/bin/env sh

aws s3 sync --acl public-read generated_data/$1 s3://gdc-tiger-test-data/real_time/$1