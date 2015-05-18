#!/usr/bin/python

import logging
import random
from ConfigParser import SafeConfigParser

#Section identifiers:
GLOBAL_SECTION = "Global"
LOGGING_SECTION = "Logging"

#Value identifiers:
LOG_LEVEL = "log_level"
LOGGING_WRITE_MODE = 'write_mode'
LOGGING_FILENAME = 'filename'

class Configuration(object):
    def __init__(self, filename, create=False):
        '''Initialize the configuration object'''
        if create:
            #Create default configuration using
            #the given filename
            self.__create_default(filename)
        #Read configuration
        self.__config = self.__read_config(filename)
        self.__parse_config(self.__config)

    def __parse_config(self, config):
        '''Parse global configuration where possible'''
        self.__parse_logging(config)
        seed = config.getint(GLOBAL_SECTION, 'seed')
        random.seed(seed)

    def __parse_logging(self, config):
        '''Parse the specific logging information in the settings file'''
        lvl = getattr(logging, config.get(GLOBAL_SECTION, LOG_LEVEL).upper())
        if config.has_section(LOGGING_SECTION):
            filename = config.get(LOGGING_SECTION, LOGGING_FILENAME)
            if config.has_option(LOGGING_SECTION, LOGGING_WRITE_MODE):
                write_mode = config.get(LOGGING_SECTION, LOGGING_WRITE_MODE)
            else:
                write_mode = 'a'
            logging.basicConfig(filename=filename, filemode=write_mode,
                    level=lvl)
        else:
            logging.basicConfig(level=lvl)

    def get_config(self):
        return self.__config

    def __create_default(self, filename):
        '''Create a default configuration file'''
        config = SafeConfigParser()
        config.add_section(GLOBAL_SECTION)
        config.set(GLOBAL_SECTION, LOG_LEVEL, 'info')
        self.__write_config(config, filename)

    def __write_config(self, config, filename):
        '''Write a configuration out to the file specified
        in the filename'''
        with open(filename, 'wb') as w:
            config.write(w)

    def __read_config(self, filename):
        '''Read the given configuration file'''
        config = SafeConfigParser()
        config.read(filename)
        return config
