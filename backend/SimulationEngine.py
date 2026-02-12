# SimulationEngine.py
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

from SimulationParameters import SimulationParams
from airport import Airport
from aircraft import Aircraft
from statistics import Statistics


# Moved from airport to SimEng
class SimTime:
    def __init__(self, time: int):
        self.time = time

    def advance(self, dt: int):
        self.time += dt


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
      - SimTime is object
      - Demand generation is rate-based (accumulators per tick)
      - Timing noise (normal distribution) lives in Statistics (not here)
      - Jittered aircraft are placed into pending lists, then flushed into queues per tick
    """

    params: SimulationParams
    airport: Airport
    stats: Statistics
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        # Validate parameters early
        self.params.validate()

        # Configure statistics sampling / RNG if supported
        if hasattr(self.stats, "configure_from_params"):
            self.stats.configure_from_params(self.params, seed=self.seed)

        # Basic state
        self.current_time_min: SimTime = SimTime(0)
        self.is_paused: bool = False

        # Rate-based accumulation
        self._inbound_acc: float = 0.0
        self._outbound_acc: float = 0.0

        # Pending spawns (spawn_time, aircraft)
        self._pending_inbound: List[Tuple[SimTime, Aircraft]] = []
        self._pending_outbound: List[Tuple[SimTime, Aircraft]] = []

        # Local RNG for IDs / non-normal randomness (normal jitter is in Statistics)
        self._rng = random.Random(self.seed)

        # Simple counters for unique IDs
        self._next_in_id: int = 1
        self._next_out_id: int = 1


    # Core tick loop
    def tick(self) -> None:
        if self.is_paused:
            return

        now: SimTime = self.current_time_min
        dt: int = self.params.tick_size_min

        # Release runways
        self.airport.updateRunways(now)                         #CHANGED: updateRunways accepts type SimTime not int type.

        # Inject aircraft whose jittered spawn time has arrived
        self._flush_pending(now)                           

        # Generate new aircraft, but add to pending using Statistics jitter
        self._generate_arrivals(now, dt)                  
        self._generate_departures(now, dt)                 

        # Constraints
        self.update_constraints(now.time, dt)                   ##CHANGED

        # Assign runway usage
        self.airport.assignLanding(now)
        self.airport.assignTakeoff(now)

        # Snapshot stats
        #TODO: Method doesn't exist in statistics class, what's the purpose of this method anyways? Can someone make it :)
        self.stats.snapshotQueues(
            holding_size=self.airport.holding.size(),
            takeoff_size=self.airport.takeoff.size(),
            time=int(now),
        )

        # Advance time
        self.current_time = self.current_time.advance(dt)                      

    def run_for(self, duration_min: int) -> None:
        end_time = self.current_time_min.time + duration_min
        while self.current_time_min < end_time:
            self.tick()


    # Demand generation
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

    def _apply_emergencies_this_tick(self, aircraft_created: List[Aircraft]) -> None:
        n = int(self.params.emergencies_per_tick)
        if n <= 0 or not aircraft_created:
            return

        k = min(n, len(aircraft_created))
        chosen = self._rng.sample(aircraft_created, k)

        for a in chosen:
            a.Emergency = self._create_emergency()

    # Arrival / departure generation
    def _generate_arrivals(self, now: SimTime, dt: int) -> None:
        self._inbound_acc += self.expected_per_tick(self.params.inbound_rate_per_hour, dt)
        created: List[Aircraft] = []

        while self._inbound_acc >= 1.0:
            self._inbound_acc -= 1.0

            a = self.make_inbound_aircraft(now)
            created.append(a)

            spawn_raw = self.stats.sample_inbound_spawn_time(int(now))
            self._pending_inbound.append((SimTime(int(spawn_raw)), a))

        self._apply_emergencies_this_tick(created)

    def _generate_departures(self, now: SimTime, dt: int) -> None:
        self._outbound_acc += self.expected_per_tick(self.params.outbound_rate_per_hour, dt)
        created: List[Aircraft] = []

        while self._outbound_acc >= 1.0:
            self._outbound_acc -= 1.0

            a = self.make_outbound_aircraft(now)
            created.append(a)

            #TODO: sample_outbound_spawn_time Not implemented
            spawn_raw = self.stats.sample_outbound_spawn_time(int(now))
            self._pending_outbound.append((SimTime(int(spawn_raw)), a))

        # apply emergencies to outbound as well
        self._apply_emergencies_this_tick(created)


    # Pending flush
    def _flush_pending(self, now: SimTime) -> None:
        """
        Move pending aircraft with spawn_time <= now into the airport queues.
        """
        if self._pending_inbound:
            due, future = [], []
            for t, a in self._pending_inbound:
                (due if t <= now else future).append((t, a))
            self._pending_inbound = future
            for _, a in due:
                self.airport.handleInbound(a, now.time)

        if self._pending_outbound:
            due, future = [], []
            for t, a in self._pending_outbound:
                (due if t <= now else future).append((t, a))
            self._pending_outbound = future
            for _, a in due:
                self.airport.handleOutbound(a, now.time)


    def update_constraints(self, now: int, dt: int) -> None:
        """
        Placeholder:

        Typical responsibilities later:
          - burn fuel for holding aircraft; divert if below threshold
          - cancel takeoffs waiting too long
        """
        return


    def make_inbound_aircraft(self, scheduled_time_min: int) -> Aircraft:
        """
        Creates an inbound aircraft using SimulationParams for fuel bounds.
        This MUST match your Aircraft constructor.

        Current repo Aircraft ctor takes many args; you should simplify it.
        For now, this version assumes a minimal ctor:
            Aircraft(aircraft_id, flight_type, scheduledTime, fuelRemaining)
        """
        aircraft_id = f"I{self._next_in_id}"
        self._next_in_id += 1

        fuel = self._rng.randint(self.params.fuel_initial_min_min, self.params.fuel_initial_max_min)

        # Expected minimal constructor (recommended for your team)
        return Aircraft(aircraft_id, "INBOUND", scheduled_time_min, int(fuel),emergency=None)

    def make_outbound_aircraft(self, scheduled_time_min: int) -> Aircraft:
        aircraft_id = f"O{self._next_out_id}"
        self._next_out_id += 1

        # fuel can be 0 for outbound if your model doesn't track it
        return Aircraft(aircraft_id, "OUTBOUND", scheduled_time_min, 0, emergency=None)
