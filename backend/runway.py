import random


class Runway:
    """Represent a runway in the airport simulation.

    A runway stores its operational mode, availability, occupancy state,
    currently assigned aircraft, and additional metadata such as runway
    length and bearing.
    """

    def __init__(self, runway_id, runway_mode) -> None:
        """Initialise a runway.

        Parameters
        ----------
        runway_id
            Unique identifier for the runway.
        runway_mode
            Runway capability, typically ``LANDING``, ``TAKEOFF``, or ``MIXED``.
        """
        self.id = runway_id
        self.mode = runway_mode
        self.status = "AVAILABLE"
        self.occupancy = "FREE"
        self.currentOperation = None
        self.occupiedUntil = 0
        self.currentAircraft = None
        self.length = random.randint(2000, 4000)
        self.bearing = random.randint(1, 36)

    def isAvailable(self) -> bool:
        """Return whether the runway is currently available.

        Returns
        -------
        bool
            True if the runway is free and available for use, otherwise False.
        """
        return self.occupancy == "FREE" and self.status == "AVAILABLE"

    def assign(
        self,
        aircraft,
        operationMode="LANDING",
        time: int = 0,
        duration: int = 1,
    ) -> None:
        """Assign an aircraft to the runway.

        Parameters
        ----------
        aircraft
            Aircraft assigned to the runway.
        operationMode : str, optional
            Operation being performed, usually ``LANDING`` or ``TAKEOFF``.
        time : int, optional
            Simulation time at which the assignment begins.
        duration : int, optional
            Number of simulation time units for which the runway will remain occupied.
        """
        self.currentAircraft = aircraft
        self.currentOperation = operationMode
        self.occupiedUntil = time + duration
        self.occupancy = "OCCUPIED"

    def canLand(self) -> bool:
        """Return whether the runway can currently accept a landing.

        Returns
        -------
        bool
            True if the runway is unoccupied and supports landing operations,
            otherwise False.
        """
        return self.currentAircraft is None and (
            self.mode == "MIXED" or self.mode == "LANDING"
        )

    def canTakeOff(self) -> bool:
        """Return whether the runway can currently accept a takeoff.

        Returns
        -------
        bool
            True if the runway is unoccupied and supports takeoff operations,
            otherwise False.
        """
        return self.currentAircraft is None and (
            self.mode == "MIXED" or self.mode == "TAKEOFF"
        )

    def getBearingString(self) -> str:
        """Return the runway bearing as a two-digit string.

        Returns
        -------
        str
            Bearing formatted for display, for example ``03`` or ``27``.
        """
        if self.bearing <= 9:
            return "0" + str(self.bearing)
        return str(self.bearing)