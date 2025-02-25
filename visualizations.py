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
        categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']

        # Calculate optimal height based on number of categories and screen size
        height_per_subplot = 250  # pixels per subplot
        total_height = height_per_subplot * len(categories)

        fig = make_subplots(
            rows=len(categories),
            cols=1,
            subplot_titles=categories,
            vertical_spacing=0.1,  # Increased spacing for better readability
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

        # First pass: collect all dates
        for player_name, data in player_data_dict.items():
            dates = data['Date'].dt.strftime('%Y-%m-%d').values
            all_dates.extend(dates)

        # Sort unique dates for x-axis range
        all_dates = sorted(set(all_dates))

        # Add grade regions to each subplot
        for idx, category in enumerate(categories, 1):
            for grade, y0, y1, color in regions:
                if all_dates:  # Only add if we have dates
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
        for player_name, data in player_data_dict.items():
            dates = data['Date'].dt.strftime('%Y-%m-%d').values

            for idx, category in enumerate(categories, 1):
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=data[category],
                        name=player_name,
                        mode='lines+markers',
                        line=dict(width=2),
                        marker=dict(size=8),
                        showlegend=(idx == 1)  # Show legend only for first category
                    ),
                    row=idx,
                    col=1
                )

        # Update layout with strict configuration
        fig.update_layout(
            height=total_height,
            title=dict(
                text="Spillersammenligning over tid",
                y=0.95  # Move title up slightly
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            # Completely disable the modebar (removes all interactive controls)
            modebar_remove=[
                'zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                'autoScale2d', 'resetScale2d', 'hoverClosestCartesian',
                'hoverCompareCartesian', 'toImage'
            ],
            modebar_display=False,  # Hide the entire modebar
            # Optimize margins
            margin=dict(
                l=50,    # left margin
                r=20,    # right margin
                t=100,   # top margin for title and legend
                b=50,    # bottom margin
                pad=4    # padding between subplots
            ),
            # Disable all hover interactions
            hovermode=False
        )

        # Update all axes with strict configuration
        for idx in range(1, len(categories) + 1):
            # Configure y-axis
            fig.update_yaxes(
                dict(
                    ticktext=["D", "C", "B", "A"],
                    tickvals=[1, 2, 3, 4],
                    range=[0.5, 4.5],
                    showgrid=False,
                    fixedrange=True,  # Disable zooming
                    constrain='domain'  # Ensure axis stays within its domain
                ),
                row=idx,
                col=1
            )

            # Configure x-axis
            fig.update_xaxes(
                dict(
                    showgrid=False,
                    fixedrange=True,  # Disable zooming
                    constrain='domain',  # Ensure axis stays within its domain
                    rangeslider=dict(visible=False),  # Remove range slider if present
                ),
                row=idx,
                col=1
            )

        return fig