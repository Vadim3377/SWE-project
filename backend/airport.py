from typing import List

from Queues import HoldingQueue, TakeOffQueue
from runway import Runway
from SimulationEngine import SimTime


# Other classes are yet to be made but the airport class needs to inherit from them
class Airport:
    def __init__(self, runways: list[Runway], holding: HoldingQueue, takeoff: TakeOffQueue):
        self.runways = runways
        self.holding = holding
        self.takeoff = takeoff

    def handleInbound(self, aircraft, now: int):
        self.holding.enqueue(aircraft, now)

    def handleOutbound(self, aircraft, now: int):
        self.takeoff.enqueue(aircraft, now)

    def assignLanding(time: SimTime, self) -> None:
        return
    
    def assignTakeOff(time: SimTime, self) -> None:
        return
    
    def getEligibleRunways(self, mode: str) -> List[Runway]:
        return
    
    def updateRunways(time: SimTime) -> None:
        return