class RunwayMode:
    def __init__(self, mode):
        if mode not in ["L","T"]:
            raise ValueError("Mode must be L or T")
        self.mode = mode
    
    def setMode(self, newMode: str) -> None:
        self.mode = newMode
    
    def getMode(self) -> str:
        return self.mode

# Other classes are yet to be made but the airport class needs to inherit from them
class Airport(Runway, Holding, Takeoff):                                   #Not implemented by my side but we need to inherit the properties from these classes
    def __init__(self, runways: List[Runway], holding, takeoff):
        self.runways = runways                                             #runways is a list of runway objects, where a runway object is just an instance of the runway class
        super().__init__(holding = holding_items, takeoff = takeoff_items) #Will use MRO to obtain vaues, make sure variable names are unique

    def assignLanding() -> None: 
        return
    
    def assigntakeoff() -> None:
        return
    
    def getEligibleRunways(mode: RunwayMode) -> List[Runway]:
        return
    
    def updateRunways(time: SimTime) -> None:
        return