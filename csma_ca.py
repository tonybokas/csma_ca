#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

# To-do:
# - Steps (d) and (e) not implemented yet
# - Not all nuances of directions implemented yet, many constants still unused
# - Script not yet tested

import time
from dataclasses import dataclass
from random import randint

import numpy as np
import seaborn as sb
from matplotlib import pyplot

# CONSTANTS

# Network:
BW = 12 * 10**6   # bandwidth in bits/sec
FRAME = 1500 * 8  # frame size in bits

# Slot allocations:
SLOT_SIZE = 10                   # slot length in micro sec
ACK = RTS = CTS = SLOT_SIZE * 3  # acknowledgment, request- and clear-to-send
DIFS = SLOT_SIZE * 4             # distributed interframe space
SIFS = SLOT_SIZE * 2             # short interframe space
CW_MAX = SLOT_SIZE * 1024        # contention window limit

# Simulation:
SIM_TIME = 10                                   # simulation time in sec
ARRIVAL_RATE = [100, 200, 300, 500, 700, 1000]  # arrival rate in frames/sec

# VARIABLES

throughput = collisions = fairness = 0


class App:
    def __init__(self):
        self.station: Station = None
        self.frames: list = []
        self.write_times: list = []
        self.next_write: float = 0.0

    def generate_traffic(self, rate):
        # Create uniform distribution as an array:
        U = np.random.uniform(0, 1, rate * 10)

        # Convert the distribution values per Appendix 1 equation and save
        # updated array values to variable X:
        X = (-1 / rate) * np.log(1 - U)

        # Make X values positive integers per instructions. Find power of 10
        # that makes smallest number in array greater than one:
        p, m = 0, np.min(X)

        while m < 1:
            m *= 10
            p += 1

        X = np.round(X * 10**p)  # apply that power of 10 to all X and round

        # Convert to lists for better functionality:
        self.frames = list(U)
        self.write_times = list(X)
        self.next_write = 0.0

    def buffer_frame(self, now):
        if any(self.frames) and self.next_write <= now:
            self.station.buffer.append(self.frames.pop(0))
            self.next_write += self.write_times.pop(0)


class Station:
    def __init__(self):
        self.domain: CollisionDomain = None
        self.access_pt: AccessPoint = None
        self.buffer: list = []
        self.difs: int = DIFS
        self.nav: int = 0
        self.backoff: int = randint(0, self.contention_w)
        self.contention_w: int = SLOT_SIZE * 8
        self.awaiting_ack: bool = False

    def sense_channel(self):
        if len(self.domain.nav) > 1:
            return  # to-do: handle collision!
        elif self.domain.nav:
            self.nav = self.domain.nav[0]

    def freeze(self):
        if self.nav:
            self.nav -= 1
        else:
            self.difs = DIFS

    def transmit(self):
        self.domain.nav.append(self.buffer[0])
        self.awaiting_ack = True

    def double_contention_w(self):
        pass


class AccessPoint:
    def __init__(self):
        self.domain: CollisionDomain = None
        self.nav: int = 0

    def ack(self):
        # To-do: Ack which station? Probably need to store dict in domain.nav:
        pass


@dataclass
class CollisionDomain:
    nav: list = []

    def clear(self):
        self.nav = []


def main():
    # Create all the entities in the simulation:
    app_A = App()
    app_B = App()
    apps = [app_A, app_B]

    station_A = Station()
    station_B = Station()
    stations = [station_A, station_B]

    access_pt = AccessPoint()
    domain = CollisionDomain()

    # Connect the entities:
    app_A.station = station_A
    app_B.station = station_B

    for station in stations:
        station.access_pt = access_pt
        station.domain = domain  # to-do: this will change for hidden terminals

    access_pt.domain = domain

    # Create app traffic:
    for app in apps:
        app.generate_traffic(ARRIVAL_RATE[0])  # to-do: iterate

    # Set counters:
    start = time.time()     # start time
    end = start + SIM_TIME  # start time plus simulation time
    slot = 0                # slot counter

    print('Simulation start:', start)

    # From my understanding of the directions, we are to time the simulation
    # but not actually use time to dictate the transmissions. They are just
    # supposed to flow along according to the slot and then end after 10
    # seconds. This means that each iteration of the main component of the
    # script needs to equal one slot. This allows the activities between the
    # simulated entities to occur in a more realistic way. The only other way
    # to achieve this parallelism is to have multi-threading, which is not the
    # objective:

    while True:
        now = time.time()

        if now >= end:
            break

        slot += 1

        for app in apps:
            app.buffer_frame(now - end + SIM_TIME)

        for station in stations:
            if not any(station.buffer):
                continue

            if station.difs:
                station.sense_channel()

            elif station.nav:
                station.freeze()

            elif station.backoff:
                station.backoff -= 1
                station.sense_channel()

            else:
                station.transmit()

        if len(domain.nav) > 1:
            # There is a collision. Resume the loop so the stations can
            # address it:
            continue

        if domain.nav and not access_pt.nav:
            access_pt.nav = domain.nav[0]

        if domain.nav:
            # The frames are transmiting through the domain to the
            # access point:
            domain.nav[0] -= 1
            access_pt.nav -= 1

            if not access_pt.nav:
                access_pt.ack()

    print('Simulation end:', end)

    # Placeholder, will eventually generate the graphs after each run:
    # example_poisson()


def example_poisson():
    sample = np.random.poisson(5, 100)
    print('Sample data:')
    print(sample)

    plot = sb.displot(data=sample, kind='hist', bins=14)
    plot.set(title='Poisson Distribution', xlabel='event', ylabel='count')
    pyplot.tight_layout()
    pyplot.show()


if __name__ == '__main__':
    main()
