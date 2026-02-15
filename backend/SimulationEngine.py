from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

# NOTE: SimTime class removed as per instructions (using int for minutes)

@dataclass
class EmergencyType:
    mechanical_failure: bool = False
    passenger_illness: bool = False
    fuel_emergency: bool = False

@dataclass
class SimulationEngine:
    """
    Tick-based simulation controller.
    
    Key properties:
      - time is tracked in int minutes for easier calculations
      - Demand generation is rate-based (accumulators per tick)
      - Timing noise (normal distribution) lives in Statistics
      - Jittered aircraft are placed into pending lists, then flushed into queues per tick
    """

    params: any  # Type hint is 'any' for the time being to avoid import issues if SimulationParams isn't perfect
    airport: any
    stats: any
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if hasattr(self.params, "validate"):
            self.params.validate()

        # Configure statistics
        if hasattr(self.stats, "configure_from_params"):
            self.stats.configure_from_params(self.params, seed=self.seed)

        # Simulation time in minutes
        self.current_time: int = 0
        self.is_paused: bool = False

        # Rate accumulators
        self._inbound_acc: float = 0.0
        self._outbound_acc: float = 0.0

        # Pending spawns 
        self._pending_inbound: List[Tuple[int, any]] = []
        self._pending_outbound: List[Tuple[int, any]] = []

        # RNG 
        self._rng = random.Random(self.seed)

        # ID counters
        self._next_in_id: int = 1
        self._next_out_id: int = 1

    # Tick loop
    def tick(self) -> None:
        if self.is_paused:
            return

        dt: int = int(self.params.tick_size_min)
        self.current_time += dt
        now = self.current_time

        self.airport.update_runways(now)

        self._flush_pending(now)

        self._generate_arrivals(now, dt)
        self._generate_departures(now, dt)

        self.update_constraints(now, dt)

        if hasattr(self.airport, "assignLanding"):
            self.airport.assignLanding(now)
        if hasattr(self.airport, "assignTakeoff"): 
            self.airport.assignTakeoff(now)

        
        self.stats.snapshot_queues(
            holding_size=self.airport.holding.size(),
            takeoff_size=self.airport.takeoff.size(),
            time=now
        )

    def run_for(self, duration_min: int) -> None:
        end_time = self.current_time + int(duration_min)
        while self.current_time < end_time:
            self.tick()

    @staticmethod
    def expected_per_tick(rate_per_hour: float, dt_min: int) -> float:
        return rate_per_hour * (dt_min / 60.0)

    # Emergency generation
    def _create_emergency(self) -> EmergencyType:
        r = self._rng.random()
        p_mech = self.params.p_mechanical_failure
        p_ill = self.params.p_passenger_illness

        if r < p_mech:
            return EmergencyType(mechanical_failure=True)
        elif r < p_mech + p_ill:
            return EmergencyType(passenger_illness=True)
        else:
            return EmergencyType(fuel_emergency=True)

    def _apply_emergencies_this_tick(self, aircraft_created: List[any]) -> None:
        n = int(self.params.emergencies_per_tick)
        if n <= 0 or not aircraft_created:
            return

        k = min(n, len(aircraft_created))
        chosen = self._rng.sample(aircraft_created, k)

        for a in chosen:
            a.emergency = self._create_emergency()

    # Arrival / departure generation
    def _generate_arrivals(self, now: int, dt: int) -> None:
        self._inbound_acc += self.expected_per_tick(self.params.inbound_rate_per_hour, dt)
        created = []

        while self._inbound_acc >= 1.0:
            self._inbound_acc -= 1.0

            # Create aircraft 
            a = self.make_inbound_aircraft(now)
            created.append(a)

            # Sample actual spawn time (jitter) via Statistics
            spawn_time = self.stats.sample_inbound_spawn_time(now)
            
            # Add to pending list
            self._pending_inbound.append((spawn_time, a))

        self._apply_emergencies_this_tick(created)

    def _generate_departures(self, now: int, dt: int) -> None:
        self._outbound_acc += self.expected_per_tick(self.params.outbound_rate_per_hour, dt)
        created = []

        while self._outbound_acc >= 1.0:
            self._outbound_acc -= 1.0

            a = self.make_outbound_aircraft(now)
            created.append(a)

            spawn_time = self.stats.sample_outbound_spawn_time(now)
            self._pending_outbound.append((spawn_time, a))

        self._apply_emergencies_this_tick(created)

    # Pending flush
    def _flush_pending(self, now: int) -> None:
       
        # Inbound
        if self._pending_inbound:
            due, future = [], []
            for t, a in self._pending_inbound:
                if t <= now:
                    due.append((t, a))
                else:
                    future.append((t, a))
            self._pending_inbound = future
            
            for t, a in due:
                self.airport.handleInbound(a, t) # Pass the actual spawn time 't'

        # Outbound
        if self._pending_outbound:
            due, future = [], []
            for t, a in self._pending_outbound:
                if t <= now:
                    due.append((t, a))
                else:
                    future.append((t, a))
            self._pending_outbound = future
            
            for t, a in due:
                self.airport.handleOutbound(a, t)

    def update_constraints(self, now: int, dt: int) -> None:
        """
        Placeholder for fuel burn logic, etc.
        """
        pass

    # Aircraft factories
    def make_inbound_aircraft(self, now: int):
        from backend.aircraft import Aircraft
        aircraft_id = f"I{self._next_in_id}"
        self._next_in_id += 1

        fuel = self._rng.randint(
            self.params.fuel_initial_min_min,
            self.params.fuel_initial_max_min,
        )

        return Aircraft(
            aircraft_id=aircraft_id,
            flight_type="INBOUND",
            scheduledTime=now,
            fuelRemaining=fuel,
            emergency=None,
        )

    def make_outbound_aircraft(self, now: int):
        from backend.aircraft import Aircraft
        aircraft_id = f"O{self._next_out_id}"
        self._next_out_id += 1

        return Aircraft(
            aircraft_id=aircraft_id,
            flight_type="OUTBOUND",
            scheduledTime=now,
            fuelRemaining=0, # Fixed outbound fuel (usually irrelevant or max)
            emergency=None,
        )