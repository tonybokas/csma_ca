#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

# To-do:
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

ACK = RTS = CTS = 3
ARRIVAL_RATE = [100, 200, 300, 500, 700, 1000]  # arrival rate in frames/sec
BW = 12                                         # bits per microsecond
CW = 8                                          # base contention window
CW_MAX = 1024                                   # contention window limit
DIFS = 4                                        # distributed interframe space
FRAME = 1500 * 8                                # frame size in bits
SIFS = 2                                        # short interframe space
SIM_TIME = 10                                   # simulation time in sec
SLOT_DURATION = 10                              # slot microseconds
SLOT_SIZE = 0.00001                             # slot length in micro sec

BITS_PER_SLOT = BW * SLOT_DURATION

# VARIABLES

throughput = collisions = fairness = 0


class App:
    def __init__(self):
        self.station: Station = None
        self.write_times: list = []
        self.next_write: int = 0

    def state(self):
        s = f'{self}:\n'
        s += f'    station: {self.station}\n'
        s += f'    write_times (next 3): {self.write_times[:3]}\n'
        s += f'    next_write: {self.next_write}\n'
        return s

    def generate_traffic(self, rate):
        U = np.random.uniform(0, 1, rate*SIM_TIME)  # uniform dist
        X = ((-1/rate) * np.log(1-U))/SLOT_SIZE     # exponential dist
        self.write_times = [round(f) for f in X]    # use list functionality
        self.next_write = self.write_times.pop(0)   # queue up the first write

    def try_buffer_frame(self, slot):
        if self.write_times and self.next_write == slot:
            self.station.buffer.append(FRAME)
            self.next_write += self.write_times.pop(0)


class Station:
    def __init__(self, vcs: bool = False):
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
        self.vcs: bool = vcs
        self.rts: int = RTS

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
        # To-do: implement SIFS
        if self.vcs:
            if self.rts:
                self.rts -= 1
                self.backoff = SIFS
                return
            if self.access_pt.cts > 0:
                self.domain.transmissions -= 1
                self.access_pt.domain.transmissions += 1

        if not self.sending:
            self.sending = True
            self.transmission = self.buffer[0] / BITS_PER_SLOT + SIFS + ACK

            self.domain.nav = self.transmission
            self.domain.transmissions += 1

            self.access_pt.domain.nav = self.transmission
            self.access_pt.domain.transmissions += 1

        if self.transmission > 0:
            self.transmission -= 1
        else:
            self.access_pt.sifs = SIFS
            self.access_pt.ack = ACK
            self.awaiting_ack = True


class AccessPoint:
    def __init__(self, vcs: bool = False):
        self.domain: CollisionDomain = None
        self.ack: int = 0
        self.sifs: int = 0
        self.vcs: bool = vcs
        self.cts: int = 0

    def state(self):
        return f'{self}:\n    sifs: {self.sifs}\n    ack: {self.ack}\n'

    def try_ack(self, station):
        if self.domain.transmissions > 1:
            return
        elif self.sifs:
            self.sifs -= 1
        elif self.ack:
            self.ack -= 1
        else:
            self.domain.nav = 0             # testing
            self.domain.transmissions -= 1  # testing

            station.domain.nav = 0
            station.domain.transmissions -= 1

            station.sending = station.awaiting_ack = False
            station.collisions = 0
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


def simulation_state(slot, apps, stations):
    print('Iteration:', slot)

    print('App states:')
    for app in apps:
        print(app.state())

    print('Station states:')
    for station in stations:
        print(station.state())

    print('Access point state:')
    print(stations[0].access_pt.state())


def example_poisson():
    sample = np.random.poisson(5, 100)
    print('Sample data:')
    print(sample)

    plot = sb.displot(data=sample, kind='hist', bins=14)
    plot.set(title='Poisson Distribution', xlabel='event', ylabel='count')
    pyplot.tight_layout()
    pyplot.show()


def simulate(rate: int, hidden_terminals: bool, vcs: bool):
    # Create all the entities in the simulation:
    app_A = App()
    app_B = App()
    apps = [app_A, app_B]

    if vcs:
        station_A = Station(vcs=True)
        station_B = Station(vcs=True)
    else:
        station_A = Station()
        station_B = Station()

    stations = [station_A, station_B]

    access_pt = AccessPoint(vcs=True) if vcs else AccessPoint()

    # Connect the entities:
    app_A.station = station_A
    app_B.station = station_B

    for station in stations:
        station.access_pt = access_pt

    # Conditional to set up single domain or hidden terminals:
    if hidden_terminals:
        station_A.domain = CollisionDomain()
        station_B.domain = CollisionDomain()
        access_pt.domain = CollisionDomain()
    else:
        station_A.domain = \
        station_B.domain = \
        access_pt.domain = CollisionDomain()

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

        for app in apps:
            app.try_buffer_frame(slot)

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

                if station.backoff == 0:
                    station.double_cw()
                    station.backoff += SIFS

            elif any(station.buffer):
                station.try_send()

        for station in stations:
            station.domain.transmissions = station.domain.nav = 0

        access_pt.domain.transmissions = access_pt.domain.nav = 0

    print(f'Simulation end: {end}\n')

    simulation_state(slot, apps, stations)

    # Placeholder, will eventually generate the graphs after each run:
    # example_poisson()


def main():
    for rate in ARRIVAL_RATE:
        simulate(rate, False, True)


if __name__ == '__main__':
    main()
