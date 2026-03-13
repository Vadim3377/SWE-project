import random
import string
from dataclasses import dataclass
from typing import Optional
# from .SimulationEngine import EmergencyType
# Defined here to avoid circular import from SimulationEngine

"""
This is the dataclass for the emergencies that an aircraft can have
We made them to be boolean because an aircraft can either have any one of these emergencies at a time or none at all
"""
@dataclass
class EmergencyType:
    mechanical_failure: bool = False
    passenger_illness: bool = False
    fuel_emergency: bool = False

"""
- The Aircraft class is built to contain information about an airplane object
- The aircraft type attribute can either be INBOUND or OUTBOUND
- EmergencyType is CREATED by SimulationEngine and injected here.
- The origin attribute of the aircraft depends on the flight type. if it's outbound, the origin is another randomly generated airport and if it's outbound, the origin is the airport itself 
"""
class Aircraft:

    def __init__(self, aircraft_id: str, flight_type: str, scheduledTime: int, fuelRemaining: int,*, emergency: Optional[EmergencyType] = None, altitude: int = 0, enteredHoldingAt: Optional[int] = None, joinedTakeoffQueueAt: Optional[int] = None):
        
        self.id = aircraft_id
        self.type = flight_type 
        self.scheduledTime = int(scheduledTime)
        self.fuelRemaining = int(fuelRemaining)
        self.altitude = altitude
        self.emergency = emergency #this variable is of type EmergencyType
        
        self.enteredHoldingAt = enteredHoldingAt
        self.joinedTakeoffQueueAt = joinedTakeoffQueueAt
        icao_code = [
            "Boeing ", "Airbus ", "RYANAIR ", "Speedbird ", "Emirates ",
            "EASY ", "Oceanic ", "Virgin ", "Delta ", "United "
        ]
        self.callsign = f"{random.choice(icao_code)}{random.randint(100, 999)}"
        self.operator = random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase)
        self.ground_speed = random.randint(300, 600)

        if self.type == "INBOUND":
            self.origin = self._rand_airport()
            self.destination = "SIMULATED_AIRPORT"
        else:
            self.origin = "SIMULATED_AIRPORT"
            self.destination = self._rand_airport()

    """
    - The method below is used to randomly generate 3 letters for airport codes for origin/destination
    - This is done by randomly selecting 3 ASCII characters 
    """
    @staticmethod
    def _rand_airport() -> str:
        return "".join(random.choice(string.ascii_uppercase) for _ in range(3))

    """
    - The method below checks if the aircraft has an emergency. If the emergency attribute is not declared, then there's no emergency so return false
    - If the emergency attribute is declared then return true
    """
    def isEmergency(self) -> bool:
        e = self.emergency
        if e is None:
            return False
        return e.mechanical_failure or e.passenger_illness or e.fuel_emergency 

    """
    - The following method below is called to decrement the remaining fuel by a certain amount for every tick for the aircraft.
    - This is needed so that the aircraft will actually be "burning" fuel as the simulation progresses
    """
    def consumeFuel(self, amount: int) -> None:
        self.fuelRemaining = max(0, self.fuelRemaining - int(amount))
    
    """
    - This method below checks if the aircraft should be assigned a priority by  checking if it has an emergency (using a method expplained above)
    - If there is an emergency, we return 0 so that when we add it to the holding queue, it will prioritise the aircraft with 0 in their tuple since it will be the lowest
    - Lower value means higher priority so that emergency aircraft must always come first.
    """
    def priority(self, time: int) -> int:
        return 0 if self.isEmergency() else 1

    """
    - This is a getter method which just returns the fuel remaining
    """
    def getFuel(self) -> int:
        return self.fuelRemaining