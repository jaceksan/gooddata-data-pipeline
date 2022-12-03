import json
from typing import Optional
import attrs

from dbt_gooddata.dbt.base import Base
from dbt_gooddata.dbt.tables import DbtModelBase
# TODO - add CatalogDeclarativeMetric to gooddata_sdk.__init__.py
from gooddata_sdk.catalog.workspace.declarative_model.workspace.analytics_model.analytics_model import (
    CatalogDeclarativeMetric
)


SUPPORTED_DBT_CALCULATION_METHODS = {
    "count_distinct": "COUNT",
    "sum": "SUM",
    "average": "AVG",
    "min": "MIN",
    "max": "MAX",
}


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataMetricProps(Base):
    model_id: Optional[str] = None
    format: Optional[str] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataMetric(Base):
    gooddata: Optional[DbtModelMetaGoodDataMetricProps] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetric(DbtModelBase):
    label: str
    meta: DbtModelMetaGoodDataMetric
    calculation_method: str
    expression: str


class DbtModelMetrics:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        with open("target/manifest.json") as fp:
            self.dbt_catalog = json.load(fp)

    @property
    def metrics(self) -> list[DbtModelMetric]:
        result = []
        for metric_name, metric_def in self.dbt_catalog["metrics"].items():
            result.append(DbtModelMetric.from_dict(metric_def))
        # Return only gooddata labelled tables marked by model_id (if requested in args)
        return [
            r for r in result
            if r.meta.gooddata is not None and (not self.model_id or r.meta.gooddata.model_id == self.model_id)
        ]

    def make_gooddata_metrics(self):
        gd_metrics = []
        for dbt_metric in self.metrics:
            s = SUPPORTED_DBT_CALCULATION_METHODS
            # TODO - duplicate column name in 2+ tables.
            #  Expression would have to be parsed and each column would have to be translated to LDM ID
            calculation_method = SUPPORTED_DBT_CALCULATION_METHODS.get(dbt_metric.calculation_method)
            # TODO - filters
            if calculation_method:
                # This is nasty hack. expression can contain multiple objects
                if calculation_method == "COUNT":
                    object_id = "{label/" + dbt_metric.expression + "}"
                else:
                    object_id = "{fact/" + dbt_metric.expression + "}"
                gd_maql = f"SELECT {s[dbt_metric.calculation_method]}({object_id})"
                metric_dict = {
                    "id": dbt_metric.name,
                    "title": dbt_metric.label,
                    "description": dbt_metric.description,
                    "content": {
                        "format": dbt_metric.meta.gooddata.format,
                        "maql": gd_maql,
                    },
                    "tags": dbt_metric.tags
                }
                gd_metrics.append(CatalogDeclarativeMetric.from_dict(metric_dict))
            else:
                raise Exception(f"Unsupported calculation method: {dbt_metric.calculation_method}")
        return gd_metrics
