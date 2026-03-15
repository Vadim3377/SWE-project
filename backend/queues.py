from .aircraft import Aircraft
from collections import deque
from queue import PriorityQueue


class HoldingQueue:
    """Priority queue used for inbound aircraft waiting to land.

    Aircraft are prioritised based on emergency status. Emergency aircraft
    are placed before non-emergency aircraft. Within the same priority level,
    aircraft follow FIFO ordering using an arrival counter.
    """

    def __init__(self):
        """Initialise an empty holding queue."""
        self.items = PriorityQueue()
        self.arrival_order = 0
        self.orderingRule = "Emergency-first"

    def __len__(self):
        """Return the number of aircraft in the queue."""
        return self.size()

    def enqueue(self, a: Aircraft, time: int) -> None:
        """Add an aircraft to the holding queue.

        Parameters
        ----------
        a : Aircraft
            Aircraft entering the holding queue.
        time : int
            Simulation time when the aircraft entered the queue.
        """
        if a.isEmergency():
            emergency_priority = 0
        else:
            emergency_priority = 1

        self.items.put((emergency_priority, self.arrival_order, a))
        self.arrival_order += 1

        a.enteredHoldingAt = time
        a.altitude = (self.size() + 1) * 1000

    def enqueue_with_order(self, a: Aircraft, time: int, order: int) -> None:
        """Insert an aircraft with an existing arrival order.

        This method is used when re-adding aircraft to preserve the
        original ordering.

        Parameters
        ----------
        a : Aircraft
            Aircraft to enqueue.
        time : int
            Time the aircraft entered the holding queue.
        order : int
            Original queue ordering value.
        """
        if a.isEmergency():
            emergency_priority = 0
        else:
            emergency_priority = 1

        self.items.put((emergency_priority, order, a))
        a.enteredHoldingAt = time

    def dequeue_with_order(self):
        """Remove and return the next aircraft with its queue metadata.

        Returns
        -------
        tuple | None
            Tuple of (priority, order, aircraft) or None if queue empty.
        """
        if self.items.empty():
            return None
        emergency_priority, order, aircraft = self.items.get()
        return emergency_priority, order, aircraft

    def dequeue(self) -> Aircraft | None:
        """Remove and return the next aircraft in the queue.

        Returns
        -------
        Aircraft | None
            The next aircraft or None if the queue is empty.
        """
        if self.items.empty():
            return None

        _, _, aircraft_obj = self.items.get()
        return aircraft_obj

    def peek(self) -> Aircraft | None:
        """Return the next aircraft without removing it."""
        if self.items.empty():
            return None
        return self.items.queue[0][2]

    def size(self) -> int:
        """Return the number of aircraft in the holding queue."""
        return self.items.qsize()

    def to_list(self):
        """Return a list snapshot of the queue for UI or debugging."""
        return [t[2] for t in list(self.items.queue)]


class TakeOffQueue:
    """FIFO queue used for outbound aircraft waiting to depart."""

    def __init__(self):
        """Initialise an empty takeoff queue."""
        self.items = deque()
        self.orderingRule = "FIFO Only"

    def __len__(self):
        """Return the number of aircraft in the queue."""
        return self.size()

    def enqueue(self, a: Aircraft, time: int) -> None:
        """Add an aircraft to the takeoff queue.

        Parameters
        ----------
        a : Aircraft
            Aircraft entering the queue.
        time : int
            Simulation time when the aircraft joined the queue.
        """
        self.items.append(a)
        a.joinedTakeoffQueueAt = time

    def dequeue(self) -> Aircraft | None:
        """Remove and return the first aircraft in the queue."""
        if self.isEmpty():
            return None
        return self.items.popleft()

    def peek(self) -> Aircraft | None:
        """Return the next aircraft without removing it."""
        if self.isEmpty():
            return None
        return self.items[0]

    def size(self) -> int:
        """Return the number of aircraft in the queue."""
        return len(self.items)

    def isEmpty(self) -> bool:
        """Return True if the queue contains no aircraft."""
        return not self.items

    def to_list(self):
        """Return a list snapshot of the queue for UI or debugging."""
        return list(self.items)

