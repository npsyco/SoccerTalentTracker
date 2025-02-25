import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class Visualizer:
    def __init__(self):
        self.colors = {
            'Boldholder': '#FF9999',
            'Medspiller': '#66B2FF',
            'Presspiller': '#99FF99',
            'Støttespiller': '#FFCC99'
        }
        self.player_colors = [
            '#1f77b4',  # blue
            '#ff7f0e',  # orange
            '#2ca02c',  # green
            '#d62728'   # red
        ]
        self.rating_order = ['D', 'C', 'B', 'A']

    def plot_player_single_category(self, data, player_name, category):
        """Plot single category performance over time for a player"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        for _, row in data.iterrows():
            if pd.notna(row['Time']):
                x_labels.append(f"{row['Date']}\n{row['Time']}")
            else:
                x_labels.append(str(row['Date']))

        # Add letter grade regions
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),
            ("C", 1.75, 2.75, "#fff3e0"),
            ("B", 2.75, 3.75, "#e8f5e9"),
            ("A", 3.75, 4.5, "#e3f2fd")
        ]

        if x_labels:
            for grade, y0, y1, color in regions:
                fig.add_shape(
                    type="rect",
                    x0=x_labels[0],
                    x1=x_labels[-1],
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )

        # Add markers and lines for data points
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(
                color=self.colors[category],
                width=2,
                shape='spline'
            ),
            marker=dict(
                color=self.colors[category],
                size=10,
                symbol='circle'
            ),
            hovertemplate="Dato: %{x}<br>" + f"{category}: %{{y}}<extra></extra>"
        ))

        fig.update_layout(
            title=f"{player_name}'s {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            xaxis=dict(
                type='category',
                tickmode='array',
                ticktext=x_labels,
                tickvals=x_labels,
                categoryorder='array',
                categoryarray=x_labels,
                showgrid=False,
                fixedrange=True,
                dtick=1,
                automargin=True
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False,
                fixedrange=True
            ),
            height=500,
            showlegend=True,
            margin=dict(l=50, r=20, t=100, b=50),
            dragmode=False,
            modebar=dict(remove=["zoom", "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"])
        )

        return fig

    def plot_player_all_categories(self, data, player_name):
        """Plot all categories performance over time for a player"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        for _, row in data.iterrows():
            if pd.notna(row['Time']):
                x_labels.append(f"{row['Date']}\n{row['Time']}")
            else:
                x_labels.append(str(row['Date']))

        # Add letter grade regions
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),
            ("C", 1.75, 2.75, "#fff3e0"),
            ("B", 2.75, 3.75, "#e8f5e9"),
            ("A", 3.75, 4.5, "#e3f2fd")
        ]

        if x_labels:
            for grade, y0, y1, color in regions:
                fig.add_shape(
                    type="rect",
                    x0=x_labels[0],
                    x1=x_labels[-1],
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )

        # Add data points and lines for each category
        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(
                    color=self.colors[category],
                    width=2,
                    shape='spline'
                ),
                marker=dict(
                    color=self.colors[category],
                    size=10,
                    symbol='circle'
                ),
                hovertemplate="Dato: %{x}<br>" + f"{category}: %{{y}}<extra></extra>"
            ))

        fig.update_layout(
            title=f"{player_name}'s udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            xaxis=dict(
                type='category',
                tickmode='array',
                ticktext=x_labels,
                tickvals=x_labels,
                categoryorder='array',
                categoryarray=x_labels,
                showgrid=False,
                fixedrange=True,
                dtick=1,
                automargin=True
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False,
                fixedrange=True
            ),
            height=500,
            showlegend=True,
            margin=dict(l=50, r=20, t=100, b=50),
            dragmode=False,
            modebar=dict(remove=["zoom", "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"])
        )

        return fig

    def plot_team_single_category(self, data, category):
        """Plot single category performance over time for the team"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        for date, time in data.index:
            if pd.notna(time):
                x_labels.append(f"{date}\n{time}")
            else:
                x_labels.append(str(date))

        # Add letter grade regions
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),
            ("C", 1.75, 2.75, "#fff3e0"),
            ("B", 2.75, 3.75, "#e8f5e9"),
            ("A", 3.75, 4.5, "#e3f2fd")
        ]

        if x_labels:
            for grade, y0, y1, color in regions:
                fig.add_shape(
                    type="rect",
                    x0=x_labels[0],
                    x1=x_labels[-1],
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )

        # Add markers and lines for data points
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(
                color=self.colors[category],
                width=2,
                shape='spline'
            ),
            marker=dict(
                color=self.colors[category],
                size=10,
                symbol='circle'
            ),
            hovertemplate="Dato: %{x}<br>" + f"{category}: %{{y}}<extra></extra>"
        ))

        fig.update_layout(
            title=f"Hold {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Holdvurdering",
            xaxis=dict(
                type='category',
                tickmode='array',
                ticktext=x_labels,
                tickvals=x_labels,
                categoryorder='array',
                categoryarray=x_labels,
                showgrid=False,
                fixedrange=True,
                dtick=1,
                automargin=True
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False,
                fixedrange=True
            ),
            height=500,
            showlegend=True,
            margin=dict(l=50, r=20, t=100, b=50),
            dragmode=False,
            modebar=dict(remove=["zoom", "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"])
        )

        return fig

    def plot_team_all_categories(self, data):
        """Plot all categories performance over time for the team"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        for date, time in data.index:
            if pd.notna(time):
                x_labels.append(f"{date}\n{time}")
            else:
                x_labels.append(str(date))

        # Add letter grade regions
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),
            ("C", 1.75, 2.75, "#fff3e0"),
            ("B", 2.75, 3.75, "#e8f5e9"),
            ("A", 3.75, 4.5, "#e3f2fd")
        ]

        if x_labels:
            for grade, y0, y1, color in regions:
                fig.add_shape(
                    type="rect",
                    x0=x_labels[0],
                    x1=x_labels[-1],
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )

        # Add data points and lines for each category
        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(
                    color=self.colors[category],
                    width=2,
                    shape='spline'
                ),
                marker=dict(
                    color=self.colors[category],
                    size=10,
                    symbol='circle'
                ),
                hovertemplate="Dato: %{x}<br>" + f"{category}: %{{y}}<extra></extra>"
            ))

        fig.update_layout(
            title="Hold udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Holdvurdering",
            xaxis=dict(
                type='category',
                tickmode='array',
                ticktext=x_labels,
                tickvals=x_labels,
                categoryorder='array',
                categoryarray=x_labels,
                showgrid=False,
                fixedrange=True,
                dtick=1,
                automargin=True
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False,
                fixedrange=True
            ),
            height=500,
            showlegend=True,
            margin=dict(l=50, r=20, t=100, b=50),
            dragmode=False,
            modebar=dict(remove=["zoom", "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"])
        )

        return fig

    def plot_player_comparison(self, player_data_dict):
        """Plot comparison between multiple players"""
        if not player_data_dict:
            return go.Figure()

        categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']

        # Calculate subplot dimensions
        height_per_subplot = 300  # Increased height per subplot
        total_height = height_per_subplot * len(categories)

        fig = make_subplots(
            rows=len(categories),
            cols=1,
            subplot_titles=categories,
            vertical_spacing=0.12  # Increased spacing between subplots
        )

        # Add letter grade regions to each subplot
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),
            ("C", 1.75, 2.75, "#fff3e0"),
            ("B", 2.75, 3.75, "#e8f5e9"),
            ("A", 3.75, 4.5, "#e3f2fd")
        ]

        # Track all x values to update region boundaries
        all_dates = set()
        for data in player_data_dict.values():
            all_dates.update([str(date) for date in data['Date']])
        all_dates = sorted(all_dates)

        if not all_dates:
            return fig

        # Add grade regions to each subplot
        for idx, category in enumerate(categories, 1):
            for grade, y0, y1, color in regions:
                fig.add_shape(
                    type="rect",
                    x0=all_dates[0],
                    x1=all_dates[-1],
                    y0=y0,
                    y1=y1,
                    fillcolor=color,
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    row=idx,
                    col=1
                )

        # Add traces for each player
        for i, (player_name, data) in enumerate(player_data_dict.items()):
            player_color = self.player_colors[i % len(self.player_colors)]

            for idx, category in enumerate(categories, 1):
                x_labels = []
                for _, row in data.iterrows():
                    if pd.notna(row['Time']):
                        x_labels.append(f"{row['Date']}\n{row['Time']}")
                    else:
                        x_labels.append(str(row['Date']))

                fig.add_trace(
                    go.Scatter(
                        x=x_labels,
                        y=data[category],
                        mode='lines+markers',
                        name=player_name,
                        line=dict(
                            color=player_color,
                            width=2,
                            shape='spline'
                        ),
                        marker=dict(
                            color=player_color,
                            size=10,
                            symbol='circle'
                        ),
                        showlegend=(idx == 1),
                        hovertemplate=f"{player_name}<br>Dato: %{{x}}<br>{category}: %{{y}}<extra></extra>"
                    ),
                    row=idx,
                    col=1
                )

        # Update layout
        fig.update_layout(
            height=total_height,  # Use calculated height
            title="Spillersammenligning over tid",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=50, r=20, t=100, b=50, pad=4),
            dragmode=False,
            modebar=dict(remove=["zoom", "pan", "select", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"])
        )

        # Update all axes with strict configuration
        for idx in range(1, len(categories) + 1):
            fig.update_yaxes(
                dict(
                    ticktext=["D", "C", "B", "A"],
                    tickvals=[1, 2, 3, 4],
                    range=[0.5, 4.5],
                    showgrid=False,
                    fixedrange=True
                ),
                row=idx,
                col=1
            )

            fig.update_xaxes(
                dict(
                    type='category',
                    tickmode='array',
                    categoryorder='array',
                    showgrid=False,
                    fixedrange=True,
                    dtick=1,
                    automargin=True
                ),
                row=idx,
                col=1
            )

        return fig