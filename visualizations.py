import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class Visualizer:
    def __init__(self):
        self.colors = {
            'Technical': '#FF9999',
            'Tactical': '#66B2FF',
            'Physical': '#99FF99',
            'Mental': '#FFCC99'
        }

    def plot_player_single_category(self, data, player_name, category):
        """Plot single category performance over time for a player"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(color=self.colors[category], width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f"{player_name}'s {category} Performance Over Time",
            xaxis_title="Date",
            yaxis_title="Rating",
            yaxis_range=[0, 10],
            height=500
        )
        
        return fig

    def plot_player_all_categories(self, data, player_name):
        """Plot all categories performance over time for a player"""
        fig = go.Figure()
        
        for category in ['Technical', 'Tactical', 'Physical', 'Mental']:
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=f"{player_name}'s Performance Over Time",
            xaxis_title="Date",
            yaxis_title="Rating",
            yaxis_range=[0, 10],
            height=500
        )
        
        return fig

    def plot_team_single_category(self, data, category):
        """Plot single category performance over time for the team"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[category],
            mode='lines+markers',
            name=category,
            line=dict(color=self.colors[category], width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f"Team {category} Performance Over Time",
            xaxis_title="Date",
            yaxis_title="Average Rating",
            yaxis_range=[0, 10],
            height=500
        )
        
        return fig

    def plot_team_all_categories(self, data):
        """Plot all categories performance over time for the team"""
        fig = go.Figure()
        
        for category in ['Technical', 'Tactical', 'Physical', 'Mental']:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[category],
                mode='lines+markers',
                name=category,
                line=dict(color=self.colors[category], width=2),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Team Performance Over Time",
            xaxis_title="Date",
            yaxis_title="Average Rating",
            yaxis_range=[0, 10],
            height=500
        )
        
        return fig
