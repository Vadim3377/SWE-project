import random
import string
from dataclasses import dataclass
from typing import Optional
# from .SimulationEngine import EmergencyType
# Defined here to avoid circular import from SimulationEngine
from dataclasses import dataclass
from typing import Optional
import random
import string


@dataclass
class EmergencyType:
    """Represent the emergency state of an aircraft.

    An aircraft may have a mechanical failure, passenger illness,
    fuel emergency, or no emergency at all.
    """

    mechanical_failure: bool = False
    passenger_illness: bool = False
    fuel_emergency: bool = False


class Aircraft:
    """Represent an aircraft in the airport simulation.

    Each aircraft stores its identity, flight type, scheduling data,
    fuel state, optional emergency information, and generated flight
    metadata such as callsign, operator, origin, and destination.

    Inbound aircraft originate from a randomly generated airport and
    arrive at the simulated airport. Outbound aircraft depart from the
    simulated airport and are assigned a random destination airport.
    """

    def __init__(
        self,
        aircraft_id: str,
        flight_type: str,
        scheduledTime: int,
        fuelRemaining: int,
        *,
        emergency: Optional[EmergencyType] = None,
        altitude: int = 0,
        enteredHoldingAt: Optional[int] = None,
        joinedTakeoffQueueAt: Optional[int] = None,
    ):
        """Initialise an aircraft object.

        Parameters
        ----------
        aircraft_id : str
            Unique identifier for the aircraft.
        flight_type : str
            Type of flight, either ``INBOUND`` or ``OUTBOUND``.
        scheduledTime : int
            Scheduled arrival or departure time.
        fuelRemaining : int
            Initial amount of remaining fuel.
        emergency : Optional[EmergencyType], optional
            Emergency assigned to the aircraft, if any.
        altitude : int, optional
            Current aircraft altitude.
        enteredHoldingAt : Optional[int], optional
            Time the aircraft entered the holding queue.
        joinedTakeoffQueueAt : Optional[int], optional
            Time the aircraft joined the takeoff queue.
        """
        self.id = aircraft_id
        self.type = flight_type
        self.scheduledTime = int(scheduledTime)
        self.fuelRemaining = int(fuelRemaining)
        self.altitude = altitude
        self.emergency = emergency

        self.enteredHoldingAt = enteredHoldingAt
        self.joinedTakeoffQueueAt = joinedTakeoffQueueAt

        icao_code = [
            "Boeing ",
            "Airbus ",
            "RYANAIR ",
            "Speedbird ",
            "Emirates ",
            "EASY ",
            "Oceanic ",
            "Virgin ",
            "Delta ",
            "United ",
        ]
        self.callsign = f"{random.choice(icao_code)}{random.randint(100, 999)}"
        self.operator = (
            random.choice(string.ascii_uppercase)
            + random.choice(string.ascii_uppercase)
        )
        self.ground_speed = random.randint(300, 600)

        if self.type == "INBOUND":
            self.origin = self._rand_airport()
            self.destination = "SIMULATED_AIRPORT"
        else:
            self.origin = "SIMULATED_AIRPORT"
            self.destination = self._rand_airport()

    @staticmethod
    def _rand_airport() -> str:
        """Generate a random three-letter airport code."""
        return "".join(random.choice(string.ascii_uppercase) for _ in range(3))

    def isEmergency(self) -> bool:
        """Return whether the aircraft currently has an emergency."""
        e = self.emergency
        if e is None:
            return False
        return e.mechanical_failure or e.passenger_illness or e.fuel_emergency

    def consumeFuel(self, amount: int) -> None:
        """Reduce remaining fuel by the specified amount."""
        self.fuelRemaining = max(0, self.fuelRemaining - int(amount))

    def priority(self, time: int) -> int:
        """Return queue priority for the aircraft.

        Emergency aircraft have higher priority and return ``0``.
        Normal aircraft return ``1``.
        """
        return 0 if self.isEmergency() else 1

    def getFuel(self) -> int:
        """Return the amount of fuel remaining."""
        return self.fuelRemaining