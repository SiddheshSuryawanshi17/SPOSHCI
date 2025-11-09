#!/usr/bin/env python3
"""
cpu_scheduling.py

Simulate CPU Scheduling Algorithms:
    1. FCFS (First Come First Serve)
    2. SJF (Preemptive)
    3. Priority (Non-Preemptive)
    4. Round Robin (Preemptive)

For each process, the program calculates:
 - Waiting Time (WT)
 - Turnaround Time (TAT)
 - Average WT and TAT
"""

from collections import deque

# ---------------- FCFS ----------------
def fcfs(processes):
    """First Come First Serve Scheduling"""
    n = len(processes)
    processes.sort(key=lambda x: x['arrival'])

    time = 0
    total_wt = 0
    total_tat = 0
    print("\n--- FCFS SCHEDULING ---")
    print("PID\tAT\tBT\tWT\tTAT")

    for p in processes:
        if time < p['arrival']:
            time = p['arrival']
        p['waiting'] = time - p['arrival']
        time += p['burst']
        p['turnaround'] = p['waiting'] + p['burst']
        total_wt += p['waiting']
        total_tat += p['turnaround']
        print(f"{p['pid']}\t{p['arrival']}\t{p['burst']}\t{p['waiting']}\t{p['turnaround']}")

    print(f"\nAverage Waiting Time: {total_wt/n:.2f}")
    print(f"Average Turnaround Time: {total_tat/n:.2f}")

# ---------------- SJF (Preemptive) ----------------
def sjf_preemptive(processes):
    """Shortest Remaining Time First (Preemptive SJF)"""
    n = len(processes)
    processes.sort(key=lambda x: x['arrival'])

    remaining = [p['burst'] for p in processes]
    complete = 0
    time = 0
    shortest = 0
    minm = float('inf')
    check = False
    finish_time = 0
    wt = [0]*n
    tat = [0]*n

    while complete != n:
        for j in range(n):
            if (processes[j]['arrival'] <= time) and (remaining[j] < minm) and remaining[j] > 0:
                minm = remaining[j]
                shortest = j
                check = True
        if not check:
            time += 1
            continue
        remaining[shortest] -= 1
        minm = remaining[shortest]
        if minm == 0:
            minm = float('inf')

        if remaining[shortest] == 0:
            complete += 1
            check = False
            finish_time = time + 1
            wt[shortest] = finish_time - processes[shortest]['burst'] - processes[shortest]['arrival']
            if wt[shortest] < 0:
                wt[shortest] = 0
        time += 1

    for i in range(n):
        tat[i] = processes[i]['burst'] + wt[i]

    print("\n--- SJF (Preemptive) ---")
    print("PID\tAT\tBT\tWT\tTAT")
    for i in range(n):
        print(f"{processes[i]['pid']}\t{processes[i]['arrival']}\t{processes[i]['burst']}\t{wt[i]}\t{tat[i]}")

    print(f"\nAverage Waiting Time: {sum(wt)/n:.2f}")
    print(f"Average Turnaround Time: {sum(tat)/n:.2f}")

# ---------------- Priority (Non-Preemptive) ----------------
def priority_non_preemptive(processes):
    """Priority Scheduling (Non-Preemptive)"""
    n = len(processes)
    processes.sort(key=lambda x: (x['arrival'], x['priority']))
    completed = []
    time = 0
    total_wt = 0
    total_tat = 0
    ready = []

    print("\n--- PRIORITY (Non-Preemptive) ---")
    print("PID\tAT\tBT\tPriority\tWT\tTAT")

    while len(completed) < n:
        for p in processes:
            if p not in ready and p not in completed and p['arrival'] <= time:
                ready.append(p)
        if not ready:
            time += 1
            continue
        ready.sort(key=lambda x: x['priority'])  # lower number = higher priority
        curr = ready.pop(0)
        if time < curr['arrival']:
            time = curr['arrival']
        curr['waiting'] = time - curr['arrival']
        time += curr['burst']
        curr['turnaround'] = curr['waiting'] + curr['burst']
        completed.append(curr)
        total_wt += curr['waiting']
        total_tat += curr['turnaround']
        print(f"{curr['pid']}\t{curr['arrival']}\t{curr['burst']}\t{curr['priority']}\t\t{curr['waiting']}\t{curr['turnaround']}")

    print(f"\nAverage Waiting Time: {total_wt/n:.2f}")
    print(f"Average Turnaround Time: {total_tat/n:.2f}")

# ---------------- Round Robin ----------------
def round_robin(processes, quantum):
    """Round Robin Scheduling (Preemptive)"""
    n = len(processes)
    rem_bt = [p['burst'] for p in processes]
    t = 0
    wt = [0]*n
    tat = [0]*n

    while True:
        done = True
        for i in range(n):
            if rem_bt[i] > 0:
                done = False
                if rem_bt[i] > quantum:
                    t += quantum
                    rem_bt[i] -= quantum
                else:
                    t += rem_bt[i]
                    wt[i] = t - processes[i]['burst'] - processes[i]['arrival']
                    rem_bt[i] = 0
        if done:
            break

    for i in range(n):
        tat[i] = processes[i]['burst'] + wt[i]

    print("\n--- ROUND ROBIN ---")
    print("PID\tAT\tBT\tWT\tTAT")
    for i in range(n):
        print(f"{processes[i]['pid']}\t{processes[i]['arrival']}\t{processes[i]['burst']}\t{wt[i]}\t{tat[i]}")

    print(f"\nAverage Waiting Time: {sum(wt)/n:.2f}")
    print(f"Average Turnaround Time: {sum(tat)/n:.2f}")

# ---------------- Input & Menu ----------------
def get_process_input(include_priority=False):
    """Input helper"""
    n = int(input("Enter number of processes: "))
    processes = []
    for i in range(n):
        print(f"\nEnter details for Process {i+1}:")
        at = int(input("Arrival Time: "))
        bt = int(input("Burst Time: "))
        if include_priority:
            pr = int(input("Priority (lower = higher): "))
            processes.append({'pid': i+1, 'arrival': at, 'burst': bt, 'priority': pr})
        else:
            processes.append({'pid': i+1, 'arrival': at, 'burst': bt})
    return processes

def main():
    while True:
        print("\n===== CPU SCHEDULING ALGORITHMS =====")
        print("1. FCFS (First Come First Serve)")
        print("2. SJF (Preemptive)")
        print("3. Priority (Non-Preemptive)")
        print("4. Round Robin (Preemptive)")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            procs = get_process_input()
            fcfs(procs)
        elif choice == '2':
            procs = get_process_input()
            sjf_preemptive(procs)
        elif choice == '3':
            procs = get_process_input(include_priority=True)
            priority_non_preemptive(procs)
        elif choice == '4':
            procs = get_process_input()
            q = int(input("Enter Time Quantum: "))
            round_robin(procs, q)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()


"""
===============================================================================
PROGRAM SUMMARY:
-------------------
This program simulates four major CPU scheduling algorithms:

1. FCFS (First Come First Serve)
   - Executes processes in the order they arrive.
   - Non-preemptive.

2. SJF (Preemptive)
   - Also known as Shortest Remaining Time First.
   - Always executes the process with the smallest remaining burst time.

3. Priority (Non-Preemptive)
   - The process with the highest priority (lowest number) runs first.

4. Round Robin (Preemptive)
   - Each process is given a fixed time quantum.
   - After the quantum, the process is preempted and added back to the queue.

===============================================================================
SAMPLE INPUT (FCFS Example):
--------------------------------
Enter your choice (1-5): 1
Enter number of processes: 4

Enter details for Process 1:
Arrival Time: 0
Burst Time: 5

Enter details for Process 2:
Arrival Time: 1
Burst Time: 3

Enter details for Process 3:
Arrival Time: 2
Burst Time: 8

Enter details for Process 4:
Arrival Time: 3
Burst Time: 6

===============================================================================
SAMPLE OUTPUT (FCFS Example):
--------------------------------
--- FCFS SCHEDULING ---
PID	AT	BT	WT	TAT
1	0	5	0	5
2	1	3	4	7
3	2	8	6	14
4	3	6	13	19

Average Waiting Time: 5.75
Average Turnaround Time: 11.25

===============================================================================
WHAT TO EXPLAIN IN EXAM:
----------------------------
- Each algorithm decides the CPU order of execution.
- Preemptive algorithms (SJF, Round Robin) allow interruption mid-execution.
- Non-preemptive algorithms (FCFS, Priority) do not.
- Compare average waiting and turnaround times.
===============================================================================
"""
