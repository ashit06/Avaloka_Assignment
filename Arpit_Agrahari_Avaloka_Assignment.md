# Avaloka AI Intern Assignment: Data Structures & Systems Design

**Candidate:** Arpit Agrahari  
**Role:** AI / Multi-Agent Systems Intern  
**Company:** Avaloka (Guruvai Sciences)  
**Date:** October 21, 2026  
**GitHub Repository:** [https://github.com/ashit06/Avaloka_Assignment](https://github.com/ashit06/Avaloka_Assignment)

---

## Overview

This document presents my solutions and architectural analysis for the Avaloka SE / Multi-Agent Systems Intern take-home assignment. It contains:
1. **Problem 1 (LRU Cache):** Personal approach, complete Python code, and operational trace.
2. **Problem 2 (Event Scheduler):** Personal approach, interval conflict detection, room sizing with a min-heap, and runnable code.
3. **Final Discussion & Analysis:** Comprehensive answers to all four questions covering time/space complexity, data structure trade-offs, practical room assignment algorithms, and thread-safety considerations.

---

## Problem 1: LRU Cache Implementation

### My Approach

When you first look at an LRU Cache, the O(1) requirement for both `get` and `put` is the main constraint that dictates the entire design. 

A plain hash table (Python dictionary) gives you instant O(1) lookups by key. But dictionaries don't naturally maintain access recency in a way that lets you extract or update the oldest element without scanning. On the other hand, an array or Python list preserves order easily, but whenever you access or delete an element from the middle, you have to shift all subsequent elements over—costing O(n) time.

To get O(1) on both retrieval and eviction, I paired two complementary structures:
1. **A Hash Map (`dict`):** Maps each integer key directly to its corresponding `Node` object in memory. This gives us O(1) access to any cached entry without searching.
2. **A Doubly Linked List:** Maintains the exact recency order of the items. The most recently accessed node is placed right at the front (after the head sentinel), and the oldest, least recently used node rests at the back (before the tail sentinel).

Why did I specifically pick a **doubly linked list** rather than a singly linked list?
Deletion is the deciding factor. In a singly linked list, unlinking a node requires updating the `next` pointer of its *predecessor*. But unless you already have a pointer to that predecessor, you have to traverse the list from the beginning to find it, taking O(n) time. With a doubly linked list, every node holds a direct reference to both its predecessor (`node.prev`) and its successor (`node.next`). That means any node can extract itself in constant time with just four pointer reassignments:
```python
node.prev.next = node.next
node.next.prev = node.prev
```

To eliminate annoying boundary conditions, I introduced two **sentinel nodes** (`head` and `tail`). These dummy nodes hold no real data and are never removed. Because real entries always live strictly between `head` and `tail`, you never have to write special branches like `if self.head is None` or `if node == self.tail`. The code stays clean, concise, and safe from off-by-one pointer errors.

#### How `get(key)` works:
- Check if the key exists in the hash map. If not, return `-1`.
- If it does exist, grab the node reference.
- Detach the node from its current spot and splice it right behind the `head` sentinel (marking it as most recently used).
- Return `node.val`.

#### How `put(key, value)` works:
- If the key already exists in the cache: overwrite its value and move the node to the front.
- If the key is new:
  - Check if the cache is currently at capacity (`len(self.cache) >= self.capacity`).
  - If full, extract the node right before `tail` (the LRU entry) and delete its key from the hash map.
  - Create a fresh `Node(key, value)`.
  - Splice the new node right behind `head`.
  - Insert the key -> node mapping into the hash map.

Every single step involves only direct pointer updates and dictionary operations, guaranteeing true O(1) execution.

---

### Python Implementation

```python
class Node:
    """A node in the doubly linked list."""
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used Cache with O(1) get and put operations.
    Combines a hash map for lookups with a doubly linked list for recency.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Sentinel dummy nodes simplify list boundary updates
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Unlink an existing node from its current position in O(1)."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Insert a node directly after head sentinel (marks as most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_front(self, node: Node) -> None:
        """Promote an accessed node to the MRU position."""
        self._remove(node)
        self._add_to_front(node)

    def _pop_lru(self) -> Node:
        """Extract and return the least recently used node (before tail sentinel)."""
        lru_node = self.tail.prev
        self._remove(lru_node)
        return lru_node

    def get(self, key: int) -> int:
        """Fetch key value. Returns -1 if absent. Updates recency."""
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._move_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair. Evicts LRU item if at capacity."""
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                evicted = self._pop_lru()
                del self.cache[evicted.key]

            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
```

---

### Step-by-Step State Walkthrough

Here is a practical trace showing how the internal linked list and dictionary evolve as operations execute on a cache with `capacity = 3`:

```
1. cache = LRUCache(3)
   State: Head <-> Tail, dict: {}

2. cache.put(1, 10); cache.put(2, 20); cache.put(3, 30)
   State: Head <-> [3:30] <-> [2:20] <-> [1:10] <-> Tail
   Key 3 is most recently used (front), Key 1 is least recently used (back).

3. cache.get(2) -> returns 20
   Node 2 is extracted and spliced to the front.
   State: Head <-> [2:20] <-> [3:30] <-> [1:10] <-> Tail

4. cache.put(4, 40)
   Cache is at full capacity (3 entries). Key 1 is at the tail, so it gets evicted.
   Node 4 is linked at the front.
   State: Head <-> [4:40] <-> [2:20] <-> [3:30] <-> Tail

5. cache.get(1) -> returns -1
   Key 1 was evicted in step 4, so dictionary lookup returns -1 immediately.

6. cache.put(3, 300)
   Key 3 exists. Its value updates to 300 and it moves to the front.
   State: Head <-> [3:300] <-> [4:40] <-> [2:20] <-> Tail
```

---

## Problem 2: Event Scheduler

### My Approach

#### Part 1: `can_attend_all(events)`
The objective here is simple: determine whether a single person can attend every scheduled meeting without being in two places at once. 

If we compare every meeting against every other meeting, we end up with an O(n^2) nested loop. That is needlessly slow. The cleaner way is to **sort the events by start time**. Once sorted:
- The earliest meeting is first, followed chronologically by subsequent meetings.
- Any potential collision can only happen between consecutive meetings in the sorted list.
- We iterate through the list from index 1 to n - 1: if `curr_start < prev_end`, the next meeting begins before the previous meeting wraps up, which means there is a conflict. We return `False` immediately.
- The assignment specification notes: *"events ending and starting at the same time do not overlap (e.g., (9, 10) and (10, 11) is fine)."* That means `curr_start == prev_end` is totally acceptable. Only a strict inequality `curr_start < prev_end` is an actual clash.

#### Part 2: `min_rooms_required(events)`
Finding the minimum number of rooms needed is equivalent to answering: **what is the maximum number of concurrent meetings occurring at any single moment?**

I implemented this using the standard **Min-Heap (Priority Queue)** approach:
1. First, sort all meetings by start time so we process them in the exact order they take place.
2. Maintain a min-heap storing the `end_time` of each currently active meeting room. The root of the heap (`heap[0]`) always represents the room that will finish earliest.
3. For each incoming event `(start, end)`:
   - Check if the room at the top of the heap is free (`heap[0] <= start`).
   - If it is free, we can reuse that room! We pop the old end time from the heap.
   - If it is not free, all active rooms are still occupied, so we must allocate a new room.
   - We push the current event's `end` time into the heap.
4. After processing all events, the number of entries in the heap represents the peak number of simultaneous rooms needed.

This approach is elegant, runs in O(n log n) time, and naturally scales into assigning concrete room names (Room A, Room B, ...) for Discussion Question 3.

---

### Python Implementation

```python
import heapq
from typing import List, Tuple


def can_attend_all(events: List[Tuple[int, int]]) -> bool:
    """
    Check if one person can attend every event without overlapping.
    Adjacent events (end == start) do not overlap.
    """
    if len(events) <= 1:
        return True

    sorted_events = sorted(events, key=lambda e: (e[0], e[1]))

    for i in range(1, len(sorted_events)):
        prev_end = sorted_events[i - 1][1]
        curr_start = sorted_events[i][0]

        # Strict collision check: next starts before previous ends
        if curr_start < prev_end:
            return False

    return True


def min_rooms_required(events: List[Tuple[int, int]]) -> int:
    """
    Compute minimum conference rooms needed to host all events concurrently.
    Uses a min-heap of active room end times.
    """
    if not events:
        return 0

    sorted_events = sorted(events, key=lambda e: (e[0], e[1]))
    active_rooms = []  # min-heap storing end times of active meetings

    for start, end in sorted_events:
        # If the earliest ending meeting finished before or when this one begins,
        # reuse that room by popping its previous end time.
        if active_rooms and active_rooms[0] <= start:
            heapq.heappop(active_rooms)

        heapq.heappush(active_rooms, end)

    return len(active_rooms)


def min_rooms_with_assignment(events: List[Tuple[int, int]]) -> List[dict]:
    """
    Bonus / Future-proofing:
    Assigns concrete room identifiers ('Room A', 'Room B', ...) to each meeting
    by prioritizing room reuse via a min-heap.
    """
    if not events:
        return []

    indexed = sorted(enumerate(events), key=lambda x: (x[1][0], x[1][1]))
    free_rooms = []  # min-heap storing tuples: (end_time, room_name)
    room_count = 0
    assignments = [None] * len(events)

    for orig_idx, (start, end) in indexed:
        if free_rooms and free_rooms[0][0] <= start:
            _, room_name = heapq.heappop(free_rooms)
        else:
            room_count += 1
            room_name = f"Room {chr(ord('A') + (room_count - 1))}" if room_count <= 26 else f"Room {room_count}"

        heapq.heappush(free_rooms, (end, room_name))
        assignments[orig_idx] = {
            "event": (start, end),
            "room": room_name
        }

    return assignments
```

---

### Example Verification Runs

```
Test Case 1: Sequential back-to-back meetings
events = [(9, 10), (10, 11), (11, 12)]
- can_attend_all(events)      -> True   (no overlaps)
- min_rooms_required(events)  -> 1      (room is reused immediately at 10 and 11)

Test Case 2: Overlapping meetings
events = [(9, 11), (10, 12), (11, 13)]
- can_attend_all(events)      -> False  ((9, 11) overlaps with (10, 12))
- min_rooms_required(events)  -> 2      (peak concurrency is 2)

Test Case 3: Fully concurrent meetings
events = [(1, 5), (1, 5), (1, 5)]
- can_attend_all(events)      -> False
- min_rooms_required(events)  -> 3      (all 3 meetings require separate rooms)

Test Case 4: Edge cases
- can_attend_all([])          -> True
- min_rooms_required([])      -> 0
- can_attend_all([(4, 8)])    -> True
- min_rooms_required([(4, 8)])-> 1
```

---

## Final Discussion & Analysis

### 1. Time and Space Complexity Analysis

Here is the exact complexity breakdown for all implemented functions:

| Function / Operation | Time Complexity | Space Complexity | Explanation |
|---|---|---|---|
| `LRUCache.get(key)` | **O(1) average** | **O(1) auxiliary** | Dictionary lookup is O(1). Detaching and re-splicing the node in the doubly linked list involves exactly 4 pointer updates, regardless of cache size. |
| `LRUCache.put(key, value)` | **O(1) average** | **O(1) auxiliary** | Updating or inserting into the dictionary takes O(1). Evicting the tail's predecessor and adding a new node to the front takes constant pointer adjustments. |
| `LRUCache Total Memory` | — | **O(capacity)** | Stores at most `capacity` entries in the hash map and `capacity + 2` nodes in the doubly linked list (including sentinel head and tail). |
| `can_attend_all(events)` | **O(n log n)** | **O(n) auxiliary** | Sorting `n` intervals takes O(n log n) using Python's Timsort. The linear scan checks adjacent pairs in O(n) time. Total time: O(n log n). |
| `min_rooms_required(events)` | **O(n log n)** | **O(n) auxiliary** | Sorting events takes O(n log n). For each of the `n` events, we perform heap push and pop operations taking O(log k) where k is the number of active rooms (k <= n). Heap space is at most O(n). |
| `min_rooms_with_assignment` | **O(n log n)** | **O(n) auxiliary** | Identical heap dynamics as above, storing tuples `(end_time, room_name)` in the heap and producing the assigned schedule list. |

---

### 2. Architectural Trade-offs: Why a Hash Map + Doubly Linked List?

When designing an LRU Cache from scratch, why do we use this specific pairing instead of other standard data structures?

Each data structure on its own has a glaring weakness that makes O(1) LRU caching impossible:

| Data Structure | Lookup Time | Recency Tracking | Eviction / Splice | Why It Fails Alone |
|---|---|---|---|---|
| **Hash Map only** | O(1) | None | O(1) | Hash maps have no inherent access order. Finding the oldest key requires scanning all entries in O(n) time. |
| **Singly Linked List only** | O(n) | O(1) at tail | O(n) in middle | Finding a key requires walking from head (O(n)). Unlinking any node requires finding its predecessor, which also requires an O(n) traversal. |
| **Doubly Linked List only** | O(n) | O(1) | O(1) with pointer | Moving or evicting a node is O(1) if you already have the pointer, but finding *which* node holds a given key requires an O(n) sequential scan. |
| **Array / Dynamic List** | O(1) by index | O(1) append | O(n) deletion | Deleting from the middle or popping from the front forces memory shifts for all subsequent elements, costing O(n). |
| **Hash Map + DLL (Chosen)** | **O(1)** | **O(1)** | **O(1)** | **The sweet spot:** The hash map provides instant O(1) pointers to nodes, and the doubly linked list lets us detach and reposition nodes in O(1). |

#### Why Sentinel Nodes Matter:
Using dummy `head` and `tail` nodes consumes negligible memory (just two dummy objects) but removes every single conditional check for empty lists or edge boundaries. Every active data node is guaranteed to have valid `prev` and `next` pointers. This drastically reduces bug surface area, simplifies code maintenance, and prevents null-pointer runtime crashes.

#### What About Python's Built-in `collections.OrderedDict`?
Python's standard library provides `OrderedDict`, which internally implements this exact hash map + doubly linked list pattern and exposes `move_to_end(key)`. In a quick script or internal tool, using `OrderedDict` is completely reasonable. However, writing the doubly linked list and sentinel logic by hand demonstrates a solid understanding of memory management, pointer manipulation, and foundational systems design.

---

### 3. Future Proofing: Assigning Concrete Meeting Rooms

In a real office or scheduling platform, knowing that you need "2 rooms" is only half the battle. Employees need to know *which* room to walk into (e.g., "Room A" vs "Room B").

To solve this, I designed a **Greedy Room Allocation Algorithm using a Min-Heap**:

#### Algorithm Logic:
1. Sort all events chronologically by start time.
2. Maintain a min-heap storing tuples: `(end_time, room_identifier)`.
3. For each incoming event `(start, end)`:
   - Inspect the root of the heap: if `heap[0].end_time <= start`, that room is officially vacant! We pop it from the heap and reuse its name for the new meeting.
   - If `heap[0].end_time > start`, every currently assigned room is still busy. We open a brand new room (e.g., `Room C`, `Room D`).
   - Push `(end, assigned_room)` back onto the heap.

#### Why This Strategy Is Optimal:
- **Minimal Room Footprint:** It only opens a new room when every existing room is confirmed busy.
- **Maximized Room Reuse:** It greedily reclaims the earliest available room, keeping rooms compact and predictable.
- **Efficient Performance:** Running time is O(n log n) sorting + n * O(log k) heap operations, running effortlessly in milliseconds even for thousands of meetings.

#### Execution Trace Example:
Given the meetings `[(9, 11), (10, 12), (11, 13), (13, 15)]`:
```
1. Meeting (9, 11):
   - Heap is empty. Open Room A.
   - Heap state: [(11, 'Room A')]
   - Assigned: (9, 11) -> Room A

2. Meeting (10, 12):
   - Heap root ends at 11, but meeting starts at 10 (11 > 10). Room A is occupied.
   - Open Room B.
   - Heap state: [(11, 'Room A'), (12, 'Room B')]
   - Assigned: (10, 12) -> Room B

3. Meeting (11, 13):
   - Heap root is Room A, ending at 11. Meeting starts at 11 (11 <= 11). Room A is free!
   - Reuse Room A.
   - Heap state: [(12, 'Room B'), (13, 'Room A')]
   - Assigned: (11, 13) -> Room A

4. Meeting (13, 15):
   - Heap root is Room B, ending at 12 (12 <= 13). Room B is free!
   - Reuse Room B.
   - Heap state: [(13, 'Room A'), (15, 'Room B')]
   - Assigned: (13, 15) -> Room B
```
This produces a clean, deterministic room schedule without conflicts.

---

### 4. Concurrency: Making the LRU Cache Thread-Safe

In a multi-threaded server (such as an API service handling parallel requests), a standard LRU cache will suffer from data corruption and race conditions without concurrency control.

A subtle but critical detail about LRU caches: **`get(key)` is NOT a read-only operation!**  
Even though `get` only asks for a value, it mutates the doubly linked list under the hood by unlinking the accessed node and moving it to the front. If two threads call `get` concurrently on different keys, they could simultaneously reassign pointer references on the same neighboring nodes, corrupting the linked list and causing an infinite loop or segmentation fault.

Here are the standard approaches to make an LRU Cache thread-safe, ranked by complexity and throughput:

#### Approach 1: Coarse-Grained Mutex (Single Lock)
The simplest and most reliable solution is wrapping every public method with a mutual exclusion lock (`threading.Lock`):

```python
import threading


class ThreadSafeLRUCache:
    def __init__(self, capacity: int):
        self._cache = LRUCache(capacity)
        self._lock = threading.Lock()

    def get(self, key: int) -> int:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: int, value: int) -> None:
        with self._lock:
            self._cache.put(key, value)
```
- **Pros:** Incredibly simple to audit, guarantees 100% correctness, and preserves exact global LRU eviction order.
- **Cons:** Under high multi-threaded contention, all threads queue behind a single lock. Because `get()` requires exclusive write access to pointers, even pure read workloads serialize.

#### Approach 2: Key-Striped / Sharded Caching
For high-throughput systems, we can divide the keyspace across $M$ independent smaller LRU caches (shards), each with its own dedicated lock:
- `shard_id = hash(key) % M`
- Threads accessing different keys hit different locks and execute completely in parallel.
- **Trade-off:** Eviction is localized per shard rather than globally across all keys. However, for large uniform workloads, this trade-off is minor compared to the massive reduction in lock contention.

#### Approach 3: Read-Write Lock with Asynchronous Recency Buffer
To avoid locking the entire structure on every `get`:
- Use a Read-Write Lock (`RWLock`). `get()` acquires a shared read lock to read the node's value from the hash map.
- Instead of immediately splicing the linked list on every read, `get()` appends an access event `(key, timestamp)` to a lightweight, lock-free ring buffer or concurrent queue.
- A background worker thread (or a periodic batch flusher) drains the access buffer and updates the linked list pointers in batches under an exclusive write lock.
- **Trade-off:** Recency ordering is slightly delayed (eventually consistent), but read throughput scales dramatically.

#### Recommendation for Python Production Environments:
In standard CPython, the **Global Interpreter Lock (GIL)** already serializes Python bytecode execution across threads. Complex lock-free algorithms or fine-grained locking patterns in pure Python rarely yield performance improvements because the GIL overhead dominates. 

Therefore, **Approach 1 (Coarse Mutex)** is the industry-recommended starting point for Python applications. It is completely safe, easy to test, and introduces near-zero overhead for moderate workloads. If profiling later reveals high lock contention, transitioning to **Approach 2 (Sharded Cache)** provides immediate horizontal scaling without complicating the core cache data structures.

---

### Author Information
- **Candidate:** Arpit Agrahari
- **Role:** AI / Multi-Agent Systems Intern
- **Company:** Avaloka (Guruvai Sciences)
- **Repository:** [https://github.com/ashit06/Avaloka_Assignment](https://github.com/ashit06/Avaloka_Assignment)
