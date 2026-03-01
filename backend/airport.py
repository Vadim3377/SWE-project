from typing import List

#from .aircraft import aircraft
from .queues import HoldingQueue, TakeOffQueue
from .runway import Runway
from .SimulationEngine import SimTime
from .statistics import Statistics


# Other classes are yet to be made but the airport class needs to inherit from them
class Airport:
    def __init__(self, runways: list[Runway], holding: HoldingQueue, takeoff: TakeOffQueue, stats: Statistics):
        self.runways = runways
        self.holding = holding
        self.takeoff = takeoff
        self.stats = stats

    def handleInbound(self, aircraft, now: int):
        self.stats.record_holding_entry(aircraft, now)
        self.holding.enqueue(aircraft, now)

    def handleOutbound(self, aircraft, now: int):
        self.stats.record_takeoff_enqueue(aircraft, now)
        self.takeoff.enqueue(aircraft, now)

    def assignLanding(self, time: SimTime) -> None:
        """
        Assign as many inbound aircraft as possible to eligible available runways.
        """
        for runway in self.runways:
            if not (runway.isAvailable() and runway.canLand()):
                continue

            plane = self.holding.dequeue()
            if plane is None: return

            duration = 3
            runway.assign(plane, "LANDING", time, duration)
            runway.startTime = time # Needs to store Start Time 
            runway.duration = duration # Needs to store Duration
            runway.occupancy = "OCCUPIED"
            self.stats.record_landing(plane, time)
            self.stats.record_runway_busy(runway, duration)

    def assignTakeOff(self, time: SimTime) -> None:
        """
        Assign as many outbound aircraft as possible to eligible available runways.
        """
        for runway in self.runways:
            if not (runway.isAvailable() and runway.canTakeOff()):
                continue

            plane = self.takeoff.dequeue()
            if plane is None: return  

            duration = 3
            runway.assign(plane, "TAKEOFF", time, duration)
            runway.startTime = time # Needs to store Start Time 
            runway.duration = duration # Needs to store Duration
            runway.occupancy = "OCCUPIED"
            self.stats.record_takeoff(plane, time)
            self.stats.record_runway_busy(runway, duration)

    
    def getEligibleRunways(self, mode: str) -> List[Runway]:
        eligible_list = []
        for runway in self.runways:
            if runway.mode == mode:
                eligible_list.append(runway)
        return eligible_list
        
    #This method updates the runways so that the runways whose time has passed can be freed
    def updateRunways(self,time: SimTime) -> None:
        for runway in self.runways:
            if runway.occupiedUntil <= time and runway.occupancy == "OCCUPIED":
                runway.occupancy = "FREE"
                runway.occupiedUntil = 0
                runway.currentAircraft = None
                runway.currentOperation = None