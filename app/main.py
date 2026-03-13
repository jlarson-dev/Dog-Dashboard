import os
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "breeds.csv")
df = pd.read_csv(DATA_PATH)
df["breed_group"] = df["breed_group"].fillna("Unknown")
df["country_code"] = df["country_code"].fillna("Unknown")


def load_data():
    """Load or reload breeds CSV into global df."""
    global df
    df = pd.read_csv(DATA_PATH)
    df["breed_group"] = df["breed_group"].fillna("Unknown")
    df["country_code"] = df["country_code"].fillna("Unknown")


def parse_metric_to_midpoint(s: str) -> float | None:
    """Parse metric string (e.g. '3.2-4.5' or 'Male: 25-30; Female: 20-25') to midpoint."""
    if pd.isna(s) or not str(s).strip():
        return None
    s = str(s)
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", s)
    if match:
        lo, hi = float(match.group(1)), float(match.group(2))
        return (lo + hi) / 2
    return None

PALETTE = [
    "#E8A87C",  # terracotta
    "#41B3A3",  # teal
    "#C38D9E",  # dusty rose
    "#85CDCA",  # mint
    "#E27D60",  # coral
    "#85C1E9",  # sky blue
    "#BB8FCE",  # lavender
    "#F7DC6F",  # golden
    "#52B788",  # sage
    "#DDA0DD",  # plum
    "#F8B739",  # amber
]


def parse_life_span_range(s: str) -> tuple[float, float] | None:
    """Parse life span string (e.g. '12-15', '10-12 years') to (min, max)."""
    if pd.isna(s) or not str(s).strip():
        return None
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", str(s))
    if match:
        lo, hi = float(match.group(1)), float(match.group(2))
        return (lo, hi)
    return None


app = Dash(__name__, title="Dog Breeds Dashboard")

app.layout = html.Div(
    [
        html.H1("Dog Breeds Dashboard", style={"textAlign": "center", "marginBottom": "0.5rem"}),
        html.P(
            "Explore dog breeds from The Dog API. Search for a specific breed or explore by country or breed group.",
            style={"textAlign": "center", "color": "#666", "marginBottom": "0.5rem"},
        ),
        html.Div(
            [
                html.Button(
                    "Refresh data",
                    id="refresh-button",
                    n_clicks=0,
                    style={
                        "padding": "0.4rem 1rem",
                        "fontSize": "0.9rem",
                        "cursor": "pointer",
                        "borderRadius": "4px",
                        "border": "1px solid #ccc",
                        "background": "#f5f5f5",
                    },
                ),
                html.Span(id="refresh-status", style={"marginLeft": "0.75rem", "fontSize": "0.9rem"}),
            ],
            style={"textAlign": "center", "marginBottom": "1.5rem"},
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
                    label="Explore by Country",
                    value="explore-country",
                    children=[
                        html.Div(
                            [
                                html.P(
                                    "Filter breeds by country. Bar and pie charts show breed group breakdown for the selected country.",
                                    style={"marginBottom": "1rem"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Country", style={"display": "block", "marginBottom": "0.25rem"}),
                                        dcc.Dropdown(
                                            id="filter-country",
                                            options=[{"label": "All countries", "value": "all"}]
                                            + [
                                                {"label": v, "value": v}
                                                for v in sorted(df["country_code"].dropna().unique())
                                                if str(v).strip() and v != "Unknown"
                                            ],
                                            value="all",
                                            clearable=False,
                                            style={"minWidth": "200px"},
                                        ),
                                    ],
                                    style={"marginBottom": "1.5rem"},
                                ),
                                dcc.Graph(id="chart-bar", style={"marginBottom": "1.5rem"}),
                                dcc.Graph(id="chart-pie"),
                            ],
                            style={"padding": "1.5rem"},
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Explore by Breed Group",
                    value="explore-group",
                    children=[
                        html.Div(
                            [
                                html.P(
                                    "Filter by breed group. View weight vs height by individual breed and life span distribution.",
                                    style={"marginBottom": "1rem"},
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
                                            style={"minWidth": "200px"},
                                        ),
                                    ],
                                    style={"marginBottom": "1.5rem"},
                                ),
                                dcc.Graph(id="chart-scatter", style={"marginBottom": "1.5rem"}),
                                dcc.Graph(id="chart-life-span"),
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


@callback(
    Output("refresh-status", "children"),
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_data(n_clicks):
    try:
        from getdata import API_KEY, save_breeds_to_csv, save_breeds_to_json
        save_breeds_to_csv(api_key=API_KEY)
        save_breeds_to_json(api_key=API_KEY)
        load_data()
        return html.Span("Data refreshed. Charts will use new data on next filter or search.", style={"color": "#0a0"})
    except Exception as e:
        return html.Span(f"Refresh failed: {e}", style={"color": "#c00"})


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
    [Output("chart-bar", "figure"), Output("chart-pie", "figure")],
    Input("filter-country", "value"),
)
def update_country_charts(country):
    filtered = df[df["country_code"] == country] if country and country != "all" else df.copy()
    country_label = country if (country and country != "all") else "All countries"

    # Bar chart: breed count by breed_group (country only)
    group_counts = filtered["breed_group"].value_counts().reset_index()
    group_counts.columns = ["breed_group", "count"]
    fig_bar = px.bar(
        group_counts,
        x="breed_group",
        y="count",
        color="breed_group",
        color_discrete_sequence=PALETTE,
        title=f"Number of Breeds by Group in {country_label}",
        labels={"breed_group": "Breed Group", "count": "Number of Breeds"},
    )
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        margin=dict(t=50, b=80),
        font=dict(size=12),
        showlegend=False,
    )

    # Pie chart: distribution by breed_group (country only)
    fig_pie = px.pie(
        filtered,
        names="breed_group",
        color_discrete_sequence=PALETTE,
        title=f"Distribution of Breeds by Group in {country_label}",
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=50, b=20), font=dict(size=12))

    return fig_bar, fig_pie


@callback(
    [Output("chart-scatter", "figure"), Output("chart-life-span", "figure")],
    Input("filter-breed-group", "value"),
)
def update_breed_group_charts(breed_group):
    filtered = (
        df[df["breed_group"] == breed_group].copy()
        if breed_group and breed_group != "all"
        else df.copy()
    )

    # Scatter: weight vs height by individual breeds
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
        fig_scatter.update_layout(
            title="Weight vs Height by Breed (metric)",
            xaxis_title="Weight (kg)",
            yaxis_title="Height (cm)",
        )
    else:
        fig_scatter = px.scatter(
            scatter_df,
            x="weight_mid",
            y="height_mid",
            color="breed_group",
            color_discrete_sequence=PALETTE,
            hover_data=["name", "breed_group"],
            title="Weight vs Height by Breed (metric)",
            labels={"weight_mid": "Weight (kg)", "height_mid": "Height (cm)"},
        )
        fig_scatter.update_layout(
            margin=dict(t=50, b=60),
            font=dict(size=12),
        )

    # Life span chart: breeds on y, life span range (min-max) on x
    life_df = filtered.copy()
    life_df["life_span_range"] = life_df["life_span"].apply(parse_life_span_range)
    life_df = life_df.dropna(subset=["life_span_range"])
    if life_df.empty:
        fig_life = go.Figure()
        fig_life.add_annotation(
            text="No life span data available for filtered breeds.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14),
        )
        fig_life.update_layout(title="Life Span by Breed")
    else:
        life_df["life_min"] = life_df["life_span_range"].apply(lambda r: r[0])
        life_df["life_max"] = life_df["life_span_range"].apply(lambda r: r[1])
        life_df = life_df.sort_values("life_max", ascending=False)
        groups = life_df["breed_group"].unique()
        color_map = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(groups)}
        fig_life = go.Figure()
        for group in groups:
            sub = life_df[life_df["breed_group"] == group]
            fig_life.add_trace(
                go.Bar(
                    x=sub["life_max"] - sub["life_min"],
                    y=sub["name"],
                    base=sub["life_min"],
                    orientation="h",
                    name=group,
                    marker_color=color_map[group],
                    hovertemplate="%{y}<br>Life span: %{base:.1f}–%{customdata:.1f} years<extra></extra>",
                    customdata=sub["life_max"],
                )
            )
        fig_life.update_layout(
            title="Life Span by Breed",
            xaxis_title="Life Span (years)",
            yaxis_title="Breed",
            margin=dict(t=50, b=60, l=120),
            font=dict(size=12),
            yaxis=dict(autorange="reversed"),
            showlegend=len(groups) > 1,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

    return fig_scatter, fig_life


if __name__ == "__main__":
    app.run(debug=True)
