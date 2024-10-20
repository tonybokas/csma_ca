#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

# To-do:
# - Not all directions implemented yet, some constants still unused

import time
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
# SIM_TIME = 10                                   # simulation time in sec
SIM_TIME = 1                                   # simulation time in sec
ARRIVAL_RATE = [100, 200, 300, 500, 700, 1000]  # arrival rate in frames/sec

# VARIABLES

throughput = collisions = fairness = 0


class App:
    def __init__(self):
        self.station: Station = None
        self.frames: list = []
        self.write_times: list = []
        self.next_write: int = 0

    def state(self):
        s = f'{self}:\n'
        s += f'    station: {self.station}\n'
        s += f'    next 3 frames: {self.frames[:3]}\n'
        s += f'    next 3 write_times: {self.write_times[:3]}\n'
        s += f'    next_write: {self.next_write}\n'
        return s

    def generate_traffic(self, rate):
        # Create uniform distribution as an array:
        U = np.random.uniform(0, 1, rate * 10)

        # Convert the distribution values per Appendix 1 equation and save
        # updated array values to variable X:
        X = (-1 / rate) * np.log(1 - U)

        # Convert to lists for better functionality:
        self.frames = [int(i) for i in scale_values(U)]
        self.write_times = [float(i) for i in X]

    def try_buffer_frame(self, slot):
        if any(self.frames) and self.next_write <= slot:
            self.station.buffer.append(self.frames.pop(0))
            self.next_write += self.write_times.pop(0)


class Station:
    def __init__(self):
        self.domain: CollisionDomain = None
        self.access_pt: AccessPoint = None
        self.buffer: list = []
        self.difs = DIFS
        self.backoff = randint(0, CW)
        self.sifs: int = 0
        self.freeze_time: int = 0
        self.transmission: int = 0
        self.collisions: int = 0
        self.cw: int = 0
        self.sending: bool = False
        self.awaiting_ack: bool = False
        self.successes: int = 0

    def state(self):
        s = f'{self}:\n'
        s += f'    domain: {self.domain}\n'
        s += f'    access_pt: {self.access_pt}\n'
        s += f'    buffer first 3: {self.buffer[:3]}\n'
        s += f'    difs: {self.difs}\n'
        s += f'    backoff: {self.backoff}\n'
        s += f'    sifs: {self.sifs}\n'
        s += f'    wait: {self.freeze_time}\n'
        s += f'    collisions: {self.collisions}\n'
        s += f'    cw: {self.cw}\n'
        s += f'    sending: {self.sending}\n'
        s += f'    awaiting_ack: {self.awaiting_ack}\n'
        s += f'    successes: {self.successes}\n'
        return s

    def double_cw(self):
        self.sending = False

        if self.cw <= CW_MAX:
            self.cw = CW * 2**self.collisions

        self.backoff = randint(0, self.cw)
        self.collisions += 1

    def freeze(self):
        if self.freeze_time:
            self.freeze_time -= 1
        else:
            self.freeze_time = self.domain.nav
            self.difs = DIFS

    def try_send(self):
        if not self.sending:
            self.sending = True
            self.domain.nav = self.transmission = self.buffer[0] + SIFS + ACK
            self.domain.transmissions += 1

        if self.transmission > 0:
            self.transmission -= 1
        else:
            self.access_pt.sifs = SIFS
            self.access_pt.ack = ACK
            self.awaiting_ack = True


class AccessPoint:
    def __init__(self):
        self.sifs: int = 0
        self.ack: int = 0

    def state(self):
        s = f'{self}:\n'
        s += f'    sifs: {self.sifs}\n '
        return s

    def try_ack(self, station):
        if self.sifs:
            self.sifs -= 1
        elif self.ack:
            self.ack -= 1
        else:
            station.sending = False
            station.domain.nav = 0
            station.domain.transmissions -= 1
            station.awaiting_ack = False
            del station.buffer[0]
            station.successes += 1


class CollisionDomain:
    def __init__(self):
        self.transmissions: int = 0
        self.nav: int = 0

    def state(self):
        s = f'{str(self.__class__.__name__)}:\n'
        s += f'    transmissions: {self.transmissions}\n'
        s += f'    nav: {self.nav}\n'
        return s


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


def simulation_state(slot, apps, stations, domain):
    print('Iteration:', slot)

    for station in stations:
        print(station.state())

    for app in apps:
        print(app.state())

    print(domain.state())


def example_poisson():
    sample = np.random.poisson(5, 100)
    print('Sample data:')
    print(sample)

    plot = sb.displot(data=sample, kind='hist', bins=14)
    plot.set(title='Poisson Distribution', xlabel='event', ylabel='count')
    pyplot.tight_layout()
    pyplot.show()


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

    # Create app traffic:
    for app in apps:
        app.generate_traffic(ARRIVAL_RATE[0])  # to-do: iterate

    # Set counters:
    start = time.time()     # start time
    end = start + SIM_TIME  # start time plus simulation time
    slot = 0                # slot counter

    print(f'Simulation start: {start}\n')

    while True:
        now = time.time()  # get time every iteration

        if now >= end:     # exit loop if current time equals end time
            break

        slot += 1

        # Stack frames onto station buffer:
        for app in apps:
            app.try_buffer_frame(now - end + SIM_TIME)

        for station in stations:
            if station.domain.transmissions > 1:
                station.double_cw()

            elif station.domain.transmissions == 1 and not station.sending:
                station.freeze()

            elif station.difs:
                station.difs -= 1

            elif station.backoff:
                station.backoff -= 1

            elif station.awaiting_ack:
                access_pt.try_ack(station)

            elif any(station.buffer):
                station.try_send()

        domain.transmissions = 0
        domain.nav = 0

    print(f'Simulation end: {end}\n')

    simulation_state(slot, apps, stations, domain)

    # Placeholder, will eventually generate the graphs after each run:
    # example_poisson()


if __name__ == '__main__':
    main()
