#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

import time
from random import randint

import numpy as np
import pandas as pd
import seaborn as sb

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


class App:
    def __init__(self):
        self.station: Station = None
        self.write_times: list = []
        self.next_write: int = 0

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
        # VCS attributes:
        self.vcs: bool = vcs
        self.rts: int = RTS if vcs else 0

        # Domain attributes:
        self.domain: CollisionDomain = None
        self.access_pt: AccessPoint = None

        # Transmission attributes:
        self.buffer: list = []
        self.difs = DIFS
        self.backoff = randint(0, CW)
        self.nav: int = 0
        self.transmission: int = 0
        self.collisions: int = 0
        self.cw: int = 0
        self.waiting: bool = True
        self.awaiting_ack: bool = False

        # Stat counters:
        self.transfer_timer: int = 0
        self.tot_trans_size: int = 0
        self.tot_trans_time: int = 0
        self.tot_successes: int = 0
        self.tot_collisions: int = 0

    def freeze(self):
        if self.nav:
            self.nav -= 1
        else:
            self.nav = self.domain.nav
            self.difs = DIFS

    def double_cw(self):
        self.domain.transmissions -= 1
        self.waiting = True  # forces resend of buffered frame

        if self.cw <= CW_MAX:
            self.cw = CW * 2**self.collisions

        self.backoff = randint(0, self.cw)
        self.collisions += 1
        self.tot_collisions += 1

    def try_send(self, start):
        if self.waiting:
            self.waiting = False
            self.transmission = self.buffer[0] / BITS_PER_SLOT + SIFS + ACK
            self.domain.nav = self.transmission
            self.domain.transmissions += 1
            self.access_pt.domain.nav = self.transmission
            self.access_pt.domain.transmissions += 1
            self.transfer_timer = start

        if self.transmission > 0:
            self.transmission -= 1
        else:
            self.access_pt.sifs = SIFS
            self.access_pt.ack = ACK
            self.awaiting_ack = True
            if self.vcs:
                self.rts = RTS
                self.access_pt.domain.cleared = None


class AccessPoint:
    def __init__(self, vcs: bool = False):
        # VCS attribute:
        self.cts: int = CTS if vcs else 0

        # Domain attribute:
        self.domain: CollisionDomain = None

        # Transmission attributes:
        self.ack: int = 0
        self.sifs: int = 0

        # Stat counters:
        self.tot_collisions: int = 0

    def clear(self, station):
        self.domain.cleared = station
        self.cts = CTS

    def try_ack(self, station):
        if self.domain.transmissions > 1:
            self.tot_collisions += 1
            return

        elif self.sifs:
            self.sifs -= 1

        elif self.ack:
            self.ack -= 1

        else:
            self.domain.nav = 0
            self.domain.transmissions -= 1
            station.domain.nav = 0
            station.domain.transmissions -= 1
            station.waiting = True
            station.awaiting_ack = False
            station.collisions = 0
            station.tot_trans_size += station.buffer.pop(0)
            station.tot_successes += 1
            station.tot_trans_time += station.transfer_timer
            station.transfer_timer = 0


class CollisionDomain:
    def __init__(self):
        self.transmissions: int = 0
        self.nav: int = 0
        self.cleared: Station = None


def virtual_carrier_sensing(station, access_pt):
    if access_pt.domain.cleared is not None:
        station.freeze()
    elif station.rts:
        station.rts -= 1
    elif access_pt.cts:
        access_pt.cts -= 1
    else:
        access_pt.clear(station)


def simulation(rate: int, ht: bool, vcs: bool):
    print(f'Simulation (rate={rate}, ht={ht}, vcs={vcs})')

    # Create apps and stations:
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

    # Connect apps to their stations:
    app_A.station = station_A
    app_B.station = station_B

    # Create access point and connect the stations to it:
    access_pt = AccessPoint(vcs=True) if vcs else AccessPoint()

    for station in stations:
        station.access_pt = access_pt

    # Create hidden terminals or single domain:
    if ht:
        station_A.domain = CollisionDomain()
        station_B.domain = CollisionDomain()
        access_pt.domain = CollisionDomain()
    else:
        station_A.domain = \
        station_B.domain = \
        access_pt.domain = CollisionDomain()

    # Create app traffic:
    for app in apps:
        app.generate_traffic(rate)

    # Create simulation counters:
    start = time.time()
    end = start + SIM_TIME
    slot = 0

    print(f'Start time: {start}')

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

            elif station.domain.transmissions == 1 and station.waiting:
                station.freeze()

            elif station.difs:
                station.difs -= 1

            elif station.backoff:
                station.backoff -= 1

            elif station.awaiting_ack:
                if station.backoff == 0:
                    station.double_cw()
                    station.backoff += SIFS

                access_pt.try_ack(station)

            elif any(station.buffer):
                if station.vcs and access_pt.domain.cleared != station:
                    virtual_carrier_sensing(station, access_pt)
                    continue

                station.try_send(start=slot)

    print(f'End time: {end}\n')

    s_A = station_A.tot_successes
    tot_A = s_A + station_A.tot_collisions
    tts_A = station_A.tot_trans_size
    ttt_A = station_A.tot_trans_time

    s_B = station_B.tot_successes
    tot_B = s_B + station_B.tot_collisions
    tts_B = station_B.tot_trans_size
    ttt_B = station_B.tot_trans_time

    stats_A = {'station': 'A',
               'throughput': s_A*FRAME/SIM_TIME,
               'ap_collisions': access_pt.tot_collisions,
               'station_collisions': station_A.tot_collisions,
               'fairness': tot_A/tot_B}

    stats_B = {'station': 'B',
               'throughput': s_B*FRAME/SIM_TIME,
               'ap_collisions': access_pt.tot_collisions,
               'station_collisions': station_B.tot_collisions,
               'fairness': tot_B/tot_A}

    return [stats_A, stats_B]


def collect_stats(rate: int, topo: str, station_stats: dict, all_stats: dict):
    all_stats['rate'].append(rate)
    all_stats['topology'].append(topo)

    for stat in station_stats.items():
        all_stats[stat[0]].append(stat[1])


def main():
    all_stats = {'station': [],
                 'rate': [],
                 'topology': [],
                 'throughput': [],
                 'ap_collisions': [],
                 'station_collisions': [],
                 'fairness': []}

    for rate in ARRIVAL_RATE:
        for station_stats in simulation(rate, False, False):
            collect_stats(rate, 'DCF', station_stats, all_stats)

        for station_stats in simulation(rate, True, False):
            collect_stats(rate, 'DCF_HT', station_stats, all_stats)

        for station_stats in simulation(rate, False, True):
            collect_stats(rate, 'DCF_VCS', station_stats, all_stats)

        for station_stats in simulation(rate, True, True):
            collect_stats(rate, 'HT_VCS', station_stats, all_stats)

    print('Creating plots...')

    df = pd.DataFrame(all_stats)

    for alpha in ['A', 'B']:
        plot = sb.catplot(df.query(f'station == "{alpha}"'),
                          kind='bar',
                          x='topology',
                          y='throughput',
                          hue='rate',
                          palette='tab10')

        plot.savefig(f'throughput_{alpha}.png')

        plot = sb.catplot(df.query(f'station == "{alpha}"'),
                          kind='bar',
                          x='topology',
                          y='fairness',
                          hue='rate',
                          palette='tab10')

        plot.savefig(f'fairness_{alpha}.png')

    plot = sb.catplot(df,
                      kind='bar',
                      x='topology',
                      y='ap_collisions',
                      hue='rate',
                      palette='tab10')

    plot.savefig('ap_collisions.png')

    plot = sb.catplot(df,
                      kind='bar',
                      x='topology',
                      y='station_collisions',
                      hue='rate',
                      palette='tab10')

    plot.savefig('station_collisions.png')

    print('Script complete.')


if __name__ == '__main__':
    main()
