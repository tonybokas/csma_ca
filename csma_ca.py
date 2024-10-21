#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

# To-do:
# - Not sure if we are supposed to use bandwidth or not. Is "arrival rate"
#   the defacto bandwidth?
#
# - If I scale the X values to be integers like the example, the simulation
#   doesn't work. The inter-arrival times are too large.
#
# - I'm not sure if prof. will be ok with use buffering the frames as slots,
#   but it works better that way. Everything else is expressed as slots. See
#   try_buffer_frame() method of App
#
# - You can run the simulation for all arrival times. Some cap off at even
#   numbers. I'm not sure if that is good or bad. If you want to run it for
#   one arrival time, edit the ARRIVAL_RATE list.
#
# - I will soon add some more variables to try and track throughout,
#   collisions, and fairness. I also will plot and save the results for
#   each run.
#
# - Still need to implement hidden terminals and virtual carrier sensing.
#   It will be kind of a hustle, but it should not require a huge change
#   to the script.

import time
from random import randint

import numpy as np
import seaborn as sb
from matplotlib import pyplot

# CONSTANTS

# Network:
BW = 12           # bits per microsecond
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
        self.next_write: int = 0

    def state(self):
        s = f'{self}:\n'
        s += f'    station: {self.station}\n'
        s += f'    frames (next 3): {self.frames[:3]}\n'
        s += f'    write_times (next 3): {self.write_times[:3]}\n'
        s += f'    next_write: {self.next_write}\n'
        return s

    def generate_traffic(self, rate):
        U = np.random.uniform(0, 1, rate*SLOT_SIZE)  # uniform distribution
        X = (-1/rate) * np.log(1 - U)                # exponential distribution

        # Convert to list for better functionality:
        self.write_times = [float(i) for i in X]

    def try_buffer_frame(self, slot, rate):
        if self.write_times and self.next_write <= slot:
            self.station.buffer.append(FRAME/rate)  # frames expressed as slots
            self.next_write += self.write_times.pop(0)


class Station:
    def __init__(self):
        self.domain: CollisionDomain = None
        self.access_pt: AccessPoint = None
        self.buffer: list = []
        self.difs = DIFS
        self.backoff = randint(0, CW)
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
        s += f'    buffer (first 3): {self.buffer[:3]}\n'
        s += f'    difs: {self.difs}\n'
        s += f'    backoff: {self.backoff}\n'
        s += f'    freeze_time: {self.freeze_time}\n'
        s += f'    collisions: {self.collisions}\n'
        s += f'    cw: {self.cw}\n'
        s += f'    sending: {self.sending}\n'
        s += f'    awaiting_ack: {self.awaiting_ack}\n'
        s += f'    successes: {self.successes}\n'
        return s

    def double_cw(self):
        self.sending = False  # forces resend of buffered frame

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
        return f'{self}:\n    sifs: {self.sifs}\n    ack: {self.ack}\n'

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


def simulate(rate):
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
        app.generate_traffic(rate)  # to-do: iterate

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
            app.try_buffer_frame(now - end + SIM_TIME, rate)

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

        domain.transmissions = domain.nav = 0

    print(f'Simulation end: {end}\n')

    simulation_state(slot, apps, stations, domain)

    # Placeholder, will eventually generate the graphs after each run:
    # example_poisson()


def main():
    for rate in ARRIVAL_RATE:
        simulate(rate)


if __name__ == '__main__':
    main()
