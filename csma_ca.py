#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

import math
import time

from numpy.random import uniform
import numpy as np
import seaborn as sb
from matplotlib import pyplot

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
SIM_TIME = 10                                   # simulation time in sec
ARRIVAL_RATE = [100, 200, 300, 500, 700, 1000]  # arrival rate in frames/sec

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

        # Pseudocode of station behvaior:
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


def example_poisson():
    sample = np.random.poisson(5, 100)
    print('Sample data:')
    print(sample)

    plot = sb.displot(data=sample, kind='hist', bins=14)
    plot.set(title='Poisson Distribution', xlabel='event', ylabel='count')
    pyplot.tight_layout()
    pyplot.show()


def main():
    start = time.time() # start time
    end = start + 10    # start time plus 10 seconds

    # Note: time.time() defaults to seconds, not microseconds

    # This is really just a placeholder for now:
    print('Simulation start:', start)

    # Selecting the first arrival rate for now. Later we will iterate through
    # the others:
    ar = ARRIVAL_RATE[0]

    # 1. Create uniform distribution as an array.
    # 2. Convert the distribution values per Appendix 1 equation and save
    #    updated array values to variable X.
    X = (-1/ar) * np.log(1-uniform(0, 1, ar*10))
    print(X[:10])  # display first ten elements

    # View the distribution shape:
    sb.displot(kind='hist', x=X)
    pyplot.show()

    print('Simulation end:', end)

    # Placeholder, but it will eventually generate the graphs after each run:
    # example_poisson()


if __name__ == '__main__':
    main()
