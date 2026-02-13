"""
Factory Physics Equations Module

Implements core Factory Physics relationships:
- Little's Law: WIP = TH × CT
- Kingman's Approximation: CT = (ca² + ce²)/2 × (u/(1-u)) × te + te
- Variability calculations
- Utilization effects
"""

import numpy as np
from typing import Dict, List, Optional


def calculate_cycle_time(
    mean_processing_time: float,
    utilization: float,
    cv_arrival: float = 1.0,
    cv_processing: float = 1.0
) -> float:
    """
    Calculate cycle time using Kingman's approximation.
    
    CT = (ca² + ce²)/2 × (u/(1-u)) × te + te
    
    Where:
    - ca = coefficient of variation of arrivals (CV)
    - ce = coefficient of variation of processing (CV)
    - u = utilization
    - te = mean effective processing time
    
    Args:
        mean_processing_time: Mean effective processing time (te)
        utilization: Station utilization (0-1)
        cv_arrival: Coefficient of variation of arrivals (default 1.0 for Poisson -> memoryless)
        cv_processing: Coefficient of variation of processing (default 1.0)
    
    Returns:
        Cycle time (CT)
    """
    if utilization >= 1.0:
        return np.inf  # Infinite queue if utilization is 100%
    
    if utilization <= 0:
        return mean_processing_time  # No waiting if no utilization
    
    # Kingman's approximation
    variability_term = (cv_arrival**2 + cv_processing**2) / 2
    utilization_term = utilization / (1 - utilization)
    
    cycle_time = variability_term * utilization_term * mean_processing_time + mean_processing_time
    
    return cycle_time


def calculate_wip(throughput: float, cycle_time: float) -> float:
    """
    Calculate Work-In-Process using Little's Law.
    
    WIP = TH × CT
    
    Args:
        throughput: Throughput rate (TH)
        cycle_time: Cycle time (CT)
    
    Returns:
        Work-In-Process (WIP)
    """
    return throughput * cycle_time


def calculate_throughput(wip: float, cycle_time: float) -> float:
    """
    Calculate throughput using Little's Law (rearranged).
    
    TH = WIP / CT
    
    Args:
        wip: Work-In-Process
        cycle_time: Cycle time
    
    Returns:
        Throughput rate
    """
    if cycle_time <= 0:
        return 0.0
    return wip / cycle_time


def calculate_utilization(
    arrival_rate: float,
    processing_rate: float
) -> float:
    """
    Calculate station utilization.
    
    u = λ / μ
    
    Where:
    - λ = arrival rate
    - μ = processing rate (1 / mean_processing_time)
    
    Args:
        arrival_rate: Arrival rate (λ)
        processing_rate: Processing rate (μ)
    
    Returns:
        Utilization (0-1)
    """
    if processing_rate <= 0:
        return 1.0  # Infinite utilization if processing rate is zero
    
    utilization = arrival_rate / processing_rate
    return min(utilization, 1.0)  # Cap at 1.0


def calculate_variability_impact(
    base_cycle_time: float,
    base_cv: float,
    new_cv: float,
    utilization: float
) -> float:
    """
    Calculate how changing variability affects cycle time.
    
    Args:
        base_cycle_time: Original cycle time
        base_cv: Original coefficient of variation
        new_cv: New coefficient of variation
        utilization: Station utilization
    
    Returns:
        New cycle time after variability change
    """
    if utilization >= 1.0:
        return np.inf
    
    # Extract the base processing time from cycle time
    # CT = variability_term * utilization_term * te + te
    # Rearranging: te = CT / (variability_term * utilization_term + 1)
    utilization_term = utilization / (1 - utilization) if utilization < 1.0 else np.inf
    base_variability_term = (1.0**2 + base_cv**2) / 2  # Assuming ca=1.0
    base_te = base_cycle_time / (base_variability_term * utilization_term + 1)
    
    # Calculate new cycle time with new CV
    new_variability_term = (1.0**2 + new_cv**2) / 2
    new_cycle_time = new_variability_term * utilization_term * base_te + base_te
    
    return new_cycle_time


def calculate_bottleneck_station(
    stations: List[Dict],
    arrival_rate: float
) -> int:
    """
    Identify the bottleneck station (highest utilization).
    
    Args:
        stations: List of station dictionaries with 'processing_rate' key
        arrival_rate: System arrival rate
    
    Returns:
        Index of bottleneck station
    """
    utilizations = []
    for station in stations:
        processing_rate = station.get('processing_rate', 1.0)
        util = calculate_utilization(arrival_rate, processing_rate)
        utilizations.append(util)
    
    return np.argmax(utilizations)


def calculate_system_throughput(
    stations: List[Dict],
    arrival_rate: float
) -> float:
    """
    Calculate system throughput (limited by bottleneck).
    
    Args:
        stations: List of station dictionaries
        arrival_rate: System arrival rate
    
    Returns:
        System throughput
    """
    bottleneck_idx = calculate_bottleneck_station(stations, arrival_rate)
    bottleneck_rate = stations[bottleneck_idx].get('processing_rate', 1.0)
    
    return min(arrival_rate, bottleneck_rate)


def calculate_system_cycle_time(
    stations: List[Dict],
    arrival_rate: float,
    cv_arrivals: List[float] = None,
    cv_processing: List[float] = None
) -> float:
    """
    Calculate total system cycle time (sum of all station cycle times).
    
    Args:
        stations: List of station dictionaries with 'mean_processing_time' key
        arrival_rate: System arrival rate
        cv_arrivals: List of arrival CVs for each station (default: all 1.0)
        cv_processing: List of processing CVs for each station (default: all 1.0)
    
    Returns:
        Total system cycle time
    """
    if cv_arrivals is None:
        cv_arrivals = [1.0] * len(stations)
    if cv_processing is None:
        cv_processing = [1.0] * len(stations)
    
    total_ct = 0.0
    current_arrival_rate = arrival_rate
    
    for i, station in enumerate(stations):
        mean_pt = station.get('mean_processing_time', 1.0)
        processing_rate = 1.0 / mean_pt if mean_pt > 0 else np.inf
        util = calculate_utilization(current_arrival_rate, processing_rate)
        
        ct = calculate_cycle_time(
            mean_pt,
            util,
            cv_arrivals[i],
            cv_processing[i]
        )
        total_ct += ct
        
        # Update arrival rate for next station (throughput of current station)
        current_arrival_rate = min(current_arrival_rate, processing_rate)
    
    return total_ct
