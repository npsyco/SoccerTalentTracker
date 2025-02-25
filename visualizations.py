import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

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
        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        dates = data['Date']
        for i, date in enumerate(dates):
            if 'Time' in data.columns and not pd.isna(data['Time'].iloc[i]):
                if len(data[data['Date'] == date]) > 1:
                    x_labels.append(f"{date}\n{data['Time'].iloc[i]}")
                else:
                    x_labels.append(str(date))
            else:
                x_labels.append(str(date))

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
            showlegend=True,
            margin=dict(
                l=50,    # left margin
                r=20,    # right margin
                t=100,   # top margin for title
                b=50,    # bottom margin
            )
        )

        return fig

    def plot_player_all_categories(self, data, player_name):
        """Plot all categories performance over time for a player"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        # Debug: Print raw input data
        st.write("### Debug: Visualization Input Data")
        st.write("Raw Date column:", data['Date'].unique().tolist())
        st.write("Raw Time column:", data['Time'].unique().tolist())

        # Format x-axis labels
        x_labels = []
        # Track exact date-time pairs for debugging
        date_time_pairs = []

        for _, row in data.iterrows():
            date_str = str(row['Date'])
            time_str = str(row['Time']) if pd.notna(row['Time']) else None
            date_time_pairs.append((date_str, time_str))

            # Create x-axis label
            if time_str and time_str != 'None':
                x_labels.append(f"{date_str}\n{time_str}")
            else:
                x_labels.append(date_str)

        # Debug: Print processed labels
        st.write("### Debug: Visualization Processing")
        st.write("Date-Time pairs:", date_time_pairs)
        st.write("Final x-axis labels:", x_labels)

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

        # Add data points for each category
        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='markers',  # Only markers, no lines
                name=category,
                marker=dict(
                    color=self.colors[category],
                    size=10,
                    symbol='circle'
                ),
                hovertemplate="Dato: %{x}<br>" + f"{category}: %{{y}}<extra></extra>"
            ))

        # Debug: Print final plot configuration
        st.write("### Debug: Plot Configuration")
        st.write("Number of data points:", len(x_labels))
        st.write("X-axis range:", [x_labels[0], x_labels[-1]] if x_labels else "Empty")

        fig.update_layout(
            title=f"{player_name}'s udvikling over tid",
            xaxis_title="Dato",
            yaxis_title="Vurdering",
            xaxis=dict(
                type='category',  # Force x-axis to be categorical
                tickmode='array',
                ticktext=x_labels,
                tickvals=x_labels,
                categoryorder='array',
                categoryarray=x_labels,
                showgrid=False,
                fixedrange=True,  # Disable zoom/pan
                rangemode='tozero',  # Force exact range
                constrain='domain',  # Ensure axis stays within its domain
                dtick=1,  # Force tick for every category
                automargin=True  # Adjust margins for labels
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False,
                fixedrange=True  # Disable zoom/pan
            ),
            height=500,
            showlegend=True,
            margin=dict(l=50, r=20, t=100, b=50),
            dragmode=False,  # Disable all drag interactions
            staticPlot=True  # Make the plot completely static
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
            ("D", 0.5, 1.75, "#ffebee"),  # Light red
            ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
            ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
            ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
        ]

        if x_labels:  # Only add regions if we have data points
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

        # Add markers for data points
        y_values = data[category]
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=y_values,
            mode='markers',
            name=category,
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
                showgrid=False,
                constrain='domain'
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False
            ),
            height=500,
            showlegend=True,
            margin=dict(
                l=50,
                r=20,
                t=100,
                b=50,
            )
        )

        return fig

    def plot_team_all_categories(self, data):
        """Plot all categories performance over time for the team"""
        if data.empty:
            return go.Figure()  # Return empty figure if no data

        fig = go.Figure()

        # Format x-axis labels
        x_labels = []
        for date, time in data.index:
            if pd.notna(time):
                x_labels.append(f"{date}\n{time}")
            else:
                x_labels.append(str(date))

        # Add letter grade regions first (so they appear behind the lines)
        regions = [
            ("D", 0.5, 1.75, "#ffebee"),  # Light red
            ("C", 1.75, 2.75, "#fff3e0"),  # Light orange
            ("B", 2.75, 3.75, "#e8f5e9"),  # Light green
            ("A", 3.75, 4.5, "#e3f2fd")    # Light blue
        ]

        if x_labels:  # Only add regions if we have data points
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
                mode='markers', # Only markers, no lines
                name=category,
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
                type='category',  # Force x-axis to be categorical
                tickmode='array',
                ticktext=x_labels,
                tickvals=x_labels,
                showgrid=False,
                fixedrange=True, #Disable zoom/pan
                constrain='domain'  # Ensure axis stays within its domain
            ),
            yaxis=dict(
                ticktext=["D", "C", "B", "A"],
                tickvals=[1, 2, 3, 4],
                range=[0.5, 4.5],
                showgrid=False,
                fixedrange=True #Disable zoom/pan
            ),
            height=500,
            showlegend=True,
            margin=dict(
                l=50,    # left margin
                r=20,    # right margin
                t=100,   # top margin for title
                b=50,    # bottom margin
            ),
            dragmode=False, # Disable all drag interactions
            staticPlot=True # Make the plot completely static
        )

        return fig

    def plot_team_performance(self, data):
        """Plot team performance over time"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()
        x_labels = []
        for date, time in data.index:
            if pd.notna(time):
                x_labels.append(f"{date}\n{time}")
            else:
                x_labels.append(str(date))

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

        for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
            fig.add_trace(go.Scatter(
                x=x_labels,
                y=data[category],
                mode='markers',
                name=category,
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
                showgrid=False,
                fixedrange=True,
                constrain='domain'
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
            staticPlot=True
        )
        return fig

    def plot_player_comparison(self, player_data_dict):
        """Plot comparison between multiple players"""
        if not player_data_dict:
            return go.Figure()

        categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']
        fig = make_subplots(
            rows=len(categories),
            cols=1,
            subplot_titles=categories,
            vertical_spacing=0.1
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

        # Add traces for each player with consistent colors
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
                        mode='markers',  # Only markers, no lines
                        name=player_name,
                        marker=dict(
                            color=player_color,
                            size=10,
                            symbol='circle'
                        ),
                        showlegend=(idx == 1),  # Show legend only for first category
                        hovertemplate=f"{player_name}<br>Dato: %{{x}}<br>{category}: %{{y}}<extra></extra>"
                    ),
                    row=idx,
                    col=1
                )

        # Update layout
        fig.update_layout(
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
            dragmode=False,  # Disable all drag interactions
            staticPlot=True  # Make the plot completely static
        )

        # Update all axes with strict configuration
        for idx in range(1, len(categories) + 1):
            fig.update_yaxes(
                dict(
                    ticktext=["D", "C", "B", "A"],
                    tickvals=[1, 2, 3, 4],
                    range=[0.5, 4.5],
                    showgrid=False,
                    fixedrange=True,  # Disable zoom/pan
                    constrain='domain'
                ),
                row=idx,
                col=1
            )

            fig.update_xaxes(
                dict(
                    type='category',
                    tickmode='array',
                    showgrid=False,
                    fixedrange=True,  # Disable zoom/pan
                    constrain='domain',
                    rangemode='tozero',  # Force exact range
                    automargin=True
                ),
                row=idx,
                col=1
            )

        return fig