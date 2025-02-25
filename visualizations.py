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
            line=dict(color=self.colors[category], width=2),
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
                line=dict(color=self.colors[category], width=2),
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

        # Ensure data is properly categorical
        data[category] = pd.Categorical(data[category], 
                                      categories=self.rating_order,
                                      ordered=True)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(color=self.colors[category], width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=f"Hold {category} udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Gennemsnit Vurdering",
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

        # Convert all categories to proper categorical type
        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            data[category] = pd.Categorical(data[category], 
                                          categories=self.rating_order,
                                          ordered=True)
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title="Hold udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Gennemsnit Vurdering",
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