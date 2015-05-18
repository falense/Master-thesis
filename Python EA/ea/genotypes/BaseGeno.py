
#!/usr/bin/python

FITNESS_SECTION = 'Fitness'
GENOTYPE_SECTION = 'Genotype'
GLOBAL_SECTION = 'Global'



class BaseSettings(object):
    def parse_emitter(self,config):
        x = config.getint(FITNESS_SECTION, 'emitter_pos_x')
        y = config.getint(FITNESS_SECTION, 'emitter_pos_y')
        self.emitter = (x,y);
    def parse_base_pos(self,config):
        x = config.getint(GENOTYPE_SECTION, 'base_pos_x')
        y = config.getint(GENOTYPE_SECTION, 'base_pos_y')
        self.base_pos = (x,y)
    def __init__(self,config):
        self.parse_emitter(config)
        self.parse_receiver_freedom(config)
        self.parse_base_pos(config)
        self.num_receivers = config.getint(GLOBAL_SECTION, 'num_receivers')
    def get_num_receivers(self):
        return self.num_receivers
    def get_emitter(self):
        return self.emitter;
    def get_base_pos(self):
        return self.base_pos
    def get_mutation_rate(self):
        return self.mutation_rate
class BaseGenotype(object):
    def __init__(self,settings,receiver_set):
        self.settings = settings
        self.receiver_set = receiver_set
        
    def serialize(self):
        r = []
        for receiver in self.receiver_set:
            for value in receiver:
                r.append(value)
        return r
    def get_receiver_set(self):
        return self.receiver_set
    def get_emitter(self):
        return self.settings.get_emitter()
    def get_base_pos(self):
        return self.settings.get_base_pos()
