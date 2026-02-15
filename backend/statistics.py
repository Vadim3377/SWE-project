from dataclasses import dataclass, field
import random

@dataclass
class Statistics:
  
    # Configuration parameters
    _arrival_stddev: int = 0
    _departure_stddev: int = 0
    _rng: random.Random = field(default_factory=lambda: random.Random())

    # Queue Maxima
    max_holding_size: int = 0
    max_takeoff_size: int = 0  # Renamed from takeoff_size as requested
    
    # Metrics 
    total_landings: int = 0
    total_holding_time: int = 0
    total_takeoffs: int = 0
    total_takeoff_wait_time: int = 0
    total_arrival_delay: int = 0
    max_arrival_delay: int = 0
    
    diversions: int = 0
    cancellations: int = 0
    
    # Runway Usage
    runway_busy_time: dict = field(default_factory=dict)

    def configure_from_params(self, params, seed=None):
        self._arrival_stddev = params.arrival_stddev_min
        self._departure_stddev = params.departure_stddev_min
        
        if seed is not None:
            self._rng.seed(seed)

    def sample_inbound_spawn_time(self, scheduled_time_min: int) -> int:
        jitter = self._rng.gauss(0, self._arrival_stddev)
        return max(0, int(scheduled_time_min + jitter))

    def sample_outbound_spawn_time(self, scheduled_time_min: int) -> int:
        jitter = self._rng.gauss(0, self._departure_stddev)
        return max(0, int(scheduled_time_min + jitter))

    def snapshot_queues(self, holding_size: int, takeoff_size: int, time: int):
        if holding_size > self.max_holding_size:
            self.max_holding_size = holding_size
        
        if takeoff_size > self.max_takeoff_size:
            self.max_takeoff_size = takeoff_size

    def record_holding_entry(self, aircraft, time: int):
        # Logic is handled by calculating duration at landing, but 
        # this stub exists for completeness if needed later.
        pass

    def record_landing(self, aircraft, time: int):
        self.total_landings += 1
        
        # Computes the holding time
        if aircraft.enteredHoldingAt is not None:
            hold_duration = time - aircraft.enteredHoldingAt
            self.total_holding_time += hold_duration

        # Computes the arrival delay
        delay = time - aircraft.scheduledTime
        if delay < 0: delay = 0
        self.total_arrival_delay += delay
        
        if delay > self.max_arrival_delay:
            self.max_arrival_delay = delay

    def record_takeoff_enqueue(self, aircraft, time: int):
        pass

    def record_takeoff(self, aircraft, time: int):
        self.total_takeoffs += 1
        
        if aircraft.joinedTakeoffQueueAt is not None:
            wait_duration = time - aircraft.joinedTakeoffQueueAt
            self.total_takeoff_wait_time += wait_duration

    def record_diversion(self, aircraft, time: int):
        self.diversions += 1

    def record_cancellation(self, aircraft, time: int):
        self.cancellations += 1

    def record_runway_usage(self, runway, duration: int):
        r_id = getattr(runway, 'id', str(runway))
        if r_id not in self.runway_busy_time:
            self.runway_busy_time[r_id] = 0
        self.runway_busy_time[r_id] += duration