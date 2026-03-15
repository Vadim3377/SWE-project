# Airport Traffic Simulation System

## Project description

This project implements a **discrete-time airport traffic simulation system** that models aircraft arrivals, holding patterns, takeoff queues, runway allocation, fuel constraints, emergencies, diversions, cancellations, and operational statistics.

The system simulates airport traffic operations and allows users to observe how aircraft move through queues and runways under different operational conditions.

---

# 1. User Guide

This section explains how to **install and use the simulation program**.

---

# Installation
1. Navigate to the `dist` directory:

```
dist/
```

2. Make the executable runnable (if required):

```
chmod +x AirportSimulation
```

3. Run the program:

```
./AirportSimulation
```

No Python installation is required when using the executable.

---

# System Requirements

To run the executable version the system must support:

* Linux operating system
* x86-64 architecture
* graphical environment (X11 / desktop environment)

---

# Program Overview

The simulation models airport traffic operations including:

* Aircraft arrivals
* Aircraft departures
* Holding patterns
* Takeoff queues
* Runway assignment
* Aircraft fuel consumption
* Aircraft emergencies
* Flight diversions
* Flight cancellations
* Operational statistics

The simulation progresses in **discrete time steps ("ticks")**, where each tick represents a fixed number of minutes.

---

# Starting a Simulation

1. Launch the program.
2. Configure simulation parameters in the **settings panel**.
3. Press **Start Simulation**.

Aircraft will begin appearing automatically according to the configured traffic rates.

---

# Simulation Settings

Users can configure the following parameters before starting the simulation.

| Parameter               | Description                                            | Input Range Validation    |
| ----------------------- | ------------------------------------------------------ | ------------------------- |
| Runways                 | The number of runways in the simulation.               | 1 - 10                    |
| Inbound Rate            | Aircraft arrivals per hour                             | 1 - 45                    |
| Outbound Rate           | Aircraft departures per hour                           | 1 - 45                    |
| Tick Size               | Duration of one simulation tick / simulation speed     | 0 - 10 (not including 0)  |
| Fuel Limits             | Minimum and emergency fuel levels (in minutes)         | 20 - 30                   |
| Emergency Probabilities | Probability of mechanical failure or passenger illness | 0 - 50 (not including 0)  |
| Maximum Takeoff Wait    | Maximum time an aircraft can wait before cancellation  | 10 - 59                   |

Changing these parameters alters the behaviour of the airport traffic system.

---

# Viewing Aircraft

Users can select aircraft within the interface to view detailed information.

Aircraft information includes:

* Aircraft ID
* Flight type (Inbound / Outbound)
* Remaining fuel
* Emergency status
* Time entered queue
* Assigned runway

This allows monitoring aircraft conditions and priority levels.

---

# Viewing Runways

Each runway displays its current operational status.

Possible runway states include:

* **Available**
* **Landing**
* **Takeoff**
* **Blocked**

The interface shows which aircraft are currently using each runway.

---

# Blocking a Runway

Runways can be manually blocked.

Blocking a runway simulates:

* runway maintenance
* emergency closures
* accidents

When a runway is blocked:

* aircraft cannot be assigned to that runway
* queues may increase due to reduced capacity

Runways can be unblocked to restore normal operation.

---

# Queue Behaviour

The system maintains two queues.

---

## Holding Queue (Inbound Aircraft)

Inbound aircraft waiting to land are placed in the **holding queue**.

Priority rules:

1. Aircraft with emergencies are prioritised
2. Non-emergency aircraft follow FIFO order

Aircraft consume fuel while waiting.

If fuel levels drop too low, the aircraft may divert.

---

## Takeoff Queue (Outbound Aircraft)

Outbound aircraft waiting to depart are placed in the **takeoff queue**.

Queue behaviour:

* FIFO ordering
* aircraft depart when a runway becomes available

If aircraft remain in the queue too long, the flight may be cancelled.

---

# Aircraft Emergencies

Aircraft may experience two types of emergencies:

* Mechanical failure
* Passenger illness

Emergency aircraft receive priority in landing queues.

Fuel emergencies may also occur if fuel falls below the emergency threshold.

---

# Aircraft Diversions

If an inbound aircraft runs out of safe fuel reserves, it will divert to another airport.

Diversions occur when:

```
fuelRemaining <= minimumFuelThreshold
```

The aircraft is removed from the holding queue and the event is recorded in statistics.

---

# Flight Cancellations

Outbound aircraft may be cancelled if they remain in the takeoff queue for too long.

Cancellation condition:

```
waitingTime > max_takeoff_wait
```

Cancelled flights are removed from the simulation and recorded in statistics.

---

# Statistics

The simulation collects operational statistics such as:

* aircraft landed
* aircraft departed
* aircraft diverted
* flights cancelled
* queue sizes
* waiting times

Statistics are updated during each simulation tick.

---

# Saving Simulation Results

When the simulation stops, statistics are automatically saved to a CSV file.

Example file:

```
simulation_statistics.csv
```

The file contains statistics from the completed simulation.

---

# Viewing Previous Simulations

Previous simulations can be viewed:

1. In the **statistics window** inside the program
2. By opening the CSV statistics file

This allows comparison between different simulation runs.

---


# 2. Developer Guide
## Source Code Repository

The full source code for the Airport Traffic Simulation System is available on GitHub:

[https://github.com/Vadim3377/SWE-project](https://github.com/Vadim3377/SWE-project)

---
## Programming Language and Technologies

The backend of the Airport Traffic Simulation System is implemented in **Python 3**.

Python was chosen because it provides:

* clear and readable syntax
* strong support for modular architecture
* built-in data structures suitable for queue management
* libraries for randomness and statistical modelling

The simulation relies only on **standard Python libraries**, including:

| Library               | Purpose                                                              |
| --------------------- | -------------------------------------------------------------------- |
| `dataclasses`         | Used to define structured data objects such as the simulation engine |
| `collections.deque`   | Implements the FIFO takeoff queue                                    |
| `queue.PriorityQueue` | Implements the priority-based holding queue                          |
| `random`              | Generates probabilistic events such as emergencies                   |
| `typing`              | Provides type annotations for improved code clarity                  |

Using only built-in libraries ensures the backend remains lightweight and easy to run without external dependencies.

---

## Backend Architecture Overview

The backend is organised into multiple modules, each responsible for a specific aspect of the simulation.

The architecture separates the following responsibilities:

* **Simulation control**
* **Airport operations**
* **Aircraft representation**
* **Queue management**
* **Runway management**
* **Statistics and reporting**

This modular design improves maintainability and allows different components of the simulation to be developed independently.

The main backend modules are:

```text
SimulationEngine.py
airport.py
aircraft.py
queues.py
runway.py
statistics.py
report.py
SimulationParameters.py
```

Each module encapsulates a specific part of the simulation logic.

---

## Simulation Overview

The simulation models airport traffic using a **discrete-time system**.

Time advances in fixed increments called **ticks**, where each tick represents a configurable number of minutes.

During every tick the simulation performs the following steps:

1. update runway availability
2. generate new aircraft arrivals and departures
3. move aircraft from pending schedules into queues
4. apply operational constraints (fuel usage, emergencies, cancellations)
5. assign aircraft to available runways
6. update system statistics

This approach ensures that the system evolves in a controlled and predictable way while still allowing stochastic events such as emergencies and variable arrival times.


# System Architecture

The system is organised into modular components.

Typical structure:

```
backend/
    aircraft.py
    airport.py
    queues.py
    runway.py
    SimulationEngine.py
    SimulationParameters.py
    statistics.py
    report.py

frontend/
    (UI implementation)

dist/
    executable build
```

The architecture separates:

* simulation logic
* data structures
* statistics collection
* user interface

---

# Core Modules

---

# SimulationEngine

The **SimulationEngine** is the main controller of the simulation.

Responsibilities:

* advancing simulation time
* generating aircraft arrivals and departures
* scheduling aircraft events
* applying operational constraints
* assigning aircraft to runways
* updating statistics

The simulation runs using a **tick-based loop**.

Each tick performs the following operations:

1. update runway status
2. generate aircraft
3. move aircraft into queues
4. apply constraints
5. assign runways
6. update statistics

---

# Aircraft Module

`aircraft.py` defines the **Aircraft class**.

Aircraft objects store information such as:

* aircraft ID
* flight type
* fuel remaining
* emergency status
* queue entry time

Aircraft behaviour includes fuel consumption and emergency conditions.

---

# Airport Module

`airport.py` manages airport operations.

Responsibilities:

* managing holding and takeoff queues
* interacting with runways
* handling aircraft arrivals
* assigning aircraft to runways

This module acts as the central coordination layer between queues and runways.

---

# Runway Module

`runway.py` defines runway objects.

Runways manage:

* aircraft landing operations
* aircraft takeoff operations
* runway availability
* runway blocking status

Runways track aircraft occupancy and release themselves when operations complete.

---

# Queue System

Two queue structures are implemented.

---

## HoldingQueue

Used for inbound aircraft.

Data structure used:

```
PriorityQueue
```

Priority ordering:

```
(emergency_priority, arrival_order, aircraft)
```

Aircraft with emergencies receive higher priority.

FIFO ordering is preserved within equal priority levels.

---

## TakeOffQueue

Used for outbound aircraft.

Data structure used:

```
collections.deque
```

Queue ordering:

```
FIFO
```

Aircraft depart in the order they join the queue.

---

# Aircraft Scheduling

Aircraft generation uses **rate accumulation**.

Expected aircraft per tick:

```
rate_per_hour × (tick_size / 60)
```

Aircraft are generated when the accumulated value reaches 1.

This method produces consistent traffic flow.

---

# Randomised Arrival Timing

Aircraft spawn times are adjusted using a **normal distribution**.

Purpose:

* simulate realistic air traffic behaviour
* avoid perfectly uniform arrivals

Spawn times are sampled around the scheduled arrival time.

---

# Constraint Processing

Each simulation tick applies operational constraints.

---

## Fuel Consumption

Inbound aircraft consume fuel while waiting.

If fuel drops below the emergency threshold:

* aircraft becomes emergency priority

If fuel drops below the minimum threshold:

* aircraft diverts.

---

## Takeoff Queue Constraints

Outbound aircraft waiting longer than the allowed time are cancelled.

This prevents unbounded queue growth.

---

# Statistics Module

The statistics system records operational data including:

* queue sizes
* waiting times
* diversions
* cancellations
* aircraft movements

Statistics are updated during every simulation tick.

---

# Report Module

The report module exports simulation statistics to CSV files.

These files store results from previous simulations and allow later analysis.

---

# Data Persistence

Simulation results are stored in:

```
simulation_statistics.csv
```

This file contains:

* simulation configuration
* event counts
* queue metrics

---

# User Interface

Once ran, the program will first open to the simulation settings. These are parameters requested by the client and will configure the simulation. Each input is explained above, and these are all validated.

Upon pressing apply changes, the program immidately will start running. The two columns on the left of the screen represent the take-off and holding queues. The number of planes in each queue is also shown at the top.

Each widget in the queue represents a plane. Some basic information is shown, as well as a progress bar representing the time spent in the runway.

Clicking on a widget allows for more information to about a plane to be shown, as well as a diagram representing the plane in its current state. This can be between on a runway, in the air (in the holding queue) or on land (in take off queue). 

Information such as alitude and fuel levels are accurate. All planes in the holding queue are seperated by 1000, and fuel decreses every minute. Other data about planes such as origin, ground speed and callsign are randomised, but realistic.

If there is an emergency on a plane, it will also be shown in the widget.

All columns will become scrollable if the number of widgets becomes too large to fit on the screen.

On the other side of the display is the runways column. This shows information about all the runways in the simulation, and allows the user to configure them. 

The first button allows the user to close the runway (e.g. for maintainace, snow clearance etc.) The program clears any planes on the runway first. The second button allows the user to cycle between different operating modes: landing, take-off and mixed.

Clicking on a runway widget also allows a diagram of the runway to appear, depending on if it has a plane on it or not. The runway rotation depends on the randomised bearing for it. Additional information is also shown about the runway.

The bottom section shows the simulated time, and allows for further functionality. All the buttons can be clicked or accessed using a key press. 

Pause/Continue allows the user to pause and play the simulation. System settings brings up the same settings as before, and allows for live simulation updates.

View Statistics brings up a window which shows information collected during the simulation runtime. Previous runs are also stored and collected allowing for easy comparison between them.

Reset simulation clears the current simulation, allowing you to re-run the simulation with the same data.

Stop simulation saves the simulation run, and allows you to compare runs.
The user interface (UI) for the Airport Traffic Simulation System is a graphical dashboard built using **Python’s Tkinter library**. It serves as the primary way for users to interact with the simulation engine, providing real-time visual feedback, manual controls, and statistical reporting.


### Technical Implementation Details

* **Image Caching:** To prevent lag, the UI preloads assets (planes, runways, icons) into memory using the `PIL` (Pillow) library.
* **Smooth Updates:** A `smooth_update` loop runs at 60Hz (every 16ms) to ensure progress bars move fluidly, even if the simulation "tick" happens only once per second.
* **Thread-Like Behavior:** Uses `root.after()` loops to manage the simulation timing without freezing the interface.
