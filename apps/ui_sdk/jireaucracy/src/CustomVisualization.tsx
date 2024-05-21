// (C) 2021 GoodData Corporation
import React from "react";
import Highcharts from "highcharts";
import HighchartSankey from "highcharts/modules/sankey";
import HighchartsWheel from "highcharts/modules/dependency-wheel";
import HighchartsReact from "highcharts-react-official";
import * as MdFAA from "./catalog_faa.js";

HighchartSankey(Highcharts);
HighchartsWheel(Highcharts);

export default ({ error, isLoading, result }) => {
    if (isLoading) {
        return <span>Loading…</span>;
    }

    if (error) {
        return <span>Something went wrong :-(</span>;
    }

    if (result) {
        const data = result
            .data()
            .series()
            .firstForMeasure(MdFAA.FlightCount)
            .dataPoints()
            .map((dataPoint) => ({
                from: dataPoint.sliceDesc.headers[0].attributeHeaderItem.name,
                to: dataPoint.sliceDesc.headers[1].attributeHeaderItem.name,
                weight: parseFloat(dataPoint.rawValue)
            }));

        return (
            <HighchartsReact
                highcharts={Highcharts}
                options={{
                    chart: {
                        type: "dependencywheel"
                    },
                    title: {
                        text: "🎉 Custom Chart Built with Highcharts 🎉"
                    },
                    series: [
                        {
                            data
                        }
                    ]
                }}
            />
        );
    }

    return <span>Init…</span>;
};
