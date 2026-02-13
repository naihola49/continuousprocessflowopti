"""
Production Line Simulation

Models a multi-stage production line with CONWIP control.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from .discrete_event_sim import DiscreteEventSimulator, Event, EventType
from .factory_physics import calculate_cycle_time, calculate_utilization


class StationState(Enum):
    """States a station can be in"""
    IDLE = "idle"
    PROCESSING = "processing"
    BLOCKED = "blocked"  # Finished but downstream is full
    STARVED = "starved"  # Ready but no material available


@dataclass
class Station:
    """Represents a single station in the production line"""
    station_id: int
    name: str
    mean_processing_time: float
    cv_processing: float = 1.0  # Coefficient of variation
    buffer_capacity: int = 0  # 0 = no buffer (blocking)
    
    # State
    state: StationState = StationState.IDLE
    current_job: Optional[int] = None
    queue: List[int] = field(default_factory=list)
    buffer: List[int] = field(default_factory=list)
    
    # Statistics
    total_processed: int = 0
    total_processing_time: float = 0.0
    total_idle_time: float = 0.0
    total_blocked_time: float = 0.0
    total_starved_time: float = 0.0
    last_state_change_time: float = 0.0
    
    def get_processing_time(self) -> float:
        """Sample processing time from distribution."""
        if self.cv_processing == 0:
            return self.mean_processing_time
        
        # Use gamma distribution to match mean and CV
        # For gamma: mean = shape * scale, CV = 1/sqrt(shape)
        # So: shape = 1/(CV^2), scale = mean * CV^2
        if self.cv_processing > 0:
            shape = 1.0 / (self.cv_processing ** 2)
            scale = self.mean_processing_time / shape
            return np.random.gamma(shape, scale)
        else:
            return self.mean_processing_time
    
    def update_statistics(self, current_time: float):
        """Update time-based statistics."""
        time_elapsed = current_time - self.last_state_change_time
        
        if self.state == StationState.IDLE:
            self.total_idle_time += time_elapsed
        elif self.state == StationState.BLOCKED:
            self.total_blocked_time += time_elapsed
        elif self.state == StationState.STARVED:
            self.total_starved_time += time_elapsed
        
        self.last_state_change_time = current_time
    
    def get_utilization(self, current_time: float) -> float:
        """Calculate utilization up to current time."""
        self.update_statistics(current_time)
        total_time = current_time
        if total_time > 0:
            processing_time = total_time - self.total_idle_time - self.total_blocked_time - self.total_starved_time
            return processing_time / total_time
        return 0.0


class ProductionLine:
    """
    Multi-stage production line with CONWIP control.
    
    CONWIP (Constant Work-In-Process): Limits total WIP in the system.
    """
    
    def __init__(
        self,
        num_stations: int = 4,
        conwip_level: int = 10,
        mean_processing_times: Optional[List[float]] = None,
        cv_processing: Optional[List[float]] = None,
        arrival_rate: float = 0.1,
        cv_arrival: float = 1.0
    ):
        """
        Initialize production line.
        
        Args:
            num_stations: Number of stations in the line
            conwip_level: Maximum WIP allowed in system
            mean_processing_times: Mean processing time for each station
            cv_processing: Coefficient of variation for each station
            arrival_rate: Arrival rate (jobs per time unit)
            cv_arrival: Coefficient of variation of arrivals
        """
        self.num_stations = num_stations
        self.conwip_level = conwip_level
        self.arrival_rate = arrival_rate
        self.cv_arrival = cv_arrival
        
        # Initialize stations
        if mean_processing_times is None:
            mean_processing_times = [1.0] * num_stations
        if cv_processing is None:
            cv_processing = [1.0] * num_stations
        
        self.stations = [
            Station(
                station_id=i,
                name=f"Station {i+1}",
                mean_processing_time=mean_processing_times[i],
                cv_processing=cv_processing[i]
            )
            for i in range(num_stations)
        ]
        
        # Simulation state
        self.simulator = DiscreteEventSimulator()
        self.entity_counter = 0
        self.system_wip = 0  # Current WIP in system
        self.completed_jobs = []
        self.job_arrival_times = {}
        self.job_completion_times = {}
        
        # Register event handlers
        self.simulator.register_handler(EventType.ARRIVAL, self._handle_arrival)
        self.simulator.register_handler(EventType.PROCESSING_END, self._handle_processing_end)
        
        # Statistics
        self.stats_history = []
    
    def _handle_arrival(self, event: Event):
        """Handle job arrival event."""
        if self.system_wip < self.conwip_level:
            # Can accept new job
            self.entity_counter += 1
            job_id = self.entity_counter
            self.system_wip += 1
            self.job_arrival_times[job_id] = self.simulator.clock
            
            # Try to start processing at first station
            self._try_start_processing(0, job_id)
        else:
            # System is full (CONWIP limit), reject or delay arrival
            # For now, we'll just not accept it (could also delay)
            pass
    
    def _try_start_processing(self, station_id: int, job_id: int):
        """Try to start processing a job at a station."""
        station = self.stations[station_id]
        
        if station.state == StationState.IDLE:
            # Station is idle, start processing immediately
            station.state = StationState.PROCESSING
            station.current_job = job_id
            station.update_statistics(self.simulator.clock)
            
            # Schedule processing end
            processing_time = station.get_processing_time()
            # Ensure processing time is positive
            processing_time = max(0.001, processing_time)
            end_event = Event(
                time=self.simulator.clock + processing_time,
                event_type=EventType.PROCESSING_END,
                station_id=station_id,
                entity_id=job_id
            )
            self.simulator.schedule_event(end_event)
        else:
            # Station is busy, add to queue (avoid duplicates)
            if job_id not in station.queue:
                station.queue.append(job_id)
    
    def _handle_processing_end(self, event: Event):
        """Handle processing completion event."""
        station_id = event.station_id
        job_id = event.entity_id
        station = self.stations[station_id]
        
        # Update station statistics
        station.total_processed += 1
        station.current_job = None
        station.state = StationState.IDLE
        station.update_statistics(self.simulator.clock)
        
        # Move job to next station or complete
        if station_id < self.num_stations - 1:
            # Move to next station
            self._try_start_processing(station_id + 1, job_id)
        else:
            # Job completed
            self.job_completion_times[job_id] = self.simulator.clock
            self.completed_jobs.append(job_id)
            self.system_wip -= 1
            
            # Schedule new arrival immediately
            if self.system_wip < self.conwip_level:
                new_arrival = Event(
                    time=self.simulator.clock,
                    event_type=EventType.ARRIVAL
                )
                self.simulator.schedule_event(new_arrival)
        
        # Process next job in queue if any
        if station.queue:
            next_job = station.queue.pop(0)
            self._try_start_processing(station_id, next_job)
    
    def generate_arrivals(self, duration: float):
        """Generate arrival events for the simulation duration."""
        current_time = 0.0
        while current_time < duration:
            # Generate inter-arrival time
            if self.cv_arrival == 1.0:
                # Exponential (Poisson process)
                inter_arrival = np.random.exponential(1.0 / self.arrival_rate)
            else:
                # Use appropriate distribution based on CV
                inter_arrival = np.random.exponential(1.0 / (self.arrival_rate * self.cv_arrival))
            
            current_time += inter_arrival
            if current_time < duration:
                arrival_event = Event(
                    time=current_time,
                    event_type=EventType.ARRIVAL
                )
                self.simulator.schedule_event(arrival_event)
    
    def run(self, duration: float, warmup_period: float = 0.0):
        """
        Run the simulation.
        
        Args:
            duration: Total simulation duration
            warmup_period: Period to exclude from statistics (for steady state)
        """
        # Generate arrivals
        self.generate_arrivals(duration)
        
        # Run simulation
        self.simulator.run(max_time=duration)
        
        # Calculate statistics
        return self.get_statistics(warmup_period)
    
    def get_statistics(self, warmup_period: float = 0.0) -> Dict:
        """
        Calculate and return simulation statistics.
        
        Args:
            warmup_period: Period to exclude from statistics
        
        Returns:
            Dictionary of statistics
        """
        # Update all station statistics to current time
        for station in self.stations:
            station.update_statistics(self.simulator.clock)
        
        # Calculate cycle times
        cycle_times = []
        for job_id in self.completed_jobs:
            if job_id in self.job_arrival_times and job_id in self.job_completion_times:
                arrival_time = self.job_arrival_times[job_id]
                completion_time = self.job_completion_times[job_id]
                if arrival_time >= warmup_period:
                    cycle_times.append(completion_time - arrival_time)
        
        # Calculate throughput
        total_time = self.simulator.clock - warmup_period
        throughput = len(cycle_times) / total_time if total_time > 0 else 0.0
        
        # Calculate average cycle time
        avg_cycle_time = np.mean(cycle_times) if cycle_times else 0.0
        
        # Calculate average WIP (using Little's Law)
        avg_wip = throughput * avg_cycle_time if avg_cycle_time > 0 else 0.0
        
        # Station-level statistics
        station_stats = []
        for station in self.stations:
            util = station.get_utilization(self.simulator.clock)
            station_stats.append({
                'station_id': station.station_id,
                'name': station.name,
                'utilization': util,
                'total_processed': station.total_processed,
                'avg_processing_time': station.total_processing_time / station.total_processed if station.total_processed > 0 else 0.0
            })
        
        return {
            'throughput': throughput,
            'avg_cycle_time': avg_cycle_time,
            'avg_wip': avg_wip,
            'total_completed': len(cycle_times),
            'station_stats': station_stats,
            'simulation_time': self.simulator.clock
        }
    
    def update_parameters(
        self,
        station_id: int,
        mean_processing_time: Optional[float] = None,
        cv_processing: Optional[float] = None
    ):
        """Update parameters for a specific station."""
        station = self.stations[station_id]
        if mean_processing_time is not None:
            station.mean_processing_time = mean_processing_time
        if cv_processing is not None:
            station.cv_processing = cv_processing
    
    def reset(self):
        """Reset the production line to initial state."""
        self.simulator.reset()
        self.entity_counter = 0
        self.system_wip = 0
        self.completed_jobs = []
        self.job_arrival_times = {}
        self.job_completion_times = {}
        self.stats_history = []
        
        for station in self.stations:
            station.state = StationState.IDLE
            station.current_job = None
            station.queue = []
            station.buffer = []
            station.total_processed = 0
            station.total_processing_time = 0.0
            station.total_idle_time = 0.0
            station.total_blocked_time = 0.0
            station.total_starved_time = 0.0
            station.last_state_change_time = 0.0
