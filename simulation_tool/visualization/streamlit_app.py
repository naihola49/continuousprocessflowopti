"""
Main Streamlit application for Factory Physics Simulation Tool
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation_engine import ProductionLine, calculate_cycle_time, calculate_utilization
from visualization.charts import (
    plot_wip_over_time,
    plot_cycle_time_over_time,
    plot_utilization,
    plot_metrics_comparison,
    plot_factory_physics_equation
)
from visualization.widgets import (
    create_station_controls,
    create_variability_controls,
    create_system_controls
)


def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="Factory Physics Simulation Tool",
        page_icon="🏭",
        layout="wide"
    )
    
    st.title("🏭 Factory Physics Simulation Tool")
    st.markdown("""
    Interactive simulation tool demonstrating Factory Physics principles.
    Adjust parameters below to see how variability affects cycle time and WIP.
    """)
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # System parameters
        system_params = create_system_controls()
        
        st.divider()
        
        # Variability controls
        variability_params = create_variability_controls()
        
        st.divider()
        
        # Station parameters
        station_params = create_station_controls(
            num_stations=system_params['num_stations'],
            default_mean_pt=1.0,
            default_cv=variability_params['processing_cv']
        )
        
        st.divider()
        
        # Run simulation button
        run_simulation = st.button("🚀 Run Simulation", type="primary", use_container_width=True)
    
    # Main content area
    if run_simulation:
        with st.spinner("Running simulation..."):
            # Initialize production line
            mean_processing_times = [
                station_params[i]['mean_processing_time'] 
                for i in range(system_params['num_stations'])
            ]
            cv_processing = [
                station_params[i]['cv_processing'] 
                for i in range(system_params['num_stations'])
            ]
            
            production_line = ProductionLine(
                num_stations=system_params['num_stations'],
                conwip_level=system_params['conwip_level'],
                mean_processing_times=mean_processing_times,
                cv_processing=cv_processing,
                arrival_rate=variability_params['arrival_rate'],
                cv_arrival=variability_params['demand_cv']
            )
            
            # Run simulation
            stats = production_line.run(
                duration=system_params['simulation_duration'],
                warmup_period=system_params['warmup_period']
            )
            
            # Store results in session state
            if 'baseline_stats' not in st.session_state:
                st.session_state.baseline_stats = stats
            st.session_state.current_stats = stats
    
    # Display results
    if 'current_stats' in st.session_state:
        stats = st.session_state.current_stats
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Throughput", f"{stats['throughput']:.2f}", "jobs/time")
        with col2:
            st.metric("Avg Cycle Time", f"{stats['avg_cycle_time']:.2f}", "time units")
        with col3:
            st.metric("Avg WIP", f"{stats['avg_wip']:.2f}", "jobs")
        with col4:
            st.metric("Completed Jobs", f"{stats['total_completed']}", "")
        
        st.divider()
        
        # Station utilization
        station_names = [s['name'] for s in stats['station_stats']]
        utilizations = [s['utilization'] for s in stats['station_stats']]
        
        fig_util = plot_utilization(station_names, utilizations)
        st.plotly_chart(fig_util, use_container_width=True)
        
        # Factory Physics equation display
        st.subheader("Factory Physics Equation")
        
        # Calculate for first station as example
        if stats['station_stats']:
            first_station = stats['station_stats'][0]
            mean_pt = station_params[0]['mean_processing_time']
            cv_proc = station_params[0]['cv_processing']
            util = first_station['utilization']
            cv_arr = variability_params['demand_cv']
            
            ct = calculate_cycle_time(
                mean_pt,
                util,
                cv_arr,
                cv_proc
            )
            
            equation_html = plot_factory_physics_equation(
                util, cv_arr, cv_proc, mean_pt, ct
            )
            st.markdown(equation_html, unsafe_allow_html=True)
        
        # Comparison with baseline
        if 'baseline_stats' in st.session_state and st.session_state.baseline_stats != stats:
            st.subheader("Comparison with Baseline")
            fig_comp = plot_metrics_comparison(
                st.session_state.baseline_stats,
                stats
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        # Detailed station statistics
        st.subheader("Station Statistics")
        station_df = pd.DataFrame(stats['station_stats'])
        st.dataframe(station_df, use_container_width=True)
    
    else:
        st.info("👈 Adjust parameters in the sidebar and click 'Run Simulation' to start.")
    
    # Footer
    st.divider()
    st.markdown("""
    ### About
    This tool demonstrates Factory Physics principles:
    - **Little's Law**: WIP = Throughput × Cycle Time
    - **Kingman's Approximation**: Shows how variability and utilization affect cycle time
    - **CONWIP Control**: Limits total work-in-process in the system
    
    Adjust the variability sliders to see how increased variability increases cycle time and WIP.
    """)


if __name__ == "__main__":
    main()
