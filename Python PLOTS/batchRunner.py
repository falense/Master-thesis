

from plotfitness_emitter import main as main_em
from plotfitness_receiver import main as main_recv
from plotfitness_direction import main as main_dir
from time import sleep

production = True

if production:
    print "Warning running in production mode. This will take a long time"
    sleep(1)
    num_steps = [1,1]
else:
    num_steps = [5,5]

def run_pltfit_emitter():
    for radius in xrange(200,350,50):
        main_em(1.5, 40, 3, radius, None, [1000,1000], num_steps, "PltFit Emitter UAV radius %s," % radius)

def run_pltfit_receiver():
    for uav_count in xrange(2,6):
        for noise_step in xrange(5):
            main_recv(0.5 + noise_step, 40, uav_count, 400, None, [1000,1000], num_steps, "PltFit Receiver UAV count %s," % uav_count)

def high_res():
    #main_em(1.5, 40, 3, 200, None, [1000,1000], [1,1], "PltFit Emitter UAV count %s," % 3)
    for uav_count in xrange(2,6):
        for noise_step in xrange(5):
            if uav_count < 3 and noise_step < 3:
                continue
            main_recv(0.5 + noise_step, 40, uav_count, 400, None, [1000,1000], [1,1], "PltFit Receiver UAV count %s," % uav_count)

def run_pltfit_direction():
    for uav_count in xrange(3,5):
        main_dir(1.0, (670.0,670.0), uav_count, 1000, 3, 50, 1, 2, None, "PltFit Direction")

    
if __name__=="__main__":
    run_pltfit_emitter()
    #run_pltfit_receiver()
    #run_pltfit_direction()
