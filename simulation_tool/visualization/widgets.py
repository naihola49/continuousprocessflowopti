"""
Widget components for Streamlit UI
"""

import streamlit as st
from typing import Dict, List, Optional


def create_station_controls(
    num_stations: int,
    default_mean_pt: float = 1.0,
    default_cv: float = 1.0
) -> Dict:
    """
    Create Streamlit controls for station parameters.
    
    Args:
        num_stations: Number of stations
        default_mean_pt: Default mean processing time
        default_cv: Default coefficient of variation
    
    Returns:
        Dictionary with station parameters
    """
    params = {}
    
    st.subheader("Station Parameters")
    
    cols = st.columns(num_stations)
    
    for i in range(num_stations):
        with cols[i]:
            st.write(f"**Station {i+1}**")
            
            mean_pt = st.slider(
                f"Mean PT",
                min_value=0.1,
                max_value=10.0,
                value=default_mean_pt,
                step=0.1,
                key=f"mean_pt_{i}"
            )
            
            cv = st.slider(
                f"CV",
                min_value=0.0,
                max_value=3.0,
                value=default_cv,
                step=0.1,
                key=f"cv_{i}"
            )
            
            params[i] = {
                'mean_processing_time': mean_pt,
                'cv_processing': cv
            }
    
    return params


def create_variability_controls() -> Dict:
    """
    Create controls for variability parameters.
    
    Returns:
        Dictionary with variability parameters
    """
    st.subheader("Variability Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        processing_cv = st.slider(
            "Processing Variability (CV)",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Coefficient of variation for processing times"
        )
        
        raw_material_cv = st.slider(
            "Raw Material Variability (CV)",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Variability in raw material properties"
        )
    
    with col2:
        demand_cv = st.slider(
            "Demand Variability (CV)",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Variability in demand/arrival rate"
        )
        
        arrival_rate = st.slider(
            "Arrival Rate",
            min_value=0.01,
            max_value=2.0,
            value=0.5,
            step=0.01,
            help="Jobs per time unit"
        )
    
    return {
        'processing_cv': processing_cv,
        'raw_material_cv': raw_material_cv,
        'demand_cv': demand_cv,
        'arrival_rate': arrival_rate
    }


def create_system_controls() -> Dict:
    """
    Create controls for system-level parameters.
    
    Returns:
        Dictionary with system parameters
    """
    st.subheader("System Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_stations = st.number_input(
            "Number of Stations",
            min_value=2,
            max_value=10,
            value=4,
            step=1
        )
        
        conwip_level = st.number_input(
            "CONWIP Level",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            help="Maximum WIP allowed in system"
        )
    
    with col2:
        simulation_duration = st.number_input(
            "Simulation Duration",
            min_value=100.0,
            max_value=10000.0,
            value=1000.0,
            step=100.0
        )
        
        warmup_period = st.number_input(
            "Warmup Period",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=50.0,
            help="Period to exclude from statistics"
        )
    
    return {
        'num_stations': int(num_stations),
        'conwip_level': int(conwip_level),
        'simulation_duration': float(simulation_duration),
        'warmup_period': float(warmup_period)
    }
