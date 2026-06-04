"""Chart generation using Plotly."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import CHART_COLORS, MAX_CHART_ROWS


class ChartService:
    def __init__(self):
        self.template = "plotly_dark"
        self.colors   = CHART_COLORS

    def build(self, df: pd.DataFrame, config: dict) -> go.Figure | None:
        if df.empty or not config:
            return None
        df = df.head(MAX_CHART_ROWS)
        chart_type = config.get("chart_type", "bar")
        x     = config.get("x")
        y     = config.get("y")
        color = config.get("color")
        title = config.get("title", "Chart")

        # Validate columns exist
        valid_x = x if x and x in df.columns else None
        valid_y = y if y and y in df.columns else None
        valid_c = color if color and color in df.columns else None

        try:
            fig = None
            if chart_type == "bar":
                fig = px.bar(df, x=valid_x, y=valid_y, color=valid_c, title=title,
                             color_discrete_sequence=self.colors, template=self.template)
            elif chart_type == "line":
                fig = px.line(df, x=valid_x, y=valid_y, color=valid_c, title=title,
                              color_discrete_sequence=self.colors, template=self.template)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=valid_x, y=valid_y, color=valid_c, title=title,
                                 color_discrete_sequence=self.colors, template=self.template)
            elif chart_type == "pie":
                val_col = valid_y or (df.select_dtypes(include="number").columns[0] if len(df.select_dtypes(include="number").columns) > 0 else None)
                name_col = valid_x or df.columns[0]
                if val_col:
                    fig = px.pie(df, names=name_col, values=val_col, title=title,
                                 color_discrete_sequence=self.colors, template=self.template)
            elif chart_type == "histogram":
                col = valid_x or valid_y or df.select_dtypes(include="number").columns[0]
                fig = px.histogram(df, x=col, color=valid_c, title=title,
                                   color_discrete_sequence=self.colors, template=self.template)
            elif chart_type == "treemap":
                path_col = [valid_x] if valid_x else [df.columns[0]]
                val_col  = valid_y or df.select_dtypes(include="number").columns[0]
                fig = px.treemap(df, path=path_col, values=val_col, title=title,
                                 color_discrete_sequence=self.colors, template=self.template)
            elif chart_type == "box":
                fig = px.box(df, x=valid_x, y=valid_y, color=valid_c, title=title,
                             color_discrete_sequence=self.colors, template=self.template)

            if fig:
                fig = self._style(fig)
            return fig
        except Exception:
            return None

    def _style(self, fig: go.Figure) -> go.Figure:
        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#0a0e1a",
            font=dict(family="IBM Plex Mono", color="#e2e8f0", size=12),
            title_font=dict(size=15, color="#00d4ff"),
            legend=dict(bgcolor="#111827", bordercolor="#1e293b"),
            margin=dict(l=40, r=20, t=50, b=40),
            xaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
        )
        return fig

    # ── Quick charts for dashboard ──────────────────────────────────────────
    def quick_bar(self, df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure | None:
        return self.build(df, {"chart_type": "bar", "x": x, "y": y, "title": title})

    def quick_line(self, df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure | None:
        return self.build(df, {"chart_type": "line", "x": x, "y": y, "title": title})

    def quick_pie(self, df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure | None:
        return self.build(df, {"chart_type": "pie", "x": names, "y": values, "title": title})
