import pytest

from backend.aircraft import Aircraft, EmergencyType

#Tests

#isEmergency

def test_isEmergency_no_emergency_returns_false():
    a = Aircraft("A1", "INBOUND", 10, 50)

    assert a.isEmergency() is False

def test_isEmergency_mechanical_failure_returns_true():
    e = EmergencyType(mechanical_failure=True)
    a = Aircraft("A2", "INBOUND", 10, 50, emergency=e)

    assert a.isEmergency() is True

def test_isEmergency_passenger_illness_returns_true():
    e = EmergencyType(passenger_illness=True)
    a = Aircraft("A3", "INBOUND", 10, 50, emergency=e)

    assert a.isEmergency() is True

def test_isEmergency_fuel_emergency_returns_true():
    e = EmergencyType(fuel_emergency=True)
    a = Aircraft("A4", "INBOUND", 10, 50, emergency=e)

    assert a.isEmergency() is True

def test_isEmergency_multiple_flags_returns_true():
    e = EmergencyType(mechanical_failure=True, passenger_illness=True, fuel_emergency=True)
    a = Aircraft("A5", "INBOUND", 10, 50, emergency=e)

    assert a.isEmergency() is True


#Fuel related functions

def test_consumeFuel_reduces_fuel_correctly():
    a = Aircraft("A6", "INBOUND", 10, 50)

    a.consumeFuel(12)

    assert a.getFuel() == 38

def test_consumeFuel_does_not_go_negative():
    a = Aircraft("A7", "INBOUND", 10, 5)

    a.consumeFuel(999)

    assert a.getFuel() == 0

def test_getFuel_returns_current_fuel():
    a = Aircraft("A8", "INBOUND", 10, 60)

    assert a.getFuel() == 60


#priority based on queue logic 0 is emergency 1 if other

def test_priority_normal_aircraft_returns_one():
    a = Aircraft("A9", "INBOUND", 10, 50)

    assert a.priority(time=0) == 1

def test_priority_emergency_aircraft_returns_zero():
    e = EmergencyType(mechanical_failure=True)
    a = Aircraft("A10", "INBOUND", 10, 50, emergency=e)

    assert a.priority(time=0) == 0


#origin and destination

def test_init_inbound_sets_destination_simulated_airport():
    a = Aircraft("A11", "INBOUND", 10, 50)

    assert a.destination == "SIMULATED_AIRPORT"
    assert a.origin != "SIMULATED_AIRPORT"

def test_init_outbound_sets_origin_simulated_airport():
    a = Aircraft("A12", "OUTBOUND", 10, 50)

    assert a.origin == "SIMULATED_AIRPORT"
    assert a.destination != "SIMULATED_AIRPORT"


#types check casting 

def test_scheduledTime_and_fuelRemaining_cast_to_int():
    a = Aircraft("A13", "INBOUND", "15", "40")

    assert isinstance(a.scheduledTime, int)
    assert isinstance(a.fuelRemaining, int)
    assert a.scheduledTime == 15
    assert a.fuelRemaining == 40