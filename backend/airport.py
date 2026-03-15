from typing import List

#from .aircraft import aircraft
from .queues import HoldingQueue, TakeOffQueue
from .runway import Runway
from .SimulationEngine import SimTime
from .statistics import Statistics


"""
- The airport class utilises the runways and the two queues so that the aircraft objects can move between them accordingly
- It also records any statistics by using an object that is an instance of the Statistics class
- Its only attributes are the runways, the takeoff and holding queue and the statistics class object because the aircraft objects can only move between them accordingly in an aircraft
"""
class Airport:
    def __init__(self, runways: list[Runway], holding: HoldingQueue, takeoff: TakeOffQueue, stats: Statistics):
        self.runways = runways
        self.holding = holding
        self.takeoff = takeoff
        self.stats = stats

    """
    - This method below returns the runways for landing by looping through the list of runways and assigning 0 to any landing runways, 1 to any mixed runways and 2 to anything else
    - We then sort the list based on these assigned numbers so that the landing and mixed runways all end up at the start
    """
    def _runways_for_landing(self):
        # LANDING-only first, then MIXED
        return sorted(self.runways, key=lambda r: 0 if r.mode == "LANDING" else (1 if r.mode == "MIXED" else 2))

    """
    - This method below returns the runways for takeoff by looping through the list of runways and assigning 0 to any takeoff runways, 1 to any mixed runways and 2 to anything else
    - We then sort the list based on these assigned numbers so that the takeoff and mixed runways all end up at the start
    """
    def _runways_for_takeoff(self):
        # TAKEOFF-only first, then MIXED
        return sorted(self.runways, key=lambda r: 0 if r.mode == "TAKEOFF" else (1 if r.mode == "MIXED" else 2))

    """
    - This method below records the entry of an aircraft into the holding queue at a specific time
    - It also pushes the aircraft object into the holding queue
    """
    def handleInbound(self, aircraft, time: int):
        self.stats.record_holding_entry(aircraft, time)
        self.holding.enqueue(aircraft, time)

    """
    - This method below records the entry of an aircraft into the takeoff queue at a specific time
    - It also pushes the aircraft object into the takeoff queue
    """
    def handleOutbound(self, aircraft, time: int):
        self.stats.record_takeoff_enqueue(aircraft, time)
        self.takeoff.enqueue(aircraft, time)

    """
    - The method below just assigns as many inbound aircraft as possible to eligible available runways.
    """
    def assignLanding(self, time: SimTime) -> None:
        for runway in self.runways:
            if not (runway.isAvailable() and runway.canLand()):
                continue

            plane = self.holding.dequeue() # Takes a plane out of the holding queue
            if plane is None: return       # Checks if there's actually a plane. If there isn't, we return

            # The following lines of code below just assigns the plane to the runway that is available for landing. We also record data for the statistics class object at the end
            duration = 3
            runway.assign(plane, "LANDING", time, duration)
            runway.startTime = time                              # Needs to store Start Time 
            runway.duration = duration                           # Needs to store Duration
            runway.occupancy = "OCCUPIED"
            self.stats.record_landing(plane, time)
            self.stats.record_runway_busy(runway, duration)

    """
    - Description of method: Assigns as many outbound aircraft as possible to eligible available runways.
    """
    def assignTakeOff(self, time: SimTime) -> None:
        for runway in self.runways:
            if not (runway.isAvailable() and runway.canTakeOff()):
                continue

            plane = self.takeoff.dequeue()  # Takes a plane out of the takeoff queue
            if plane is None: return        # Checks if there's actually a plane. If there isn't, we return

            # The following lines of code below just assigns the plane to the runway that is available for takeoff. We also record data for the statistics class object at the end
            duration = 3
            runway.assign(plane, "TAKEOFF", time, duration)
            runway.startTime = time # Needs to store Start Time
            runway.duration = duration # Needs to store Duration
            runway.occupancy = "OCCUPIED"
            self.stats.record_takeoff(plane, time)
            self.stats.record_runway_busy(runway, duration)

    """
    - This method returns a list of all the avaiable runways for landing or for takeoff by iterating through the list and finding which ones are landing, takeoff or mixed
    """
    def getEligibleRunways(self, op: str) -> List[Runway]:
        if op == "LANDING":
            return [r for r in self.runways if r.mode in ("LANDING", "MIXED")]
        if op == "TAKEOFF":
            return [r for r in self.runways if r.mode in ("TAKEOFF", "MIXED")]
        return []
    
    """
    - This method updates the runways so that the runways whose time has passed can be freed for future aircraft to land in
    """   
    def updateRunways(self,time: SimTime) -> None:
        for runway in self.runways:
            if runway.occupiedUntil <= time and runway.occupancy == "OCCUPIED":
                runway.occupancy = "FREE"
                runway.occupiedUntil = 0
                runway.currentAircraft = None
                runway.currentOperation = None