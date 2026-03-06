"""
Dog Breeds Dashboard - Interactive Dash application for exploring dog breed data.
"""
import os
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "breeds.csv")
df = pd.read_csv(DATA_PATH)

# Fill NaN for filter columns so dropdowns work
df["bred_for"] = df["bred_for"].fillna("Unknown")
df["breed_group"] = df["breed_group"].fillna("Unknown")
df["country_code"] = df["country_code"].fillna("Unknown")


def parse_metric_to_midpoint(s: str) -> float | None:
    """Parse metric string (e.g. '3.2-4.5' or 'Male: 25-30; Female: 20-25') to midpoint."""
    if pd.isna(s) or not str(s).strip():
        return None
    s = str(s)
    # Extract first X-Y pattern (handles "3.2-4.5" or "Male: 25-30; Female: 20-25")
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", s)
    if match:
        lo, hi = float(match.group(1)), float(match.group(2))
        return (lo + hi) / 2
    return None


app = Dash(__name__, title="Dog Breeds Dashboard")

app.layout = html.Div(
    [
        html.H1("Dog Breeds Dashboard", style={"textAlign": "center", "marginBottom": "0.5rem"}),
        html.P(
            "Explore dog breeds from The Dog API. Search for a specific breed or filter and compare breeds by group, origin, and purpose.",
            style={"textAlign": "center", "color": "#666", "marginBottom": "1.5rem"},
        ),
        dcc.Tabs(
            id="tabs",
            value="search",
            children=[
                dcc.Tab(
                    label="Breed Search",
                    value="search",
                    children=[
                        html.Div(
                            [
                                html.P(
                                    "Search for a dog breed to view its details and image.",
                                    style={"marginBottom": "0.5rem"},
                                ),
                                dcc.Input(
                                    id="breed-search",
                                    type="search",
                                    placeholder="Search breed by name...",
                                    debounce=True,
                                    style={
                                        "width": "100%",
                                        "padding": "0.5rem 1rem",
                                        "fontSize": "1rem",
                                        "borderRadius": "4px",
                                        "border": "1px solid #ccc",
                                    },
                                ),
                                html.Div(id="breed-result", style={"marginTop": "1.5rem"}),
                            ],
                            style={"padding": "1.5rem", "maxWidth": "800px"},
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Explore & Compare",
                    value="explore",
                    children=[
                        html.Div(
                            [
                                html.P(
                                    "Filter breeds by purpose, breed group, or country. Charts update based on your selection.",
                                    style={"marginBottom": "1rem"},
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Label("Bred for", style={"display": "block", "marginBottom": "0.25rem"}),
                                                dcc.Dropdown(
                                                    id="filter-bred-for",
                                                    options=[{"label": "All", "value": "all"}]
                                                    + [
                                                        {"label": v, "value": v}
                                                        for v in sorted(df["bred_for"].dropna().unique())
                                                        if str(v).strip()
                                                    ],
                                                    value="all",
                                                    clearable=False,
                                                    style={"minWidth": "150px"},
                                                ),
                                            ],
                                            style={"flex": "1", "marginRight": "1rem"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Breed group", style={"display": "block", "marginBottom": "0.25rem"}),
                                                dcc.Dropdown(
                                                    id="filter-breed-group",
                                                    options=[{"label": "All", "value": "all"}]
                                                    + [
                                                        {"label": v, "value": v}
                                                        for v in sorted(df["breed_group"].dropna().unique())
                                                        if str(v).strip()
                                                    ],
                                                    value="all",
                                                    clearable=False,
                                                    style={"minWidth": "150px"},
                                                ),
                                            ],
                                            style={"flex": "1", "marginRight": "1rem"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Country", style={"display": "block", "marginBottom": "0.25rem"}),
                                                dcc.Dropdown(
                                                    id="filter-country",
                                                    options=[{"label": "All", "value": "all"}]
                                                    + [
                                                        {"label": v, "value": v}
                                                        for v in sorted(df["country_code"].dropna().unique())
                                                        if str(v).strip() and v != "Unknown"
                                                    ],
                                                    value="all",
                                                    clearable=False,
                                                    style={"minWidth": "150px"},
                                                ),
                                            ],
                                            style={"flex": "1"},
                                        ),
                                    ],
                                    style={"display": "flex", "flexWrap": "wrap", "marginBottom": "1.5rem"},
                                ),
                                dcc.Graph(id="chart-bar", style={"marginBottom": "1.5rem"}),
                                dcc.Graph(id="chart-pie", style={"marginBottom": "1.5rem"}),
                                dcc.Graph(id="chart-scatter"),
                            ],
                            style={"padding": "1.5rem"},
                        ),
                    ],
                ),
            ],
        ),
    ],
    style={"fontFamily": "system-ui, sans-serif", "maxWidth": "1200px", "margin": "0 auto", "padding": "1rem"},
)


@callback(Output("breed-result", "children"), Input("breed-search", "value"))
def update_breed_search(query):
    if not query or not str(query).strip():
        return html.P("Enter a breed name to search.", style={"color": "#888"})
    q = str(query).strip()
    matches = df[df["name"].str.contains(q, case=False, na=False)]
    if matches.empty:
        return html.P("No breed found. Try another search.", style={"color": "#c00"})
    row = matches.iloc[0]
    img = (
        html.Img(
            src=row["image_url"],
            alt=row["name"],
            style={"maxWidth": "300px", "maxHeight": "250px", "objectFit": "contain", "borderRadius": "8px"},
        )
        if pd.notna(row["image_url"]) and str(row["image_url"]).strip()
        else html.P("(No image available)", style={"color": "#888"})
    )
    return html.Div(
        [
            html.H2(row["name"], style={"marginTop": 0}),
            html.Div([img], style={"float": "right", "marginLeft": "1rem", "marginBottom": "1rem"}),
            html.P(row["description"], style={"marginBottom": "0.5rem"}) if pd.notna(row["description"]) else None,
            html.P(
                [html.Strong("Temperament: "), row["temperament"] or "—"],
                style={"marginBottom": "0.5rem"},
            ),
            html.P(
                [html.Strong("Life span: "), row["life_span"] or "—"],
                style={"marginBottom": "0.5rem"},
            ),
            html.P(
                [html.Strong("Height (imperial): "), row["imperial_height"] or "—"],
                style={"marginBottom": "0.5rem"},
            ),
            html.P(
                [html.Strong("Weight (imperial): "), row["imperial_weight"] or "—"],
                style={"marginBottom": "0.5rem"},
            ),
            html.P(
                [html.Strong("Origin: "), row["origin"] or "—"],
                style={"marginBottom": "0.5rem"},
            ),
            html.Div(style={"clear": "both"}),
        ],
        style={"lineHeight": 1.5},
    )


@callback(
    [
        Output("chart-bar", "figure"),
        Output("chart-pie", "figure"),
        Output("chart-scatter", "figure"),
    ],
    [
        Input("filter-bred-for", "value"),
        Input("filter-breed-group", "value"),
        Input("filter-country", "value"),
    ],
)
def update_charts(bred_for, breed_group, country):
    filtered = df.copy()
    if bred_for and bred_for != "all":
        filtered = filtered[filtered["bred_for"] == bred_for]
    if breed_group and breed_group != "all":
        filtered = filtered[filtered["breed_group"] == breed_group]
    if country and country != "all":
        filtered = filtered[filtered["country_code"] == country]

    # Bar chart: breed count by breed_group
    group_counts = filtered["breed_group"].value_counts().reset_index()
    group_counts.columns = ["breed_group", "count"]
    fig_bar = px.bar(
        group_counts,
        x="breed_group",
        y="count",
        title="Number of Breeds by Breed Group",
        labels={"breed_group": "Breed Group", "count": "Number of Breeds"},
    )
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        margin=dict(t=50, b=80),
        font=dict(size=12),
    )

    # Pie chart: distribution by breed_group
    fig_pie = px.pie(
        filtered,
        names="breed_group",
        title="Distribution of Breeds by Group",
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=50, b=20), font=dict(size=12))

    # Scatter: metric_weight vs metric_height
    filtered = filtered.copy()
    filtered["weight_mid"] = filtered["metric_weight"].apply(parse_metric_to_midpoint)
    filtered["height_mid"] = filtered["metric_height"].apply(parse_metric_to_midpoint)
    scatter_df = filtered.dropna(subset=["weight_mid", "height_mid"])
    if scatter_df.empty:
        fig_scatter = go.Figure()
        fig_scatter.add_annotation(
            text="No numeric weight/height data available for filtered breeds.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14),
        )
        fig_scatter.update_layout(title="Weight vs Height (metric)")
    else:
        fig_scatter = px.scatter(
            scatter_df,
            x="weight_mid",
            y="height_mid",
            color="breed_group",
            hover_data=["name"],
            title="Weight vs Height by Breed (metric)",
            labels={"weight_mid": "Weight (kg)", "height_mid": "Height (cm)"},
        )
        fig_scatter.update_layout(
            margin=dict(t=50, b=60),
            font=dict(size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

    return fig_bar, fig_pie, fig_scatter


if __name__ == "__main__":
    app.run(debug=True)
