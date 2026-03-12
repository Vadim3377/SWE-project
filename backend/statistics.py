from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import random

SimTime = int

@dataclass
class Statistics:
    """
    Tracks the simulation metrics and handle random timing jitter for aircraft spawns.

    Records the queue sizes, delay times, diversions, and cancellations. Also serves 
    as the main random number generator for normal-distributed aircraft spawns.
    """
    # Configuration (set via configure_from_params)
    _arrival_stddev_min: int = 0
    _departure_stddev_min: int = 0
    _tick_size_min: int = 1
    _rng: random.Random = field(default_factory=random.Random, repr=False)

    # Queue Sizes
    max_holding_size: int = 0
    max_takeoff_size: int = 0
    max_takeoff_wait = 0
    holding_size_sum: int = 0
    takeoff_size_sum: int = 0
    snapshots: int = 0

    # Holding / Landing Metrics
    holding_time_sum: int = 0
    holding_count: int = 0

    # Takeoff Metrics
    takeoff_wait_sum: int = 0
    takeoff_count: int = 0

    # Arrival / Delay Metrics
    arrival_delay_sum: int = 0
    arrival_count: int = 0
    max_arrival_delay: SimTime = 0

    # Exceptions
    diversions: int = 0
    cancellations: int = 0

    # Runway Usage
    runway_busy_time: Dict[Any, int] = field(default_factory=dict)

    def configure_from_params(self, params: Any, seed: Optional[int] = None) -> None:
        """
        Extract statistical parameters and seed the RNG from the main simulation config.

        Parameters
        ----------
        params : Any
            The simulation parameters object containing stddev and tick size data.
        seed : int, optional
            A seed for the random number generator to ensure reproducible results.
        """
        self._arrival_stddev_min = int(getattr(params, "arrival_stddev_min", 0))
        self._departure_stddev_min = int(getattr(params, "departure_stddev_min", 0))
        self._tick_size_min = int(getattr(params, "tick_size_min", 1)) or 1

        if seed is not None:
            self._rng.seed(int(seed))

    def _round_to_tick(self, minutes: float) -> int:
        """
        Snap randomised times to the nearest discrete tick duration.

        Parameters
        ----------
        minutes : float
            The raw continuous time to format.

        Returns
        -------
        int
            The time rounded to the appropriate simulation tick resolution.
        """
        t = int(self._tick_size_min) or 1
        return int(round(minutes / t) * t)

    def sample_inbound_spawn_time(self, scheduled_time_min: int) -> int:
        """
        Apply normally-distributed jitter to an inbound flight's scheduled time.

        Parameters
        ----------
        scheduled_time_min : int
            The initial scheduled arrival time.

        Returns
        -------
        int
            The final calculated spawn time, constrained to be >= 0.
        """
        sigma = float(self._arrival_stddev_min)
        jitter = self._rng.gauss(0.0, sigma) if sigma > 0 else 0.0
        spawn = int(round(int(scheduled_time_min) + jitter))
        return max(0, spawn)

    def sample_outbound_spawn_time(self, scheduled_time_min: int) -> int:
        """
        Apply normally-distributed jitter to an outbound flight's scheduled time.

        Parameters
        ----------
        scheduled_time_min : int
            The initial scheduled departure time.

        Returns
        -------
        int
            The final calculated spawn time, constrained to be >= 0.
        """
        sigma = float(self._departure_stddev_min)
        jitter = self._rng.gauss(0.0, sigma) if sigma > 0 else 0.0
        spawn = int(round(int(scheduled_time_min) + jitter))
        return max(0, spawn)

    def snapshot_queues(self, holding_size: int, takeoff_size: int, time: int) -> None:
        """
        Record current queue sizes to calculate running maximums and averages.

        Parameters
        ----------
        holding_size : int
            The current number of aircraft in the holding queue.
        takeoff_size : int
            The current number of aircraft in the take-off queue.
        time : int
            The current simulation time in minutes.
        """
        self.snapshots += 1
        self.max_holding_size = max(self.max_holding_size, int(holding_size))
        self.max_takeoff_size = max(self.max_takeoff_size, int(takeoff_size))
        self.holding_size_sum += int(holding_size)
        self.takeoff_size_sum += int(takeoff_size)

    def record_holding_entry(self, aircraft: Any, time: SimTime) -> None:
        """
        Log the exact time an aircraft enters the holding pattern.

        Parameters
        ----------
        aircraft : Any
            The aircraft object entering the queue.
        time : SimTime
            The timestamp of entry.
        """
        # Always set; no need to guard with hasattr
        setattr(aircraft, "enteredHoldingAt", int(time))

    def record_landing(self, aircraft: Any, time: SimTime) -> None:
        """
        Compute and store delay and holding durations when an aircraft lands.

        Parameters
        ----------
        aircraft : Any
            The aircraft object that has landed.
        time : SimTime
            The simulation time at touchdown.
        """
        t = int(time)

        entered = getattr(aircraft, "enteredHoldingAt", None)
        if entered is not None:
            ht = max(0, t - int(entered))
            self.holding_time_sum += ht
            self.holding_count += 1

        sched = getattr(aircraft, "scheduledTime", None)
        if sched is not None:
            delay = max(0, t - int(sched))
            self.arrival_delay_sum += delay
            self.arrival_count += 1
            self.max_arrival_delay = max(self.max_arrival_delay, delay)

    def record_takeoff_enqueue(self, aircraft: Any, time: SimTime) -> None:
        """
        Log the exact time an aircraft joins the take-off queue.

        Parameters
        ----------
        aircraft : Any
            The aircraft object joining the queue.
        time : SimTime
            The timestamp of entry.
        """
        setattr(aircraft, "joinedTakeoffQueueAt", int(time))

    def record_takeoff(self, aircraft: Any, time: SimTime) -> None:
        """
        Compute and store the wait duration when an aircraft successfully takes off.

        Parameters
        ----------
        aircraft : Any
            The aircraft object that is departing.
        time : SimTime
            The simulation time at departure.
        """
        joined = getattr(aircraft, "joinedTakeoffQueueAt", None)
        if joined is None:
            return

        wait = max(0, int(time) - int(joined))
        self.takeoff_wait_sum += wait
        self.takeoff_count += 1

        self.max_takeoff_wait = max(self.max_takeoff_wait, wait)

    def record_diversion(self, aircraft: Any = None, time: SimTime = 0) -> None:
        """
        Increment the diversion counter for aircraft unable to land.
        
        Parameters
        ----------
        aircraft : Any, optional
            The aircraft being diverted.
        time : SimTime, optional
            The timestamp of the diversion.
        """
        self.diversions += 1

    def record_cancellation(self, aircraft: Any = None, time: SimTime = 0) -> None:
        """
        Increment the cancellation counter for aircraft waiting too long to take off.

        Parameters
        ----------
        aircraft : Any, optional
            The aircraft being cancelled.
        time : SimTime, optional
            The timestamp of the cancellation.
        """
        self.cancellations += 1

    def record_runway_busy(self, runway: Any, duration_min: int) -> None:
        """
        Accumulate active usage time for a specific runway.

        Parameters
        ----------
        runway : Any
            The runway being utilised.
        duration_min : int
            The operational duration to add to the runway's total busy time.
        """
        self.runway_busy_time[runway] = self.runway_busy_time.get(runway, 0) + int(duration_min)

    def report(self) -> Dict[str, float]:
        """
        Calculate final averages and package all metrics into a reporting dictionary.

        Returns
        -------
        Dict[str, float]
            A dictionary containing the calculated maximums, averages, and totals
            for rendering in the UI or exporting to a log file.
        """
        avg_holding_q = round((self.holding_size_sum / self.snapshots) if self.snapshots else 0.0)
        avg_takeoff_q = round((self.takeoff_size_sum / self.snapshots) if self.snapshots else 0.0)
        avg_hold_time = round((self.holding_time_sum / self.holding_count) if self.holding_count else 0.0)
        avg_takeoff_wait = round((self.takeoff_wait_sum / self.takeoff_count) if self.takeoff_count else 0.0)
        avg_arrival_delay = round((self.arrival_delay_sum / self.arrival_count) if self.arrival_count else 0.0)

        return {
            "maxHoldingQueue": float(self.max_holding_size),
            "avgHoldingQueue": float(avg_holding_q),
            "maxTakeoffQueue": float(self.max_takeoff_size),
            "avgTakeoffQueue": float(avg_takeoff_q),
            "avgHoldingTime": float(avg_hold_time),
            "avgTakeoffWait": float(avg_takeoff_wait),
            "maxTakeoffWait": float(self.max_takeoff_wait),
            "avgArrivalDelay": float(avg_arrival_delay),
            "maxArrivalDelay": float(self.max_arrival_delay),
            "diversions": float(self.diversions),
            "cancellations": float(self.cancellations),
        }