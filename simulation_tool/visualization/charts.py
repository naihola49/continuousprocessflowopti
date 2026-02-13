"""
Chart plotting functions for simulation visualization
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def plot_wip_over_time(
    time_points: List[float],
    wip_values: List[float],
    title: str = "Work-In-Process Over Time"
) -> go.Figure:
    """
    Plot WIP over time.
    
    Args:
        time_points: List of time points
        wip_values: List of WIP values
        title: Plot title
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=wip_values,
        mode='lines',
        name='WIP',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Work-In-Process (WIP)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_cycle_time_over_time(
    time_points: List[float],
    cycle_times: List[float],
    title: str = "Cycle Time Over Time"
) -> go.Figure:
    """
    Plot cycle time over time.
    
    Args:
        time_points: List of time points
        cycle_times: List of cycle time values
        title: Plot title
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=cycle_times,
        mode='lines',
        name='Cycle Time',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Cycle Time (CT)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_utilization(
    station_names: List[str],
    utilizations: List[float],
    title: str = "Station Utilization"
) -> go.Figure:
    """
    Plot station utilization as bar chart.
    
    Args:
        station_names: List of station names
        utilizations: List of utilization values (0-1)
        title: Plot title
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    colors = ['#2ca02c' if u < 0.8 else '#d62728' if u > 0.95 else '#ff7f0e' 
              for u in utilizations]
    
    fig.add_trace(go.Bar(
        x=station_names,
        y=utilizations,
        marker_color=colors,
        text=[f'{u:.1%}' for u in utilizations],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Station',
        yaxis_title='Utilization',
        yaxis=dict(range=[0, 1.1]),
        template='plotly_white'
    )
    
    # Add utilization threshold lines
    fig.add_hline(y=0.8, line_dash="dash", line_color="orange", 
                  annotation_text="80% threshold")
    fig.add_hline(y=0.95, line_dash="dash", line_color="red", 
                  annotation_text="95% threshold")
    
    return fig


def plot_metrics_comparison(
    baseline_stats: Dict,
    current_stats: Dict,
    title: str = "Metrics Comparison"
) -> go.Figure:
    """
    Compare baseline vs current metrics.
    
    Args:
        baseline_stats: Dictionary with baseline metrics
        current_stats: Dictionary with current metrics
        title: Plot title
    
    Returns:
        Plotly figure
    """
    metrics = ['throughput', 'avg_cycle_time', 'avg_wip']
    metric_labels = ['Throughput', 'Cycle Time', 'WIP']
    
    baseline_values = [baseline_stats.get(m, 0) for m in metrics]
    current_values = [current_stats.get(m, 0) for m in metrics]
    
    fig = go.Figure()
    
    x_pos = np.arange(len(metrics))
    width = 0.35
    
    fig.add_trace(go.Bar(
        x=x_pos,
        y=baseline_values,
        name='Baseline',
        marker_color='#1f77b4',
        width=width
    ))
    
    fig.add_trace(go.Bar(
        x=x_pos,
        y=current_values,
        name='Current',
        marker_color='#ff7f0e',
        width=width
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(tickmode='array', tickvals=x_pos, ticktext=metric_labels),
        yaxis_title='Value',
        barmode='group',
        template='plotly_white'
    )
    
    return fig


def plot_factory_physics_equation(
    utilization: float,
    cv_arrival: float,
    cv_processing: float,
    mean_processing_time: float,
    cycle_time: float
) -> str:
    """
    Generate LaTeX representation of Factory Physics equation.
    
    Args:
        utilization: Station utilization
        cv_arrival: CV of arrivals
        cv_processing: CV of processing
        mean_processing_time: Mean processing time
        cycle_time: Calculated cycle time
    
    Returns:
        HTML string with equation display
    """
    equation_html = f"""
    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; font-family: monospace;">
        <h4>Kingman's Approximation:</h4>
        <p style="font-size: 14px;">
            CT = (ca² + ce²)/2 × (u/(1-u)) × te + te
        </p>
        <p style="font-size: 12px; margin-top: 10px;">
            <strong>Parameters:</strong><br>
            ca (arrival CV) = {cv_arrival:.2f}<br>
            ce (processing CV) = {cv_processing:.2f}<br>
            u (utilization) = {utilization:.2%}<br>
            te (mean processing time) = {mean_processing_time:.2f}<br>
            <br>
            <strong>Result:</strong> CT = {cycle_time:.2f}
        </p>
    </div>
    """
    return equation_html
