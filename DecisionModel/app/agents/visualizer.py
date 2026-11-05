from __future__ import annotations

import pandas as pd

from app.agents.base import BaseAgent


class VisualizerAgent(BaseAgent):
    name = "visualizer"

    def run(self, dataframe: pd.DataFrame, question: str, chart_type: str = "bar") -> dict:
        if dataframe.empty:
            return {"type": "table", "data": [], "layout": {"title": "No data"}}

        keys = list(dataframe.columns)
        x_axis = keys[0]
        y_axis = keys[1] if len(keys) > 1 else keys[0]

        if chart_type == "line":
            spec = {
                "type": "line",
                "data": [
                    {
                        "x": dataframe[x_axis].tolist(),
                        "y": dataframe[y_axis].tolist(),
                        "mode": "lines+markers",
                        "type": "scatter",
                    }
                ],
                "layout": {
                    "title": question,
                    "xaxis": {"title": str(x_axis)},
                    "yaxis": {"title": str(y_axis)},
                    "template": "plotly_white",
                },
            }
        elif chart_type == "pie":
            spec = {
                "type": "pie",
                "data": [
                    {"labels": dataframe[x_axis].tolist(), "values": dataframe[y_axis].tolist(), "type": "pie"}
                ],
                "layout": {"title": question, "template": "plotly_white"},
            }
        else:
            spec = {
                "type": "bar",
                "data": [
                    {"x": dataframe[x_axis].tolist(), "y": dataframe[y_axis].tolist(), "type": "bar"}
                ],
                "layout": {
                    "title": question,
                    "xaxis": {"title": str(x_axis)},
                    "yaxis": {"title": str(y_axis)},
                    "template": "plotly_white",
                },
            }

        return spec
