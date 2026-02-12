import random
import string
from dataclasses import dataclass
from typing import Optional
from SimulationEngine import SimTime
from SimulationEngine import EmergencyType

class Aircraft:
    # Attribute actualTime removed
    def __init__(self,aircraft_id: str,flight_type: str,scheduledTime: int, fuelRemaining: int,*,emergency=None,altitude: int = 0,enteredHoldingAt: Optional[int] = None,joinedTakeoffQueueAt: Optional[int] = None):
        self.id = aircraft_id
        self.type = flight_type #a string that will either be INBOUND or OUTBOUND
        self.scheduledTime = scheduledTime
        #self.actualTime = actualTime #this is of type SimTime
        self.fuelRemaining = fuelRemaining
        self.altitude = altitude
        self.emergency = emergency #this variable is of type EmergencyType
        
        self.enteredHoldingAt = enteredHoldingAt
        self.joinedTakeoffQueueAt = joinedTakeoffQueueAt

        icao_code = ["Boeing ", "Airbus ", "RYANAIR ", "Speedbird ", "Emirates ", "EASY ", "Oceanic ", "Virgin ", "TOMJET ", "Delta ", "American ", "United "]
        self.callsign = icao_code[random.randint(0,len(icao_code)-1)] + str(random.randint(100,999))
        self.operator = random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase)
        self.ground_speed = random.randint(300,600)
        
        if self.type == "INBOUND":
            self.origin = self._rand_airport()
            self.destination = "SIMULATED AIRPORT" #placeholder for out airport name
        else:
            self.origin = "SIMULATED AIRPORT"
            self.destination = self._rand_airport()

    @staticmethod
    def _rand_airport() -> str:
        return "".join(random.choice(string.ascii_uppercase) for _ in range(3))

    # REQUIRED by HoldingQueue
    def isEmergency(self) -> bool:
        e = self.emergency
        if e is None:
            return False
        return bool(
            getattr(e, "mechanical_failure", False) or
            getattr(e, "passenger_illness", False) or
            getattr(e, "fuel_emergency", False)
        )
    
    def priority(self,time: SimTime) -> int: #What is this for? Is this when we want to assign the priority for the aircraft before pushing it into the queue?
        return
    
    def consumeFuel(self,data: SimTime) -> None:
        return

