#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

# To-do:
# - Not all directions implemented yet, some constants still unused
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
CW = SLOT_SIZE * 8               # base contention window
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

        # Convert to lists for better functionality:
        self.frames = list(scale_values(U))
        self.write_times = list(scale_values(X))
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
        self.trans: dict = {'to': None, 'from': None, 'data': None}
        self.backoff: int = randint(0, CW)
        self.cw: int = 0
        self.awaiting_ack: bool = False

    def sense_channel(self):
        if len(self.domain.trans) > 1:
            return  # to-do: handle collision!
        elif self.domain.trans[0]['data']:
            self.trans = self.domain.trans[0]
            self.collisions = self.cw = 0

    def freeze(self):
        if self.trans['data']:
            self.trans -= 1
        else:
            self.difs = DIFS

    def transmit(self):
        self.trans['to'] = self.access_pt
        self.trans['from'] = self
        self.trans['data'] = self.buffer[0]
        self.domain.trans.append(self.trans)
        self.awaiting_ack = True

    def double_cw(self):
        if self.cw <= CW_MAX:
            self.cw = CW * 2**self.collisions

        # Backoff fool...
        self.backoff = randint(0, self.cw)
        self.collisions += 1


class AccessPoint:
    def __init__(self):
        self.domain: CollisionDomain = None
        self.trans: dict = {'to': None, 'from': None, 'data': None}
        self.sifs: int = SIFS

    def decrement_sifs(self):
        self.sifs -= 1

    def ack(self):
        self.domain.trans[0]['to'] = self.domain['from']
        self.domain.trans[0]['from'] = self
        self.domain.trans[0]['data'] = ACK


@dataclass
class CollisionDomain:
    nav: list = []

    def clear(self):
        self.trans = []


def scale_values(array: np.array) -> np.array:
    # Make array positive integers per project example. Find power of 10
    # that makes smallest number greater than one and apply to whole array:
    p, m = 0, np.min(array)

    if m < 0:
        raise ValueError(f'Expected positive numbers only, got {m}')

    while m < 1:
        m *= 10
        p += 1

    return np.round(array * 10**p)  # apply power of 10 and round


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
        now = time.time()  # get time every iteration

        # Exit the loop if time equals end time:
        if now >= end:
            break

        slot += 1

        # Stack frames onto station buffer
        for app in apps:
            app.buffer_frame(now - end + SIM_TIME)

        for station in stations:
            if not any(station.buffer):  # nothing for this station to send
                continue                 # jump to next station

            # Only one of these happen per slot iteration:

            if station.cw:
                station.backoff -= 1  # to-do: might make this a function

            elif station.difs:
                station.sense_channel()

            elif station.trans:
                station.freeze()

            elif station.backoff:
                station.backoff -= 1
                station.sense_channel()

            elif station.awaiting_ack:
                station.awaiting_ack = False

            else:
                station.transmit()

        # The following domain checks occur each slot iteration. This section
        # represents the "transfer through the ether":

        # There is a collision because the domain object has more than one
        # transmission dict object in its list:
        if len(domain.trans) > 1:
            for station in stations:
                station.double_cw()
                domain.trans.clear()

            continue

        if not domain.trans[0]['data']:
            domain.trans.clear()
            # To-do: decrement a SIFS wait time for stations too?
            access_pt.decrement_sifs() if access_pt.sifs else access_pt.ack()

            continue

        # Each domain host takes note of the domain transmissions:
        if not access_pt.trans['data']:
            access_pt.trans = domain.trans[0].copy()

        for station in stations:
            if not station.trans['data']:
                station.trans = domain.trans[0].copy()

        # Frames are transmiting through the domain "ether":
        domain.trans[0]['data'] -= 1
        access_pt.trans['data'] -= 1

        for station in stations:
            station.trans['data'] -= 1

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
