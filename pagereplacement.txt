#!/usr/bin/env python3
"""
page_replacement_menu.py

Menu-driven program that implements three page-replacement algorithms:
1. FIFO (First-In First-Out)
2. LRU  (Least Recently Used)
3. Optimal (Belady's optimal algorithm)

For each algorithm the program:
 - reads number of pages and page sequence from user
 - reads frame capacity
 - processes the sequence, printing 'H' (hit) or 'F' (fault) for each request
 - stores and prints the frames' states step-by-step (table)
 - prints total hits, faults and hit/fault ratios
"""

def input_pages():
    """Prompt user for number of pages and then the page sequence."""
    while True:
        try:
            n = int(input("Enter the number of pages you want to enter: ").strip())
            if n <= 0:
                print("Number of pages must be positive.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer for number of pages.")
    pages = []
    print("Enter the page numbers (space or newline separated): ")
    while len(pages) < n:
        try:
            parts = input().strip().split()
            for p in parts:
                if len(pages) < n:
                    pages.append(int(p))
        except ValueError:
            print("Invalid input. Enter integers only.")
    return pages

def input_capacity():
    """Prompt user for frame capacity."""
    while True:
        try:
            cap = int(input("Enter the capacity of frame: ").strip())
            if cap <= 0:
                print("Capacity must be a positive integer.")
                continue
            return cap
        except ValueError:
            print("Please enter a valid integer for capacity.")

# ---------------- FIFO ----------------
def fifo(pages, capacity):
    """FIFO page replacement algorithm."""
    noofpages = len(pages)
    frame = [-1] * capacity
    table = [[-1] * capacity for _ in range(noofpages)]
    index = 0
    hit = 0
    fault = 0

    print("\nFIFO Processing:")
    print("----------------------------------------------------------------------")
    for i, page in enumerate(pages):
        search = -1
        for j in range(capacity):
            if frame[j] == page:
                search = j
                hit += 1
                print(f"{'H':>4}", end='')
                break

        if search == -1:
            frame[index] = page
            fault += 1
            print(f"{'F':>4}", end='')
            index = (index + 1) % capacity

        table[i][:] = frame[:]

    print("\n----------------------------------------------------------------------")
    for r in range(capacity):
        for c in range(noofpages):
            print(f"{table[c][r]:3d} ", end='')
        print()
    print("----------------------------------------------------------------------")
    hit_ratio = (hit / noofpages) * 100
    fault_ratio = (fault / noofpages) * 100
    print(f"Page Fault: {fault}\nPage Hit: {hit}")
    print(f"Hit Ratio:{hit_ratio:.2f}% \nFault Ratio:{fault_ratio:.2f}%\n")

# ---------------- LRU ----------------
def lru(pages, capacity):
    """LRU page replacement algorithm."""
    noofpages = len(pages)
    frame = [-1] * capacity
    table = [[-1] * capacity for _ in range(noofpages)]
    recency = []
    hit = 0
    fault = 0
    index = 0
    is_full = False

    print("\nLRU Processing:")
    print("----------------------------------------------------------------------")
    for i, page in enumerate(pages):
        if page in recency:
            recency.remove(page)
        recency.append(page)

        search = -1
        for j in range(capacity):
            if frame[j] == page:
                search = j
                hit += 1
                print(f"{'H':>4}", end='')
                break

        if search == -1:
            if is_full:
                min_loc = None
                min_recency_idx = len(recency) + 1
                for j in range(capacity):
                    if frame[j] in recency:
                        idx_in_rec = recency.index(frame[j])
                        if idx_in_rec < min_recency_idx:
                            min_recency_idx = idx_in_rec
                            min_loc = j
                if min_loc is not None:
                    index = min_loc

            frame[index] = page
            fault += 1
            print(f"{'F':>4}", end='')
            index += 1
            if index == capacity:
                index = 0
                is_full = True

        table[i][:] = frame[:]

    print("\n----------------------------------------------------------------------")
    for r in range(capacity):
        for c in range(noofpages):
            print(f"{table[c][r]:3d} ", end='')
        print()
    print("----------------------------------------------------------------------")
    hit_ratio = (hit / noofpages) * 100
    fault_ratio = (fault / noofpages) * 100
    print(f"Page Fault: {fault}\nPage Hit: {hit}")
    print(f"Hit Ratio:{hit_ratio:.2f}% \nFault Ratio:{fault_ratio:.2f}%\n")

# ---------------- Optimal ----------------
def optimal(pages, capacity):
    """Optimal page replacement algorithm."""
    noofpages = len(pages)
    frame = [-1] * capacity
    table = [[-1] * capacity for _ in range(noofpages)]
    hit = 0
    fault = 0

    print("\nOptimal Processing:")
    print("------------------------------------------------------")
    for i, page in enumerate(pages):
        found = False
        for j in range(capacity):
            if frame[j] == page:
                found = True
                hit += 1
                print(f"{'H':>4}", end='')
                break

        if not found:
            idx = -1
            farthest = -1
            for j in range(capacity):
                if frame[j] == -1:
                    idx = j
                    break
            if idx == -1:
                for j in range(capacity):
                    k = i + 1
                    while k < noofpages and frame[j] != pages[k]:
                        k += 1
                    if k == noofpages:
                        idx = j
                        break
                    if k > farthest:
                        farthest = k
                        idx = j
            if idx == -1:
                idx = 0
            frame[idx] = page
            fault += 1
            print(f"{'F':>4}", end='')

        table[i][:] = frame[:]

    print("\n------------------------------------------------------")
    print("Frame Status:")
    for r in range(capacity):
        for c in range(noofpages):
            print(f"{table[c][r]:3d} ", end='')
        print()
    print("------------------------------------------------------")
    hit_ratio = (hit / noofpages) * 100
    fault_ratio = (fault / noofpages) * 100
    print(f"Page Faults: {fault}")
    print(f"Page Hits: {hit}")
    print(f"Hit Ratio: {hit_ratio:.2f}%  Fault Ratio: {fault_ratio:.2f}%\n")

# ---------------- Menu & main ----------------
def main_menu():
    """Show menu and run chosen algorithm."""
    while True:
        print("\n--- Page Replacement Algorithms Menu ---")
        print("1. FIFO")
        print("2. LRU")
        print("3. Optimal")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == '4':
            print("Exiting.")
            break
        if choice not in ('1', '2', '3'):
            print("Invalid choice. Enter 1, 2, 3, or 4.")
            continue

        pages = input_pages()
        capacity = input_capacity()

        if choice == '1':
            fifo(pages, capacity)
        elif choice == '2':
            lru(pages, capacity)
        else:
            optimal(pages, capacity)

if __name__ == "__main__":
    main_menu()
