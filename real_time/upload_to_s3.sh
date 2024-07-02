#!/usr/bin/env sh

aws s3 sync --acl public-read generated_data/$1 s3://gdc-jacek-test-redshift/real_time/$1