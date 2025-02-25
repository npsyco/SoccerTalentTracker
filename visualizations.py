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
        # Define the rating order for consistent display
        self.rating_order = ['D', 'C', 'B', 'A']

    def plot_player_single_category(self, data, player_name, category):
        """Plot single category performance over time for a player"""
        fig = go.Figure()

        # Format x-axis labels to include time when multiple matches on same date
        x_labels = []
        dates = data['Date'].dt.strftime('%Y-%m-%d').values
        for i, date in enumerate(dates):
            if 'Time' in data.columns and not pd.isna(data['Time'].iloc[i]):
                if len(data[data['Date'].dt.strftime('%Y-%m-%d') == date]) > 1:
                    x_labels.append(f"{date}\n{data['Time'].iloc[i]}")
                else:
                    x_labels.append(date)
            else:
                x_labels.append(date)

        fig.add_trace(go.Scatter(
            x=x_labels,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(color=self.colors[category], width=2, shape='spline'),
            marker=dict(size=8)
        ))

        # Add letter grade regions
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),  # Light red
            ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
            ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
            ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
        ]

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

        fig.update_layout(
            title=f"{player_name}'s {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False
            ),
            height=500,
            showlegend=True
        )

        return fig

    def plot_player_all_categories(self, data, player_name):
        """Plot all categories performance over time for a player"""
        fig = go.Figure()

        # Format x-axis labels to include time when multiple matches on same date
        x_labels = []
        dates = data['Date'].dt.strftime('%Y-%m-%d').values
        for i, date in enumerate(dates):
            if 'Time' in data.columns and not pd.isna(data['Time'].iloc[i]):
                if len(data[data['Date'].dt.strftime('%Y-%m-%d') == date]) > 1:
                    x_labels.append(f"{date}\n{data['Time'].iloc[i]}")
                else:
                    x_labels.append(date)
            else:
                x_labels.append(date)

        # Add letter grade regions first (so they appear behind the lines)
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),  # Light red
            ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
            ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
            ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
        ]

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

        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2, shape='spline'),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title=f"{player_name}'s udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False
            ),
            height=500,
            showlegend=True
        )

        return fig

    def plot_team_single_category(self, data, category):
        """Plot single category performance over time for the team"""
        fig = go.Figure()

        # Format x-axis labels
        x_labels = []

        # Convert tuple index to datetime strings
        dates = []
        for idx in data.index:
            if isinstance(idx, tuple) and len(idx) == 2:
                date, time = idx
                if time:
                    dt = pd.Timestamp.combine(date, time)
                else:
                    dt = pd.Timestamp(date)
                dates.append(dt.strftime('%Y-%m-%d'))
            else:
                dt = pd.Timestamp(idx)
                dates.append(dt.strftime('%Y-%m-%d'))

        date_counts = pd.Series(dates).value_counts()

        for i, idx in enumerate(data.index):
            if isinstance(idx, tuple) and len(idx) == 2:
                date, time = idx
                if time and date_counts[dates[i]] > 1:
                    dt = pd.Timestamp.combine(date, time)
                    x_labels.append(f"{dt.strftime('%Y-%m-%d')}\n{dt.strftime('%H:%M')}")
                else:
                    x_labels.append(dates[i])
            else:
                x_labels.append(dates[i])

        # Add letter grade regions
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),  # Light red
            ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
            ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
            ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
        ]

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

        fig.add_trace(go.Scatter(
            x=x_labels,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(color=self.colors[category], width=2, shape='spline'),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=f"Hold {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Holdvurdering",
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False
            ),
            height=500,
            showlegend=True
        )

        return fig

    def plot_team_all_categories(self, data):
        """Plot all categories performance over time for the team"""
        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        dates = []

        # Convert tuple index to datetime strings
        for idx in data.index:
            if isinstance(idx, tuple) and len(idx) == 2:
                date, time = idx
                if time:
                    dt = pd.Timestamp.combine(date, time)
                else:
                    dt = pd.Timestamp(date)
                dates.append(dt.strftime('%Y-%m-%d'))
            else:
                dt = pd.Timestamp(idx)
                dates.append(dt.strftime('%Y-%m-%d'))

        date_counts = pd.Series(dates).value_counts()

        for i, idx in enumerate(data.index):
            if isinstance(idx, tuple) and len(idx) == 2:
                date, time = idx
                if time and date_counts[dates[i]] > 1:
                    dt = pd.Timestamp.combine(date, time)
                    x_labels.append(f"{dt.strftime('%Y-%m-%d')}\n{dt.strftime('%H:%M')}")
                else:
                    x_labels.append(dates[i])
            else:
                x_labels.append(dates[i])

        # Add letter grade regions first (so they appear behind the lines)
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),  # Light red
            ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
            ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
            ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
        ]

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

        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2, shape='spline'),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title="Hold udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Holdvurdering",
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False
            ),
            height=500,
            showlegend=True
        )

        return fig

    def plot_player_comparison(self, player_data_dict):
            """Plot comparison between multiple players"""
            # Create subplots: one row for each category
            categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']

            # Calculate optimal height based on number of categories
            height_per_subplot = 200  # pixels per subplot
            total_height = max(height_per_subplot * len(categories), 600)

            fig = make_subplots(
                rows=len(categories),
                cols=1,
                subplot_titles=categories,
                vertical_spacing=0.08,  # Reduced spacing for better fit
                row_heights=[1] * len(categories)  # Equal height for all subplots
            )

            # Add letter grade regions to each subplot
            regions = [
                ("D", 0.5, 1.75, "#ffebee"),  # Light red
                ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
                ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
                ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
            ]

            # Track all x values to update region boundaries
            all_dates = []

            for player_name, data in player_data_dict.items():
                # Format x-axis labels
                x_labels = []
                dates = data['Date'].dt.strftime('%Y-%m-%d').values
                for i, date in enumerate(dates):
                    if 'Time' in data.columns and not pd.isna(data['Time'].iloc[i]):
                        if len(data[data['Date'].dt.strftime('%Y-%m-%d') == date]) > 1:
                            x_labels.append(f"{date}\n{data['Time'].iloc[i]}")
                        else:
                            x_labels.append(date)
                    else:
                        x_labels.append(date)

                all_dates.extend(x_labels)

            # Add grade regions to each subplot
            if all_dates:
                for idx, category in enumerate(categories, 1):
                    for grade, y0, y1, color in regions:
                        fig.add_shape(
                            type="rect",
                            x0=min(all_dates),
                            x1=max(all_dates),
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
            for player_name, data in player_data_dict.items():
                x_labels = []
                dates = data['Date'].dt.strftime('%Y-%m-%d').values
                for i, date in enumerate(dates):
                    if 'Time' in data.columns and not pd.isna(data['Time'].iloc[i]):
                        if len(data[data['Date'].dt.strftime('%Y-%m-%d') == date]) > 1:
                            x_labels.append(f"{date}\n{data['Time'].iloc[i]}")
                        else:
                            x_labels.append(date)
                    else:
                        x_labels.append(date)

                for idx, category in enumerate(categories, 1):
                    fig.add_trace(
                        go.Scatter(
                            x=x_labels,
                            y=data[category],
                            name=player_name,
                            mode='lines+markers',
                            line=dict(width=2),
                            showlegend=(idx == 1)  # Show legend only for first category
                        ),
                        row=idx,
                        col=1
                    )

            # Update layout and axes
            fig.update_layout(
                height=total_height,  # Dynamic height based on content
                title="Spillersammenligning over tid",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                modebar=dict(
                    remove=[
                        'zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                        'autoScale2d', 'resetScale2d', 'hoverClosestCartesian',
                        'hoverCompareCartesian'
                    ]
                ),
                margin=dict(
                    l=50,    # left margin
                    r=20,    # right margin
                    t=80,    # top margin reduced
                    b=50,    # bottom margin
                    pad=0    # padding between axis and plot
                )
            )

            # Update all y-axes
            for idx in range(1, len(categories) + 1):
                fig.update_yaxes(
                    dict(
                        ticktext=["D", "C", "B", "A"],
                        tickvals=[1, 2, 3, 4],
                        range=[0.5, 4.5],
                        showgrid=False,
                        fixedrange=True  # Disable y-axis zooming
                    ),
                    row=idx,
                    col=1
                )

                # Disable x-axis zooming and adjust layout
                fig.update_xaxes(
                    fixedrange=True,  # Disable x-axis zooming
                    showgrid=False,   # Remove grid lines
                    row=idx,
                    col=1
                )

            return fig