# PoC - integrate analytics into VR/AR/MR

The [A-FRAME](https://aframe.io/) framework is utilized here.

The goal is to provide data visualizations, ideally in an interactive manner, meaning users can create new visualizations with a drag&drop-like experience.

[Here](https://www.youtube.com/watch?v=tpbDEQ6SNek&ab_channel=LarsJuhlJensen) is an example of data visualization, utilizing the A-FRAME framework.

The repository is linked with [render.com](render.com) provider. 

Any merge into the `main` branch triggers the delivery process to staging app.
The app is connected to staging environment of the CICD data pipeline demo stored in this repository 

Any merge into the `prod` branch triggers the delivery process to production app.

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

You can test the app in web browser. Then, you can connect your VR headset to your laptop (internal network),
or you can deploy the app e.g. in [render.com](render.com) like service and make it publicly available.
