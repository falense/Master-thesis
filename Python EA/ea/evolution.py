#!/usr/bin/python

import logging

def evo_loop(initial_population, replace_protocol, progress, wait=True, nr_loops=100):
    population = initial_population
    log = logging.getLogger('evo')
    for i in range(1, nr_loops + 1):
        if i % 10 == 0:
            log.info('Progress: {0:.0%}'.format(i/float(nr_loops)))
        progress.add(i, population)
        population = replace_protocol.replace_generation(population)
    if wait:
        raw_input("Press any key to continue")
