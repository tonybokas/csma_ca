#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

import time
from multiprocessing import Process, Value

import numpy as np
import seaborn as sb
from matplotlib import pyplot

# To-do: What is the difference between λ_A and λ_C?

# CONSTANTS

# Network:
BW = 12 * 10**6   # bandwidth in bits/sec
FRAME = 1500 * 8  # frame size in bits

# Slot allocations:
SLOT = 10                   # slot length in micro sec
ACK = RTS = CTS = SLOT * 3  # acknowledgment, request- and clear-to-send
DIFS = SLOT * 4             # distributed interframe space
SIFS = SLOT * 2             # short interframe space
CW_MAX = SLOT * 1024        # contention window limit

# Simulation:
SIM_TIME = 10                               # simulation time in sec
ARRIVALS = [100, 200, 300, 500, 700, 1000]  # arrival rate in frames/sec

# VARIABLES

cw = SLOT * 8  # contention window
throughput = collisions = fairness = 0  # to-do: use None instead?


class App:
    def __init__(self, station):
        self.station = station

    def buffer_frame(self):
        pass


class Station:
    def __init__(self, c_domain, access_pt):
        self.c_domain = c_domain
        self.access_pt = access_pt
        self.cw = None
        self.backoff = None
        self.awaiting_ack = False
        self.channel_busy = False
        self.ack_received = False

    def run(self):
        frame = self.check_buffer()

        if not frame:
            return

        self.sense_channel()

        trys = 0
        while self.channel_busy:
            self.select_backoff()
            self.freeze()
            self.decrement_backoff()
            if trys == 10:
                return 'Timeout'

        self.transmit()

        wait_time = 0
        while self.awaiting_ack():
            if self.ack_received:
                return 'Success'
            if wait_time == 10:
                return 'Timeout no ack'

    def check_buffer(self):
        pass

    def select_backoff(self):
        pass

    def sense_channel(self, channel_status):
        self.channel_busy = True

    def freeze(self):
        pass

    def decrement_backoff(self):
        self.backoff -= 1

    def transmit(self):
        self.awaiting_ack = True

    def double_cw(self):
        pass


class AccessPoint:
    def __init__(self, c_domain):
        self.c_domain = c_domain

    def run(self):
        pass

    def ack(self, station):
        pass


def slot_simulation(duration, slot_start):
    i = 0
    start = time.time()
    end = start + duration

    print('Simulation start:', start)

    while True:
        slot_start.value = 0
        time.sleep(0.000009)
        slot_start.value = 1
        time.sleep(0.000001)
        i += 1
        if time.time() >= end:
            break

    print('Simulation end:', end)
    print('Slots simulated:', i)


def example_poisson():
    sample = np.random.poisson(5, 100)
    print('Sample data:')
    print(sample)

    plot = sb.displot(data=sample, kind='hist', bins=14)
    plot.set(title='Poisson Distribution', xlabel='event', ylabel='count')
    pyplot.tight_layout()
    pyplot.show()


def main():
    slot_start = Value('i', 0)  # variable typecode and value

    process = Process(target=slot_simulation,       # target function
                      args=(SIM_TIME, slot_start))  # function arguments

    process.start()

    t = f = 0

    try:
        while process.is_alive():
            # Transmissions here:
            if slot_start.value == 1:
                t += 1  # transmit
            else:
                f += 1  # gotta wait

    except Exception as e:
        raise e

    finally:
        process.join()

    print('microseconds at slot start:', t)
    print('microseconds mid-slot:', f)

    # example_poisson()


if __name__ == '__main__':
    main()
