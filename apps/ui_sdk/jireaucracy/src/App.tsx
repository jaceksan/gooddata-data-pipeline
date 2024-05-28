// (C) 2019-2024 GoodData Corporation
import React from "react";
import { BackendProvider, WorkspaceProvider } from "@gooddata/sdk-ui";
import { InsightView } from "@gooddata/sdk-ui-ext";
import { Dashboard } from "@gooddata/sdk-ui-dashboard";
import { Execute } from "@gooddata/sdk-ui";
import CustomVisualization from "./CustomVisualization.js";

import { backend } from "./backend.js";
import * as Md from "./catalog.js";
import * as MdFAA from "./catalog_faa.js";
import img from "./assets/gooddata-logo.svg";

// Workspace ID is injected by WebPack based on the value in package.json
const workspaceIdCICD = WORKSPACE_ID_CICD;
const workspaceIdFAA = WORKSPACE_ID_FAA;

export const App: React.FC = () => {
    return (
        <BackendProvider backend={backend}>
            <WorkspaceProvider workspace={workspaceIdCICD}>
                <div className="app">
                    <h1 className="app-title">GoodData UI SDK demo</h1>
                    <p className="app-paragraph">
                        Edit <code className="app-code">/src/App.tsx</code> to get started. Learn
                        more about this template in <code className="app-code">README.md</code>.
                    </p>
                    <pre className="app-preformatted">
                        <code className="app-code">
                            &lt;Dashboard dashboard=&#123;Md.Dashboards.Jireaucracy&#125; /&gt;
                        </code>
                    </pre>
                    <figure className="app-figure">
                        <Dashboard dashboard={Md.Dashboards.Jireaucracy} showTitle/>
                    </figure>
                    <pre className="app-preformatted">
                        <code className="app-code">
                            &lt;InsightView insight=&#123;Md.Insights.CreatedCommitsMonth&#125; /&gt;
                        </code>
                    </pre>
                    <figure className="app-figure">
                        <InsightView insight={Md.Insights.MissedDueDateInHistory} showTitle/>
                    </figure>
                </div>
            </WorkspaceProvider>
            <WorkspaceProvider workspace={workspaceIdFAA}>
                <div className="app">
                    <figure className="app-figure">
                        <Execute seriesBy={[MdFAA.FlightCount]} slicesBy={[MdFAA.FaaRegionOrigin, MdFAA.FaaRegionDestination]}>
                        {/* <Execute seriesBy={[MdFAA.FlightCount]} slicesBy={[MdFAA.Manufacturer, MdFAA.Nickname]}> */}
                            {CustomVisualization}
                        </Execute>
                    </figure>
                    <footer className="app-footer">
                        <img src={img} alt=""/>
                        <a
                            className="app-link"
                            target="_blank"
                            rel="noreferrer"
                            href="https://sdk.gooddata.com/gooddata-ui/docs/about_gooddataui.html"
                        >
                            GoodData.UI docs
                        </a>
                    </footer>
                </div>
            </WorkspaceProvider>
        </BackendProvider>
    );
};
