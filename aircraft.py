# This lets us know the flight type for the aircraft and to toggle the fligh type at will
class FlightType:
    def __init__(self, type):
        if type not in ["INBOUND","OUTBOUND"]:
            raise ValueError("Mode must be INBOUND or OUTBOUND")
        self.type = type
    
    def setType(self, newtype: str) -> None:
        self.type = newtype
    
    def getType(self) -> str:
        return self.type

class EmergencyType:
    def __init__(self,mechanical_failure: bool, passenger_illness: bool, fuel_amt: int):
        self.mechanical_failure = mechanical_failure
        self.passenger_illness = passenger_illness
        self.fuel_amt = fuel_amt
    
    def getmechfailure() -> bool:
        return
    
    def getpassengerillness() -> bool:
        return
    
    def getfuelamt() -> int:
        return

class Aircraft:
    def __init__(self, id: str, type: FlightType, scheduledTime: SimTime, actualTime: SimTime, state: AircraftState, fuelRemaining: SimTime, Emergency: EmergencyType, enteredHoldingAt: SimTime, joinedTakeoffQueueAt: Simtime):
        self.id = id
        self.type = type
        self.scheduledTime = scheduledTime
        self.actualTime = actualTime
        self.state = state
        self.fuelRemaining = fuelRemaining
        self.Emergency = Emergency
        self.enteredHoldingAt = enteredHoldingAt
        self.joinedTakeoffQueueAt = joinedTakeoffQueueAt

    def isEmergency() -> bool:
        return
    
    def priority(time: SimTime) -> int: #What is this for? Is this when we want to assign the priority for the aircraft before pushing it into the queue?
        return
    
    def consumeFuel(data: SimTime) -> None:
        return
    

# TODO:
# Implement SimTime; very crucial for the system but idk what it is or how to implement it