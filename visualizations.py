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
            line=dict(color=self.colors[category], width=2, shape='spline'),  # Make lines curved
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=f"{player_name}'s {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            yaxis=dict(
                ticktext=self.rating_order,
                tickvals=self.rating_order,
                categoryorder='array',
                categoryarray=self.rating_order,
                range=[-0.5, 3.5]  # Ensure full range is always shown
            ),
            height=500,
            showlegend=True
        )

        return fig

    def plot_player_all_categories(self, data, player_name):
        """Plot all categories performance over time for a player"""
        fig = go.Figure()

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

        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2, shape='spline'),  # Make lines curved
                marker=dict(size=8)
            ))

        fig.update_layout(
            title=f"{player_name}'s udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            yaxis=dict(
                ticktext=self.rating_order,
                tickvals=self.rating_order,
                categoryorder='array',
                categoryarray=self.rating_order,
                range=[-0.5, 3.5]  # Ensure full range is always shown
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
        dates = [pd.Timestamp(date).strftime('%Y-%m-%d') for date in data.index]
        date_counts = pd.Series(dates).value_counts()

        for i, date in enumerate(dates):
            if date_counts[date] > 1:
                x_labels.append(f"{date}\n{data.index[i].strftime('%H:%M')}")
            else:
                x_labels.append(date)

        fig.add_trace(go.Scatter(
            x=x_labels,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(color=self.colors[category], width=2, shape='spline'),  # Make lines curved
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=f"Hold {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Holdvurdering",
            yaxis=dict(
                ticktext=self.rating_order,
                tickvals=self.rating_order,
                categoryorder='array',
                categoryarray=self.rating_order,
                range=[-0.5, 3.5]  # Ensure full range is always shown
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
        dates = [pd.Timestamp(date).strftime('%Y-%m-%d') for date in data.index]
        date_counts = pd.Series(dates).value_counts()

        for i, date in enumerate(dates):
            if date_counts[date] > 1:
                x_labels.append(f"{date}\n{data.index[i].strftime('%H:%M')}")
            else:
                x_labels.append(date)

        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2, shape='spline'),  # Make lines curved
                marker=dict(size=8)
            ))

        fig.update_layout(
            title="Hold udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Holdvurdering",
            yaxis=dict(
                ticktext=self.rating_order,
                tickvals=self.rating_order,
                categoryorder='array',
                categoryarray=self.rating_order,
                range=[-0.5, 3.5]  # Ensure full range is always shown
            ),
            height=500,
            showlegend=True
        )

        return fig

    def plot_player_comparison(self, player_data_dict):
        """Plot comparison between multiple players

        Args:
            player_data_dict: Dictionary with player names as keys and their performance data as values
        """
        # Create subplots: one row for each category
        categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']
        fig = make_subplots(
            rows=len(categories),
            cols=1,
            subplot_titles=categories,
            vertical_spacing=0.1
        )

        for idx, category in enumerate(categories, 1):
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

                fig.add_trace(
                    go.Scatter(
                        x=x_labels,
                        y=data[category],
                        name=f"{player_name}",
                        mode='lines+markers',
                        line=dict(width=2),
                        showlegend=(idx == 1)  # Show legend only for first category
                    ),
                    row=idx,
                    col=1
                )

            # Update y-axis for each subplot
            fig.update_yaxes(
                dict(
                    ticktext=self.rating_order,
                    tickvals=self.rating_order,
                    categoryorder='array',
                    categoryarray=self.rating_order,
                    range=[-0.5, 3.5]
                ),
                row=idx,
                col=1
            )

        # Update layout
        fig.update_layout(
            height=1000,  # Increased height for better visibility
            title="Spillersammenligning over tid",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=1.1,
                xanchor="center",
                x=0.5,
                orientation="h"
            )
        )

        return fig