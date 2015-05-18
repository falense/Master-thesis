


import yaml
class BaseConf(object):
        
    emitter_position = (330.0,330.0)
    noise_stddev = 1.0
    step_size = (256,256)
    grid = (1000.0,1000.0)

    num_trials = 100
    NUM_UAVS = 4
    NUM_STEPS = 4
    BASE_POSITION = [670.0,670.0]

    NGEN = 1000
    MU = 200
    LAMBDA = 100
    CXPB = 0.7
    MUTPB = 0.1
    
    fixed_step = False
    fixed_uav_count = True
    
    uav_max_step_length = 450/NUM_STEPS
    label_objective = None
    
    def save(self,filename):
        attributes = [attr for attr in dir(self) if not callable(getattr(self,attr)) and not attr.startswith("__")]
        
        data = [(v, getattr(self,v)) for v in attributes]
        data_dict = dict(data)
        
        f = open(filename, "w")
        yaml.dump(data_dict,f)
        f.close()
    def load(self, filename):
        f = open(filename,"r")
        data_dict = yaml.load(f)
        f.close()
        
        for key, value in data_dict.items():
            setattr(self,key,value)
        
