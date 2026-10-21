"""
Problem 2: Event Scheduler
Candidate: Arpit Agrahari
Role: AI / Multi-Agent Systems Intern

Overview:
---------
We need to solve two core scheduling challenges given a list of intervals (start, end):
  1. can_attend_all: Check whether a single person can attend every event with no overlap.
  2. min_rooms_required: Find the minimum meeting rooms needed to host all events concurrently.

Key Specification Rule:
Events ending and starting at the exact same timestamp (e.g. (9, 10) and (10, 11))
do NOT conflict. A person can step right into the next meeting, and a room is freed
at the exact moment the previous meeting wraps up.

Approach (in my own words):
---------------------------
Part 1 (can_attend_all):
Comparing every pair of meetings against each other takes O(n^2) comparisons. We can do
much better: sort all events by their start time first. Once they're in order, any potential
conflict has to show up between two consecutive events. If the current meeting begins before
the previous meeting finishes (curr_start < prev_end), there's a clash and we return False.
Because adjacent events (curr_start == prev_end) are valid, we use a strict less-than check (<).
This runs in O(n log n) time due to sorting, followed by a simple O(n) scan.

Part 2 (min_rooms_required):
To determine how many rooms are needed, we want to know the maximum number of overlapping
meetings happening at any single point in time.

The most intuitive and standard way to solve this is using a Min-Heap (priority queue) of
room end times:
  1. Sort all events by start time.
  2. Maintain a min-heap where each element is the end time of an in-progress meeting.
     The root of the heap always tells us the earliest moment a room will become available.
  3. For each event:
     - Check if the earliest finishing meeting in the heap has ended (heap[0] <= start).
     - If so, that room is now vacant, so we pop it from the heap (reusing the room).
     - If not, every currently used room is still occupied, so we have to allocate another room.
     - Push the current event's end time onto the heap.
  4. The maximum size of the heap (or the final size) represents the minimum number of rooms needed.

This runs in O(n log n) time to sort, plus n heap operations each taking O(log k) where k <= n.
It also sets us up perfectly to assign actual room names (Room A, Room B, etc.) for Question 3!
"""

import heapq
from typing import List, Tuple


def can_attend_all(events: List[Tuple[int, int]]) -> bool:
    """
    Check if one person can attend every event without any scheduling conflict.
    Adjacent events (end == start) do not overlap.
    """
    if len(events) <= 1:
        return True

    # Sort events by start time
    sorted_events = sorted(events, key=lambda e: (e[0], e[1]))

    # Compare each event with the one right before it
    for i in range(1, len(sorted_events)):
        prev_end = sorted_events[i - 1][1]
        curr_start = sorted_events[i][0]

        # Strict collision check (adjacent timestamps are allowed)
        if curr_start < prev_end:
            return False

    return True


def min_rooms_required(events: List[Tuple[int, int]]) -> int:
    """
    Calculate the minimum number of meeting rooms required to host all events.
    Uses a min-heap to track active room end times.
    """
    if not events:
        return 0

    # Sort by start time so we process meetings in chronological order
    sorted_events = sorted(events, key=lambda e: (e[0], e[1]))

    # Min-heap storing the end times of active meetings
    active_rooms = []

    for start, end in sorted_events:
        # If the earliest ending meeting finished before or when this one begins,
        # reuse that room by popping its previous end time.
        if active_rooms and active_rooms[0] <= start:
            heapq.heappop(active_rooms)

        # Allocate / occupy the room until this meeting ends
        heapq.heappush(active_rooms, end)

    # Number of elements in the heap is the number of active rooms required
    return len(active_rooms)


def min_rooms_with_assignment(events: List[Tuple[int, int]]) -> List[dict]:
    """
    Future-proofing extension:
    Allocates concrete room names ('Room A', 'Room B', ...) to each meeting
    by prioritizing room reuse via a min-heap of (end_time, room_name).
    """
    if not events:
        return []

    # Keep track of original index so we can output assignments in original order
    indexed = sorted(enumerate(events), key=lambda x: (x[1][0], x[1][1]))

    # Min-heap storing tuples: (end_time, room_identifier)
    free_rooms = []
    room_count = 0
    assignments = [None] * len(events)

    for orig_idx, (start, end) in indexed:
        # Check if any occupied room has freed up
        if free_rooms and free_rooms[0][0] <= start:
            _, room_name = heapq.heappop(free_rooms)
        else:
            # All existing rooms are busy: open a new room
            room_count += 1
            room_name = f"Room {chr(ord('A') + (room_count - 1))}" if room_count <= 26 else f"Room {room_count}"

        # Assign room and push updated busy time to heap
        heapq.heappush(free_rooms, (end, room_name))
        assignments[orig_idx] = {
            "event": (start, end),
            "room": room_name
        }

    return assignments


# --- Local Demonstration ---
if __name__ == "__main__":
    print("=== Testing Event Scheduler ===\n")

    # Test 1: Sequential back-to-back meetings (start == previous end)
    events1 = [(9, 10), (10, 11), (11, 12)]
    print(f"Test 1: {events1}")
    print(f"  can_attend_all:      {can_attend_all(events1)} (Expected: True)")
    print(f"  min_rooms_required:  {min_rooms_required(events1)} (Expected: 1)")

    # Test 2: Overlapping meetings
    events2 = [(9, 11), (10, 12), (11, 13)]
    print(f"\nTest 2: {events2}")
    print(f"  can_attend_all:      {can_attend_all(events2)} (Expected: False)")
    print(f"  min_rooms_required:  {min_rooms_required(events2)} (Expected: 2)")

    # Test 3: Completely concurrent meetings
    events3 = [(1, 5), (1, 5), (1, 5)]
    print(f"\nTest 3: {events3}")
    print(f"  can_attend_all:      {can_attend_all(events3)} (Expected: False)")
    print(f"  min_rooms_required:  {min_rooms_required(events3)} (Expected: 3)")

    # Test 4: Edge cases (empty and single meeting)
    print(f"\nTest 4: Empty list -> can_attend: {can_attend_all([])}, rooms: {min_rooms_required([])}")
    print(f"        Single [(4, 8)] -> can_attend: {can_attend_all([(4, 8)])}, rooms: {min_rooms_required([(4, 8)])}")

    # Test 5: Room Assignment Demonstration
    events5 = [(9, 11), (10, 12), (11, 13), (13, 15)]
    print(f"\nTest 5: Room Assignment for {events5}:")
    assigned = min_rooms_with_assignment(events5)
    for item in assigned:
        print(f"  Event {item['event']} -> Assigned to {item['room']}")

    print("\nAll event scheduler tests passed successfully.")
