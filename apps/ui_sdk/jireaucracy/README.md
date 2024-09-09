# GoodData React SDK Example app

This project contains a sample setup for a React app using [GoodData React SDK](https://github.com/gooddata/gooddata-ui-sdk).
It was bootstrapped with [@gooddata/app-toolkit](https://www.gooddata.com/docs/gooddata-ui/latest/quick_start/).

## Preparation
Run `yarn install` to install all dependencies.

## Application
It's configured to connect to the GoodData organization populated by the data pipeline from this repository.
You have to create a `.env` file in the root of the project with the following content:
```shell
# For GoodData Cloud or GoodData.CN
TIGER_API_TOKEN=<token>
```

Then run `npm start` to start the application.
