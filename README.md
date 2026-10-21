# Avaloka AI Intern Assignment: Data Structures & Systems Design

**Candidate:** Arpit Agrahari  
**Role:** AI / Multi-Agent Systems Intern  
**Company:** Avaloka (Guruvai Sciences)  
**Submission Date:** October 21, 2026  

---

## Overview

This repository contains my solutions and architectural analysis for the Avaloka take-home technical assignment. All code is written in pure Python 3 using standard library modules only.

| File | Description |
|---|---|
| [`lru_cache.py`](lru_cache.py) | Problem 1 — LRU Cache with O(1) get & put using a hash map + doubly linked list with sentinel nodes |
| [`event_scheduler.py`](event_scheduler.py) | Problem 2 — Event Scheduler with `can_attend_all()`, `min_rooms_required()` via min-heap, and bonus room assignment |
| [`Arpit_Agrahari_Avaloka_Assignment.md`](Arpit_Agrahari_Avaloka_Assignment.md) | Complete write-up covering personal approaches, code listings, complexity tables, trade-offs, and concurrency |

---

## How to Run

Clone the repository and run each script directly with Python:

```bash
# 1. Run Problem 1 (LRU Cache demo & tests)
python3 lru_cache.py

# 2. Run Problem 2 (Event Scheduler demo & tests)
python3 event_scheduler.py
```

Both scripts run self-contained demonstration suites and print clear step-by-step verification output to stdout.

---

## Technical Summary

### Problem 1: LRU Cache
- **Lookups:** O(1) average time via Python hash map (`dict`).
- **Recency Maintenance:** O(1) time via Doubly Linked List with permanent dummy `head` and `tail` sentinel nodes.
- **Eviction:** O(1) constant-time eviction of least recently used item when inserting past capacity.

### Problem 2: Event Scheduler
- **`can_attend_all(events)`:** Sorts intervals by start time in O(n log n) and scans adjacent pairs in O(n) to detect overlaps. Correctly allows adjacent meetings (`curr_start == prev_end`).
- **`min_rooms_required(events)`:** Sorts intervals and uses a min-heap of meeting end times to track concurrent room usage in O(n log n) time.
- **`min_rooms_with_assignment(events)`:** Extends min-heap logic to greedily reuse available rooms and assign specific room labels (`Room A`, `Room B`, ...).

### Final Discussion & Systems Analysis
1. **Time & Space Complexity:** Comprehensive analysis for all operations and helper methods.
2. **Data Structure Trade-Offs:** Direct comparison of Hash Map only, Singly Linked List, Doubly Linked List, and dynamic arrays.
3. **Future-Proofing Room Assignment:** Step-by-step min-heap room recycling algorithm with execution trace.
4. **Concurrency & Thread Safety:** Evaluation of coarse-grained mutex locking, key-sharded caching, and read-write locks with async batched recency buffers in CPython.
