from pathlib import Path

import pandas as pd
from dash import Dash, Input, Output, dcc, html
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_sales_data() -> pd.DataFrame:
    csv_files = [
        "daily_sales_data_0.csv",
        "daily_sales_data_1.csv",
        "daily_sales_data_2.csv",
    ]

    frames = []
    for filename in csv_files:
        file_path = DATA_DIR / filename
        if not file_path.exists():
            continue

        df = pd.read_csv(file_path)
        pink_morsel = df[df["product"].astype(str).str.lower().str.strip() == "pink morsel"].copy()

        if pink_morsel.empty:
            continue

        pink_morsel["price"] = (
            pink_morsel["price"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        pink_morsel["price"] = pd.to_numeric(pink_morsel["price"], errors="coerce")
        pink_morsel["quantity"] = pd.to_numeric(pink_morsel["quantity"], errors="coerce")
        pink_morsel["Sales"] = pink_morsel["price"] * pink_morsel["quantity"]
        pink_morsel["Date"] = pd.to_datetime(pink_morsel["date"], errors="coerce")
        pink_morsel["Region"] = (
            pink_morsel["region"].astype(str).str.strip().str.lower()
        )

        frames.append(pink_morsel[["Sales", "Date", "Region"]].copy())

    if not frames:
        raise FileNotFoundError("No Pink Morsel sales data was found in the data folder.")

    combined = pd.concat(frames, ignore_index=True).dropna(subset=["Date", "Sales", "Region"])
    return combined.sort_values("Date").reset_index(drop=True)


sales_df = load_sales_data()
increase_date = pd.Timestamp("2021-01-15")
REGION_OPTIONS = ["north", "east", "south", "west", "all"]


def build_daily_sales(selected_region: str) -> pd.DataFrame:
    if selected_region == "all":
        return sales_df.groupby("Date", as_index=False)["Sales"].sum()

    return (
        sales_df.loc[sales_df["Region"] == selected_region]
        .groupby("Date", as_index=False)["Sales"]
        .sum()
    )


def build_figure(selected_region: str) -> go.Figure:
    daily_sales = build_daily_sales(selected_region)
    region_label = "all regions" if selected_region == "all" else f"the {selected_region.title()} region"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_sales["Date"],
            y=daily_sales["Sales"],
            mode="lines+markers",
            name="Daily sales",
            line=dict(color="#4c6ef5", width=3),
            marker=dict(size=7, color="#1c7cd6"),
            hovertemplate="Date: %{x|%b %d, %Y}<br>Sales: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_vline(
        x=increase_date,
        line_dash="dash",
        line_color="#f06595",
        annotation_text="Price increase",
        annotation_position="top left",
    )
    fig.update_layout(
        title=f"Pink Morsel Sales in {region_label.title()}",
        xaxis_title="Date",
        yaxis_title="Sales ($)",
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=40, r=20, t=70, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#23395d"),
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Sales ($)")
    return fig


def build_summary(selected_region: str):
    daily_sales = build_daily_sales(selected_region)
    before_sales = daily_sales[daily_sales["Date"] < increase_date]["Sales"]
    after_sales = daily_sales[daily_sales["Date"] >= increase_date]["Sales"]

    before_avg = before_sales.mean()
    after_avg = after_sales.mean()
    if before_avg > after_avg:
        comparison = "higher before the increase"
    elif after_avg > before_avg:
        comparison = "higher after the increase"
    else:
        comparison = "about the same across both periods"

    return html.Div(
        className="summary-card",
        children=[
            html.H3("Snapshot", style={"margin": "0 0 6px", "fontSize": "1rem"}),
            html.P(
                f"Average daily sales were ${before_avg:,.2f} before the increase and ${after_avg:,.2f} after it, so sales were {comparison}.",
                style={"margin": "0", "lineHeight": "1.5"},
            ),
        ],
    )


app = Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

initial_figure = build_figure("all")
initial_summary = build_summary("all")

app.layout = html.Div(
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "32px",
        "background": "linear-gradient(135deg, #fdf3ea 0%, #eef4ff 100%)",
        "fontFamily": "'Segoe UI', Arial, sans-serif",
        "color": "#23395d",
        "minHeight": "100vh",
    },
    children=[
        html.Div(
            style={
                "background": "rgba(255, 255, 255, 0.92)",
                "borderRadius": "20px",
                "boxShadow": "0 16px 40px rgba(35, 57, 93, 0.12)",
                "padding": "24px 28px",
                "marginBottom": "18px",
                "backdropFilter": "blur(8px)",
            },
            children=[
                html.H1(
                    "Soul Foods Pink Morsel Sales Visualiser",
                    style={"margin": "0 0 8px", "fontSize": "2rem", "color": "#142c4f"},
                ),
                html.P(
                    "Explore how Pink Morsel sales change over time and compare regional performance with one click.",
                    style={"margin": "0", "color": "#5f6f8e", "lineHeight": "1.5"},
                ),
            ],
        ),
        html.Div(
            style={
                "background": "#ffffff",
                "borderRadius": "16px",
                "padding": "18px 20px",
                "boxShadow": "0 10px 24px rgba(35, 57, 93, 0.08)",
                "marginBottom": "16px",
            },
            children=[
                html.Label(
                    "Filter by region",
                    style={
                        "display": "block",
                        "fontWeight": "700",
                        "color": "#314b74",
                        "marginBottom": "10px",
                    },
                ),
                dcc.RadioItems(
                    id="region-radio",
                    options=[
                        {"label": "All regions", "value": "all"},
                        {"label": "North", "value": "north"},
                        {"label": "East", "value": "east"},
                        {"label": "South", "value": "south"},
                        {"label": "West", "value": "west"},
                    ],
                    value="all",
                    inline=True,
                    labelStyle={"display": "inline-flex"},
                ),
            ],
        ),
        html.Div(id="summary-card", children=initial_summary),
        html.Div(
            style={
                "background": "#ffffff",
                "borderRadius": "18px",
                "padding": "16px",
                "boxShadow": "0 12px 28px rgba(35, 57, 93, 0.08)",
            },
            children=[
                dcc.Graph(
                    id="sales-graph",
                    figure=initial_figure,
                    config={"displayModeBar": False},
                )
            ],
        ),
    ],
)


@app.callback(
    Output("sales-graph", "figure"),
    Output("summary-card", "children"),
    Input("region-radio", "value"),
)
def update_visualiser(selected_region: str):
    return build_figure(selected_region), build_summary(selected_region)


if __name__ == "__main__":
    app.run(debug=True)
