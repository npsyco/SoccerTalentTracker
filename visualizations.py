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

        # Convert ratings to categorical type with proper ordering
        data[category] = pd.Categorical(data[category], 
                                      categories=self.rating_order,
                                      ordered=True)

        fig.add_trace(go.Scatter(
            x=data['Date'],
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
                categoryarray=self.rating_order
            ),
            height=500
        )

        return fig

    def plot_player_all_categories(self, data, player_name):
        """Plot all categories performance over time for a player"""
        fig = go.Figure()

        # Convert all rating columns to categorical
        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            data[category] = pd.Categorical(data[category], 
                                          categories=self.rating_order,
                                          ordered=True)
            fig.add_trace(go.Scatter(
                x=data['Date'],
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
                categoryarray=self.rating_order
            ),
            height=500
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
                categoryarray=self.rating_order
            ),
            height=500
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
                categoryarray=self.rating_order
            ),
            height=500
        )

        return fig