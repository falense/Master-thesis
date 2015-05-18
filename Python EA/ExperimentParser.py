

import os
import json
import subprocess
import webbrowser
    
from xlwt import Workbook, easyxf,Formula
import xlwt
from xlwt.Utils import rowcol_to_cell
import ConfigParser

#!/usr/bin/python

import logging
import random
from ConfigParser import SafeConfigParser

#Section identifiers:
GLOBAL_SECTION = "Global"
FITNESS_SECTION = "Fitness"
GENOTYPE_SECTION = "Genotype"
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



class Experiment(object):
    def get_config_filename(self):
        for path in os.listdir(self.experiment_folder):
            try:
                filename, filetype = path.split(".")
                if filetype == "ini":
                    return os.path.join(self.experiment_folder,path)
            except ValueError:
                continue
        return None
    def __init__(self, experiment_folder):
        self.experiment_folder = experiment_folder
        self.config_filename = self.get_config_filename()
        self.config = Configuration(self.config_filename, False).get_config()
    def get_phenome(self, generation, index, sort_key=None, reverse=False):
        
        phenomes = self.get_phenomes(generation, sort_key, reverse)
        if phenomes is None:
            return None
            
        return phenomes[index]

    def simulate_phenome(self, generation, index):
        grid_size = (self.config.getfloat(FITNESS_SECTION, "grid_x"),self.config.getfloat(FITNESS_SECTION, "grid_y"))
        emitter_position = (self.config.getfloat(FITNESS_SECTION, "emitter_pos_x"),grid_size[1]-self.config.getfloat(FITNESS_SECTION, "emitter_pos_y"))
        noise_stddev = 1.0
        phenome = self.get_phenome(generation, index, "FITNESS",True)
        
        receiver_positions = map(lambda x: (x[0],grid_size[1]-x[1]), phenome['decoded_positions'])
        
        run(grid_size, emitter_position, noise_stddev, receiver_positions)
        
        
    def get_phenomes(self, generation, sort_key=None, reverse=False):
        population_filename = os.path.join(self.experiment_folder, "population_dump", "generation_" + str(generation) + ".txt")
        if not os.path.exists(population_filename):
            return None
        
        f = open(population_filename)
        population_text = f.readlines()
        f.close()
        
        def get_key(item):
            return item[sort_key]
        phenomes = map(lambda x: json.loads(x), population_text)
        
        if sort_key is not None:
            return sorted(phenomes, key=get_key, reverse=reverse)
        else:
            return phenomes
    def get_option(self, key, section = None):
        if section is None:
            for section_t in self.config.sections():
                if self.config.has_option(section_t, key):
                    section = section_t
            
        try:
            return self.config.getfloat(section, key)
        except ConfigParser.NoSectionError:
            return None
        except: 
            return self.config.get(section, key)
    def __repr__(self):
        uav_count = self.get_option("num_receivers")
        step_count = self.get_option("receiver_step_count")
        text = "Experiment - %s UAVs - %s steps (%s)" % (uav_count,step_count,self.experiment_folder)
        return text
def open_image(image_path):
    webbrowser.open(image_path)


def load_experiments(experiment_base_folder):

    experiment_folders = os.listdir(experiment_base_folder)
    experiments = []
    for experiment_folder in experiment_folders:
        experiment_folder_abs = os.path.join(experiment_base_folder, experiment_folder)
        if not os.path.isdir(experiment_folder_abs): 
            continue
        #print experiment_folder_abs
        experiment = Experiment(experiment_folder_abs)
        experiments.append(experiment)
        #for gen in xrange(1,101,10):
        #    image_path = os.path.join(experiment_folder_abs, "figure_best_predictions", "generation_" + str(gen) + ".jpg")
         #   open_image(image_path)
        #break

            #for x in xrange(0,1):
              #  phenome = experiment.simulate_phenome(gen, x)

    print "Loaded %s experiments" % len(experiments)
    return experiments
def run_simulation(list_experiments, num_uavs, num_steps, generation):
    from pygameSimulator import run
    
    for experiment in list_experiments:
        exp_num_uavs = experiment.config.getint(GLOBAL_SECTION,"num_receivers")
        exp_num_steps = experiment.config.getint(GENOTYPE_SECTION,"receiver_step_count")
        if exp_num_uavs == num_uavs and exp_num_steps == num_steps:
            experiment.simulate_phenome(generation, 0)
            return
    raise Exception("Specified data not found")

def generate_comparison(list_experiments):
    row = easyxf('pattern: pattern solid, fore_colour blue')
    col = easyxf('pattern: pattern solid, fore_colour green')
    header = easyxf('font: bold True; pattern: pattern solid, fore_colour dark_red')
    book = Workbook()
    xlwt.add_palette_colour("dark_red", 0x21)
    book.set_colour_RGB(0x21, 150, 0, 0)
    
    attributes = ['AVG_DEV','MIN_DEV','MAX_DEV','VAR_DEV','FITNESS']
    
    overview_sheets = []
    for attr in attributes:
        sheet1 = book.add_sheet("Overview %s" % attr,cell_overwrite_ok=True)
        overview_sheets.append(sheet1)
        
    
            
    #from random import randint
    #for x in xrange(1, num_uavs+1):
        #for y in xrange(1, num_samples+1):
            #style = None
            #val = x*y
            #if val < 25:
                #style = easyxf('pattern: pattern solid, fore_colour green')
            #elif val < 50:
                #style = easyxf('pattern: pattern solid, fore_colour white')
            #elif val < 75: 
                #style = easyxf('pattern: pattern solid, fore_colour orange')
            #else: 
                #style = easyxf('pattern: pattern solid, fore_colour red')
            #sheet1.write(x,y,str(val),style)
            
    num_uavs = 0
    num_steps = 0
    for experiment in list_experiments:
        exp_num_uavs = experiment.config.getint(GLOBAL_SECTION,"num_receivers")
        exp_num_steps = experiment.config.getint(GENOTYPE_SECTION,"receiver_step_count")
        
        if num_uavs < exp_num_uavs:
            num_uavs = exp_num_uavs
        if num_steps < exp_num_steps:
            num_steps = exp_num_steps
        
        best_phenome = experiment.get_phenome(100,0,"FITNESS",True)
        if best_phenome is None:
            continue
        for attr, sheet in zip(attributes, overview_sheets):
            value = best_phenome[attr]
            value = round(value,2)
            cell_value = None
            image_path = os.path.join(experiment.experiment_folder, "figure_best_predictions", "generation_100.jpg")
            image_path_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path)
            cell_value = Formula('HYPERLINK("file://' + image_path_abs + '";' + str(value) + ')')
            
            sheet.write(exp_num_steps,exp_num_uavs,cell_value)
            
    
    for sheet in overview_sheets:
        sheet.write(0,0,"# samples/UAVs",header)
    
    for x in xrange(1,num_steps+1):
        for sheet in overview_sheets:
            sheet.write(x,0,str(x),header)
    for y in xrange(1,num_uavs+1):
        for sheet in overview_sheets:
            sheet.write(0,y,str(y),header)
    #c = 0
    #for experiment in list_experiments:
        #sheet = book.add_sheet(str(c),cell_overwrite_ok=True)
        #for gen in xrange(11):
            #image_path = os.path.join(experiment.experiment_folder, "figure_best_predictions", "generation_" + str(max(gen*10,1)) + ".jpg")
            #import Image
            #try:
                #im = Image.open("./" + image_path)
                ##open_image(image_path)
                #im.save("temp.bmp", "BMP")
            #except:
                #continue
            
            #sheet.insert_bitmap("temp.bmp", gen*17+1, 0, scale_x = 0.5, scale_y= 0.5)
            
        #c += 1
    book.save(os.path.join(experiment_base_folder,'overview.xls'))
    
def find_experiment(experiments,search_parameters):
    for experiment in experiments:
        match = True
        for key, value in search_parameters:
            option_value = experiment.get_option(key)
            if option_value is None:
                match = False   
                
            if value != option_value:
                match = False
                
            if not match:
                break
        if match:
            return experiment
    return None
                






if __name__=="__main__":
    
    #print find_experiment([("num_receivers",5),("receiver_step_count",2)]).get_phenome(100, 0, "FITNESS",True)
    
    experiment_base_folder = "./"
    experiments = load_experiments(experiment_base_folder)
    generate_comparison(experiments,experiments)
#else:
#    experiment_base_folder = "experiments_ref"
#    load_experiments(experiment_base_folder)
    #run_simulation(experiments, 4, 5, 100)
