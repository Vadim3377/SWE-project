# simulation_params.py
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationParams:
    """
    Data class representing the configurable parameters for the simulation.

    This class holds all user-defined and default settings required to run
    the airport simulation, including flow rates, runtime bounds, stochastic 
    variations, and emergency probability weights.

    Parameters
    ----------
    num_runways : int
        The total number of runways available at the airport.
    inbound_rate_per_hour : float
        The expected average number of arriving aircraft per hour.
    outbound_rate_per_hour : float
        The expected average number of departing aircraft per hour.
    arrival_stddev_min : int, optional
        Standard deviation for arrival time jitter in minutes. Default is 5.
    departure_stddev_min : int, optional
        Standard deviation for departure time jitter in minutes. Default is 5.
    max_takeoff_wait_min : int, optional
        Maximum allowed waiting time in the takeoff queue before an aircraft is cancelled. Default is 30.
    fuel_min_min : int, optional
        Absolute minimum fuel threshold (in minutes) before an aircraft is diverted. Default is 10.
    fuel_initial_min_min : int, optional
        Lower bound for the random initial fuel assigned to a spawned aircraft. Default is 20.
    fuel_initial_max_min : int, optional
        Upper bound for the random initial fuel assigned to a spawned aircraft. Default is 60.
    p_mechanical_failure : float, optional
        Probability weight for generating a mechanical failure emergency. Default is 0.05.
    p_passenger_illness : float, optional
        Probability weight for generating a passenger illness emergency. Default is 0.05.
    tick_size_min : int, optional
        The length of a single simulation tick in minutes. Default is 1.
    fuel_emergency_min : int, optional
        Fuel threshold (in minutes) at which an aircraft declares a fuel emergency. Default is 15.
    """
    num_runways: int
    inbound_rate_per_hour: float
    outbound_rate_per_hour: float

    # Stochastic assumptions (minutes)
    arrival_stddev_min: int = 5
    departure_stddev_min: int = 5

    # Constraints (minutes)
    max_takeoff_wait_min: int = 30
    fuel_min_min: int = 10
    fuel_initial_min_min: int = 20
    fuel_initial_max_min: int = 60

    # Distribution of emergency types (weights)
    p_mechanical_failure: float = 0.05
    p_passenger_illness: float = 0.05

    # Engine timing
    tick_size_min: int = 1  # 1-minute discrete tick
    fuel_emergency_min: int = 15


    def validate(self) -> None:
        """
        Validate the current simulation parameters to ensure they are within operational bounds.

        Raises
        ------
        ValueError
            If any parameters fall outside their permitted ranges (e.g., negative flow rates,
            invalid probabilities, or illogical fuel boundaries).
        """
        if not (1 <= self.num_runways <= 10):
            raise ValueError("num_runways must be in [1, 10].")

        if self.inbound_rate_per_hour < 0:
            raise ValueError("inbound_rate_per_hour must be >= 0.")
        if self.outbound_rate_per_hour < 0:
            raise ValueError("outbound_rate_per_hour must be >= 0.")

        if self.tick_size_min <= 0:
            raise ValueError("tick_size_min must be > 0.")

        # Allow 0 to disable noise
        if self.arrival_stddev_min < 0 or self.departure_stddev_min < 0:
            raise ValueError("stddev minutes must be >= 0.")

        if self.max_takeoff_wait_min <= 0:
            raise ValueError("max_takeoff_wait_min must be > 0.")

        if self.fuel_initial_min_min < 0 or self.fuel_initial_max_min < 0:
            raise ValueError("fuel initial bounds must be non-negative.")
        if self.fuel_initial_min_min > self.fuel_initial_max_min:
            raise ValueError("fuel_initial_min_min must be <= fuel_initial_max_min.")
        if self.fuel_min_min >= self.fuel_initial_min_min:
            raise ValueError("fuel_min_min must be < fuel_initial_min_min.")

        # Ensure the combined probability of all emergency types doesn't exceed 100%
        total_p = self.p_mechanical_failure + self.p_passenger_illness
        
        if total_p > 1.0 + 1e-9:
            raise ValueError(f"Total emergency probability ({total_p:.2f}) cannot exceed 1.0.")
            
        if any(p < 0 for p in [self.p_mechanical_failure, self.p_passenger_illness]):
            raise ValueError("Emergency probabilities cannot be negative.")