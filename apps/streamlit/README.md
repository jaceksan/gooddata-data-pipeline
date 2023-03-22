# Build Streamlit app on top of GoodData 

Demonstrate GoodData headless BI approach allowing easy integration of any client app.

For Streamlit case, GoodData provides [Python SDK](https://www.gooddata.com/developers/cloud-native/doc/cloud/api-and-sdk/python-sdk/).

## Demo purpose

This demo app provides self-service analytics to even non-technical users.

Users can select facts/attributes/metrics in the left panel and a corresponding report(insight, visualization) is rendered in the right panel(canvas).

The following visualization types are supported:
- Table
- Line chart
- Bar chart
- Donut chart

Additionally, users can:
- Set analytical functions applied on selected facts (SUM, AVG, ...)
- Set filters (now only simple attribute filters, but would be easy to add e.g. date filters)
- Set sorting by multiple result "columns"

## How to run locally
```shell
source .env.local
# --debug provides more messages printed to the console from which you execute this statement
cd apps/streamlit
streamlit run app.py -- --debug
```

The app relies on GoodData instance. Check [top-level README](../../README.md) for how to start GoodData locally from docker-compose.

## Deploy to cloud

Deployment to [render.com](render.com) cloud is triggered by merge to this public Git repository.
