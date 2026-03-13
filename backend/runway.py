import random #Needed to assign length of runway and the bearings

"""
- The Runway class is created for the variable number of runways that our simulation may have. 
- Methods are available so we can check if we can land/takeoff on the runway, if the runway is available or if we want to assign an aircraft to a runway
- Initially, we set up the runways so that they are all free and currently have no aircraft
"""
class Runway:
    def __init__(self, runway_id, runway_mode) -> None:
        self.id = runway_id
        self.mode = runway_mode              # Represents runway capability 
        self.status = "AVAILABLE"
        self.occupancy = "FREE"
        self.currentOperation = None         # Can be "LANDING" or "TAKEOFF" or "MIXED"
        self.occupiedUntil = 0
        self.currentAircraft = None
        self.length = random.randint(2000,4000)
        self.bearing = random.randint(1,36)

    """
    - Method description: Checks if the runway is available by checking its occupancy and its status
    """
    def isAvailable(self):
        return self.occupancy == "FREE" and self.status == "AVAILABLE"

    """
    - Assigns an aircraft to a runway and changes the occupancy to being OCCUPIED
    - It also stores how long the aircraft will be occupying the runway for.
    """
    def assign(self, aircraft, operationMode="LANDING", time: int = 0, duration: int = 1) -> None:
        self.currentAircraft = aircraft
        self.currentOperation = operationMode
        self.occupiedUntil = time + duration
        self.occupancy = "OCCUPIED"

    """
    - The method below checks if a runway is available for a plane to land on it.
    """
    def canLand(self) -> bool:
        return self.currentAircraft == None and ((self.mode == "MIXED") or (self.mode == "LANDING"))

    """
    - The method below checks if a runway is available for a plane to take off from it.
    """
    def canTakeOff(self) -> bool:
        # Fixed typo: self.Mode -> self.mode
        return self.currentAircraft == None and ((self.mode == "MIXED") or (self.mode == "TAKEOFF"))

    """
    - Method description: Turns the bearing into a string with the correct bearing format for UI output.
    """
    def getBearingString(self) -> str:
        if self.bearing <= 9:
            return str("0" + str(self.bearing))
        else:
            return str(self.bearing)
