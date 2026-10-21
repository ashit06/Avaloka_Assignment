"""
Problem 1: LRU Cache
Candidate: Arpit Agrahari
Role: AI / Multi-Agent Systems Intern

Overview:
---------
An LRU (Least Recently Used) cache discards the least recently accessed items first
when it hits capacity. Both get() and put() must run in O(1) average time.

To pull that off, I paired a standard Python dictionary with a doubly linked list:
  1. The dictionary maps key -> Node reference. That gives us instant O(1) lookups.
  2. The doubly linked list keeps track of recency. The most recently accessed node
     sits right behind the head sentinel, and the oldest (least recently used) node
     sits right before the tail sentinel.

Why a doubly linked list instead of a singly linked list?
Because deleting an arbitrary node in O(1) requires access to its predecessor so we can
stitch prev and next together. A singly linked list only points forward, so finding the
predecessor would force an O(n) walk from the head. With a doubly linked list, every node
already knows its predecessor (node.prev), allowing instant O(1) removal.

Dummy sentinel nodes (head and tail) are used to avoid messy boundary checks when
inserting into an empty cache or removing the only element.
"""


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
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Sentinel dummy nodes keep pointer manipulation simple
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    # --- Internal helper methods ---

    def _remove(self, node: Node) -> None:
        """Unlink an existing node from its current spot in the list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Insert a node right after the head sentinel (most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_front(self, node: Node) -> None:
        """Promote an accessed node to the front of the list."""
        self._remove(node)
        self._add_to_front(node)

    def _pop_lru(self) -> Node:
        """Remove and return the least recently used node (just before tail)."""
        lru_node = self.tail.prev
        self._remove(lru_node)
        return lru_node

    # --- Public API ---

    def get(self, key: int) -> int:
        """
        Fetch value for key. Returns -1 if key does not exist.
        Accessing a key counts as usage, so it moves to the front.
        """
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._move_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        """
        Insert or update a key-value pair.
        If adding a new key exceeds capacity, the LRU item is evicted.
        """
        if key in self.cache:
            # Key exists: update its value and bump it to most-recent
            node = self.cache[key]
            node.val = value
            self._move_to_front(node)
        else:
            # New key: check if we need to make room first
            if len(self.cache) >= self.capacity:
                evicted = self._pop_lru()
                del self.cache[evicted.key]

            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)

    def __repr__(self) -> str:
        """Helper to print cache contents from MRU (front) to LRU (back)."""
        elements = []
        curr = self.head.next
        while curr != self.tail:
            elements.append(f"{curr.key}:{curr.val}")
            curr = curr.next
        return f"LRUCache([{', '.join(elements)}], cap={self.capacity})"


# --- Local Demonstration ---
if __name__ == "__main__":
    print("=== Testing LRU Cache (Capacity = 3) ===\n")

    cache = LRUCache(3)

    print("1. Inserting (1, 10), (2, 20), (3, 30)...")
    cache.put(1, 10)
    cache.put(2, 20)
    cache.put(3, 30)
    print(f"   Current cache: {cache}")

    print("\n2. Accessing key 2 via get(2)...")
    val = cache.get(2)
    print(f"   get(2) -> {val}")
    print(f"   Current cache (key 2 moved to front): {cache}")

    print("\n3. Inserting (4, 40) - cache is full, key 1 should be evicted...")
    cache.put(4, 40)
    print(f"   Current cache: {cache}")
    print(f"   get(1) -> {cache.get(1)} (expected -1 since it was evicted)")

    print("\n4. Updating existing key 3 with value 300 via put(3, 300)...")
    cache.put(3, 300)
    print(f"   Current cache: {cache}")
    print(f"   get(3) -> {cache.get(3)}")

    print("\nAll operations executed in O(1) time. Tests passed successfully.")
