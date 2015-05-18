#!/usr/bin/python

import argparse
import random
from ea.config import Configuration, GLOBAL_SECTION
from ea.bootstrap import Bootstrap
from ea.evolution import evo_loop

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The configuration filename")
    parser.add_argument("--create", action='store_true',
            help="Create a default configuration file")
    parser.add_argument("--wait", action='store_true',
            help="The argument tells the system whether or not to wait when it is done")
    return parser

def main(config_filename=None, config_parameters=None, create_configfile = False, wait_on_completion=False):
    #Create configuration:
    
    config = Configuration(config_filename, create_configfile).get_config()
    config.set(GLOBAL_SECTION,"config_filename",config_filename)
    
    if config_parameters is not None:
        for section, parameter_name, parameter_value in config_parameters:
            config.set(section, parameter_name, parameter_value)
            
    seed = config.get(GLOBAL_SECTION, "seed")
    random.seed(seed)
    
    
    boot = Bootstrap(config)
    replace, pop, logger, loops = boot.run()
    evo_loop(pop, replace, logger, wait_on_completion, loops)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    config_filename = args.file
    main(config_filename=config_filename, create_configfile=args.create, wait_on_completion=args.wait)
