from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html
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

        frames.append(
            pink_morsel[["Sales", "Date", "region"]].rename(columns={"region": "Region"})
        )

    if not frames:
        raise FileNotFoundError("No Pink Morsel sales data was found in the data folder.")

    combined = pd.concat(frames, ignore_index=True).dropna(subset=["Date", "Sales"])
    daily_sales = combined.groupby("Date", as_index=False)["Sales"].sum()
    return daily_sales.sort_values("Date").reset_index(drop=True)


sales_df = load_sales_data()
increase_date = pd.Timestamp("2021-01-15")

before_sales = sales_df[sales_df["Date"] < increase_date]["Sales"]
after_sales = sales_df[sales_df["Date"] >= increase_date]["Sales"]

before_avg = before_sales.mean()
after_avg = after_sales.mean()
comparison = "before" if before_avg > after_avg else "after"

app = Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=sales_df["Date"],
        y=sales_df["Sales"],
        mode="lines+markers",
        name="Daily sales",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=7),
    )
)
fig.add_vline(
    x=increase_date,
    line_dash="dash",
    line_color="#d62728",
    annotation_text="Price increase",
    annotation_position="top left",
)
fig.update_layout(
    title="Pink Morsel Sales Over Time",
    xaxis_title="Date",
    yaxis_title="Sales ($)",
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=40, r=20, t=60, b=40),
)
fig.update_xaxes(title_text="Date")
fig.update_yaxes(title_text="Sales ($)")

app.layout = html.Div(
    style={"padding": "24px", "fontFamily": "Arial, sans-serif"},
    children=[
        html.H1("Soul Foods Pink Morsel Sales Visualiser", style={"marginBottom": "8px"}),
        html.P(
            "This chart shows daily Pink Morsel sales and marks the 15 January 2021 price increase.",
            style={"marginBottom": "16px", "color": "#555"},
        ),
        html.Div(
            style={
                "padding": "12px 16px",
                "backgroundColor": "#f5f7fa",
                "borderRadius": "8px",
                "marginBottom": "16px",
            },
            children=[
                html.Strong("Answer:"),
                html.Span(
                    f" Average daily sales were ${before_avg:,.2f} before the increase and "
                    f"${after_avg:,.2f} after it, so sales were higher {comparison} the price increase."
                ),
            ],
        ),
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
    ],
)


if __name__ == "__main__":
    app.run(debug=True)
