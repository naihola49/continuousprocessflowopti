"""
Discrete Event Simulation Engine

Core simulation engine for modeling manufacturing systems using discrete event simulation.
"""

import heapq
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from enum import Enum
import numpy as np


class EventType(Enum):
    """Types of events in the simulation"""
    ARRIVAL = "arrival"
    PROCESSING_START = "processing_start"
    PROCESSING_END = "processing_end"
    DEPARTURE = "departure"


@dataclass
class Event:
    """Represents a discrete event in the simulation"""
    time: float
    event_type: EventType
    station_id: Optional[int] = None
    entity_id: Optional[int] = None
    data: Dict = field(default_factory=dict)
    
    def __lt__(self, other):
        """For priority queue ordering (earliest events first)"""
        return self.time < other.time


class DiscreteEventSimulator:
    """
    Discrete Event Simulation Engine
    
    Manages event queue and simulation clock for discrete event simulation.
    """
    
    def __init__(self):
        self.clock = 0.0
        self.event_queue = []  # Priority queue (min-heap)
        self.stats = {
            'total_entities': 0,
            'completed_entities': 0,
            'events_processed': 0
        }
        self.event_handlers = {}
    
    def schedule_event(self, event: Event):
        """
        Schedule an event in the future.
        
        Args:
            event: Event to schedule
        """
        heapq.heappush(self.event_queue, event)
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """
        Register an event handler function.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when this event type occurs
        """
        self.event_handlers[event_type] = handler
    
    def run(self, max_time: float = None, max_events: int = None):
        """
        Run the simulation until stopping condition is met.
        
        Args:
            max_time: Maximum simulation time (None = no limit)
            max_events: Maximum number of events to process (None = no limit)
        """
        while self.event_queue:
            if max_time is not None and self.clock >= max_time:
                break
            if max_events is not None and self.stats['events_processed'] >= max_events:
                break
            
            # Get next event
            event = heapq.heappop(self.event_queue)
            self.clock = event.time
            
            # Handle event
            if event.event_type in self.event_handlers:
                self.event_handlers[event.event_type](event)
            
            self.stats['events_processed'] += 1
    
    def get_next_event_time(self) -> Optional[float]:
        """Get the time of the next scheduled event."""
        if self.event_queue:
            return self.event_queue[0].time
        return None
    
    def reset(self):
        """Reset the simulator to initial state."""
        self.clock = 0.0
        self.event_queue = []
        self.stats = {
            'total_entities': 0,
            'completed_entities': 0,
            'events_processed': 0
        }
