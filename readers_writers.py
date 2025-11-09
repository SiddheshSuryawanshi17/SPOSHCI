#!/usr/bin/env python3
import threading
import time

# Shared state & semaphores (mirrors the Java version)
reader_count = 0
reader_count_lock = threading.Lock()  # only used for safe access to reader_count variable in printouts (optional)
x = threading.Semaphore(1)
rsem = threading.Semaphore(1)
wsem = threading.Semaphore(1)

def reader():
    global reader_count
    try:
        # entry section
        rsem.acquire()
        x.acquire()
        reader_count += 1
        if reader_count == 1:
            # first reader locks writers out
            wsem.acquire()
        x.release()

        # critical section (reading)
        print(f"Thread {threading.current_thread().name} is READING")
        time.sleep(1.5)
        print(f"Thread {threading.current_thread().name} has FINISHED READING")

        # exit section
        x.acquire()
        reader_count -= 1
        if reader_count == 0:
            # last reader allows writers
            wsem.release()
        x.release()
        rsem.release()

    except Exception as e:
        print("Reader error:", e)

def writer():
    try:
        rsem.acquire()
        wsem.acquire()

        print(f"Thread {threading.current_thread().name} is WRITING")
        time.sleep(2.5)
        print(f"Thread {threading.current_thread().name} has finished WRITING")

        wsem.release()
        rsem.release()

    except Exception as e:
        print("Writer error:", e)

def main():
    # create reader and writer threads similar to your Java main
    t1 = threading.Thread(target=reader, name="thread1")
    t2 = threading.Thread(target=reader, name="thread2")
    t3 = threading.Thread(target=reader, name="thread3")
    t4 = threading.Thread(target=writer, name="thread4")
    t5 = threading.Thread(target=writer, name="thread5")
    t6 = threading.Thread(target=writer, name="thread6")

    threads = [t1, t2, t3, t4, t5, t6]

    # start threads
    for t in threads:
        t.start()

    # wait for all threads to finish
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
