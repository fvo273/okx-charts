import constants as c
import plotly.graph_objects as go


def plot_pnl(df, show_pnl=True, show_clean_pnl=True, show_balance_change=True):
    fig = go.Figure()

    if show_pnl:
        fig.add_trace(
            go.Scatter(
                x=df[c.DATE],
                y=df[c.TRADER_PNL] * 100,
                mode="lines",
                name=c.TRADER_PNL,
                line=c.AUX_LINE_STYLE,
            )
        )

    if show_clean_pnl:
        fig.add_trace(
            go.Scatter(
                x=df[c.DATE],
                y=df[c.CLIENT_PNL] * 100,
                mode="lines",
                name=c.CLIENT_PNL,
                line=c.MAIN_LINE_STYLE,
            )
        )

    if show_balance_change:
        fig.add_trace(
            go.Scatter(
                x=df[c.DATE],
                y=df[c.AVAILABLE_BALANCE] * 100,
                mode="lines",
                name=c.AVAILABLE_BALANCE,
                line=c.DASH_LINE_STYLE,
            )
        )

    fig.update_layout(
        title="Relative PNL",
        xaxis_title=c.DATE,
        yaxis_title="%",
        legend_title="",
        xaxis={"showgrid": True, "gridwidth": 1, "gridcolor": "lightgray"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": "lightgray", "tickformat": ".1f"},
    )
    return fig
