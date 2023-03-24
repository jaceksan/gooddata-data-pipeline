# PoC - integrate analytics into VR/AR/MR

The [A-FRAME](https://aframe.io/) framework is utilized here.

The goal is to provide data visualizations, ideally in an interactive manner, meaning users can create new visualizations with a drag&drop-like experience.

[Here](https://www.youtube.com/watch?v=tpbDEQ6SNek&ab_channel=LarsJuhlJensen) is an example of data visualization, utilizing the A-FRAME framework.

Generally, the app is delivered consistently with the data pipeline. 
For instance, you can update the model and related insight used in the VR app, and update VR app accordingly, in the same commit.
The release is fully consistent.

End users with VR headsets simply open a browser, go to the [target site](https://vr-analytics.onrender.com/) and play with the demo.

## Static examples
Stored in [static_examples](static_examples) folder, index.html is the crossroad.

## UI.SDK
Simply run:
```shell
# Example: local docker-compose environment
export GOODDATA_HOST="http://localhost:3000"
export GOODDATA_TOKEN="YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"
export GOODDATA_WORKSPACE="faa_development"

# Install dependencies
yarn install

# Start the app on localhost:8443
yarn start
```
You can connect the app with any (publicly available) GoodData cloud environment, we provide [GoodData trial](https://www.gooddata.com/trial/),
just modify the export commands above accordingly.

## Deploy to cloud

Deployment to [render.com](render.com) cloud is triggered by merge to this public Git repository:
- `STAGING` from `main` branch: https://streamlit-gooddata-stg.onrender.com/
- `PROD` from `prod` branch: https://streamlit-gooddata.onrender.com/

render.com also provides a feature called `PR previews`. This would be benefitial for deploying DEV app from PRs.
Unfortunately, it does not seem to work properly, not sure if it is caused by free tier is used.
