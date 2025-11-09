#!/usr/bin/env python3
"""
memory_allocation.py

Simulate memory allocation (replacement) strategies:
    1. First Fit
    2. Best Fit
    3. Worst Fit
    4. Next Fit

Each algorithm decides where to place a process (of given size)
into available memory blocks (of different sizes).
"""

def first_fit(blocks, processes):
    """First Fit: allocate the first block that is big enough."""
    allocation = [-1] * len(processes)
    for i, process in enumerate(processes):
        for j, block in enumerate(blocks):
            if block >= process:
                allocation[i] = j
                blocks[j] -= process
                break
    return allocation

def best_fit(blocks, processes):
    """Best Fit: allocate the smallest block that fits."""
    allocation = [-1] * len(processes)
    for i, process in enumerate(processes):
        best_idx = -1
        for j, block in enumerate(blocks):
            if block >= process:
                if best_idx == -1 or block < blocks[best_idx]:
                    best_idx = j
        if best_idx != -1:
            allocation[i] = best_idx
            blocks[best_idx] -= process
    return allocation

def worst_fit(blocks, processes):
    """Worst Fit: allocate the largest block that fits."""
    allocation = [-1] * len(processes)
    for i, process in enumerate(processes):
        worst_idx = -1
        for j, block in enumerate(blocks):
            if block >= process:
                if worst_idx == -1 or block > blocks[worst_idx]:
                    worst_idx = j
        if worst_idx != -1:
            allocation[i] = worst_idx
            blocks[worst_idx] -= process
    return allocation

def next_fit(blocks, processes):
    """Next Fit: similar to First Fit, but starts searching from last allocated position."""
    allocation = [-1] * len(processes)
    j = 0  # start index for search
    n = len(blocks)
    for i, process in enumerate(processes):
        count = 0  # prevent infinite loop
        while count < n:
            if blocks[j] >= process:
                allocation[i] = j
                blocks[j] -= process
                break
            j = (j + 1) % n
            count += 1
    return allocation

def display_allocation(processes, allocation):
    """Print allocation table."""
    print("\nProcess No.\tProcess Size\tBlock No.")
    for i, process in enumerate(processes):
        if allocation[i] != -1:
            print(f"{i+1}\t\t{process}\t\t{allocation[i]+1}")
        else:
            print(f"{i+1}\t\t{process}\t\tNot Allocated")

def input_blocks_processes():
    """Helper to take user input."""
    n_blocks = int(input("Enter number of memory blocks: "))
    blocks = list(map(int, input("Enter block sizes: ").split()))
    if len(blocks) != n_blocks:
        print("Warning: count mismatch, adjusting automatically.")
        blocks = blocks[:n_blocks]

    n_processes = int(input("Enter number of processes: "))
    processes = list(map(int, input("Enter process sizes: ").split()))
    if len(processes) != n_processes:
        print("Warning: count mismatch, adjusting automatically.")
        processes = processes[:n_processes]

    return blocks, processes

def main_menu():
    """Menu-driven interface."""
    while True:
        print("\n====== Memory Allocation Strategies ======")
        print("1. First Fit")
        print("2. Best Fit")
        print("3. Worst Fit")
        print("4. Next Fit")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '5':
            print("Exiting...")
            break

        blocks, processes = input_blocks_processes()

        # Copy of blocks list for each algorithm (to avoid modifying same list)
        if choice == '1':
            allocation = first_fit(blocks[:], processes)
            print("\n--- FIRST FIT ---")
        elif choice == '2':
            allocation = best_fit(blocks[:], processes)
            print("\n--- BEST FIT ---")
        elif choice == '3':
            allocation = worst_fit(blocks[:], processes)
            print("\n--- WORST FIT ---")
        elif choice == '4':
            allocation = next_fit(blocks[:], processes)
            print("\n--- NEXT FIT ---")
        else:
            print("Invalid choice. Try again.")
            continue

        display_allocation(processes, allocation)

if __name__ == "__main__":
    main_menu()


"""
===============================================================================
📘 PROGRAM SUMMARY:
-------------------
This program simulates four memory allocation (replacement) strategies used in
Operating Systems for assigning processes to memory blocks:

1️⃣ First Fit:
   - Allocates the first available block that is large enough.

2️⃣ Best Fit:
   - Allocates the smallest block that is large enough to minimize waste.

3️⃣ Worst Fit:
   - Allocates the largest available block to avoid small leftover spaces.

4️⃣ Next Fit:
   - Similar to First Fit, but starts searching from where the last allocation ended.

===============================================================================
🧩 HOW TO RUN (macOS / Ubuntu / Windows):
----------------------------------------
1. Save this file as:  memory_allocation.py
2. Open a terminal (or Command Prompt on Windows).
3. Run:
       python3 memory_allocation.py
   (or just `python memory_allocation.py` if using Windows)
4. Choose the algorithm from the menu.
5. Enter:
   - Number of memory blocks (e.g., 5)
   - Block sizes (e.g., 100 500 200 300 600)
   - Number of processes (e.g., 4)
   - Process sizes (e.g., 212 417 112 426)
6. Observe how each process is allocated (or not) to memory blocks.

===============================================================================
🧮 EXAMPLE INPUT & OUTPUT:
-------------------
Enter your choice (1-5): 1
Enter number of memory blocks: 5
Enter block sizes: 100 500 200 300 600
Enter number of processes: 4
Enter process sizes: 212 417 112 426

--- FIRST FIT ---
Process No.     Process Size    Block No.
1               212             2
2               417             5
3               112             2
4               426             Not Allocated

===============================================================================
📗 WHAT TO EXPLAIN IN EXAM:
----------------------------
- Each algorithm decides where a process will be loaded into memory.
- "Fit" means how well a process size matches a memory block.
- Helps to demonstrate dynamic partition memory management.
===============================================================================
"""
