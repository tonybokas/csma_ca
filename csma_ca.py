#!/usr/bin/env python

# Authors: Antonios J. Bokas & Jamie Cookson

import random

import numpy as np
import seaborn as sb
from matplotlib import pyplot


# To-do: What is the difference between λ_A and λ_C?

def main():
    # CONSTANTS

    # Network:
    BW = 12 * 10**6   # bandwidth in bits/sec
    FRAME = 1500 * 8  # frame size in bits

    # Slot allocations:
    SLOT = 10                   # micro sec
    ACK = RTS = CTS = SLOT * 3  # acknowledgment, request- and clear-to-send
    DIFS = SLOT * 4             # distributed interframe space
    SIFS = SLOT * 2             # short interframe space
    CW_MAX = SLOT * 1024        # contention window limit

    # Simulation:
    SIM_TIME = 10 * 10**6                       # simulation time in micro sec
    ARRIVALS = [100, 200, 300, 500, 700, 1000]  # arrival rate in frames/sec

    # VARIABLES

    cw = SLOT * 8  # contention window
    throughput, collisions, fairness = 0  # to-do: use None instead?

    example_poisson()


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
