
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt 
from Environment import Environment
from nllsCuda import pyPredict
import os
import datetime
import json
import shutil

from matplotlib.patches import Rectangle, Circle, RegularPolygon, Arrow
from bootstrap import convert_ind_to_positions,convert_ind_to_distance,convert_ind_to_uav_count


def make_emitter_patch(grid,emitter_position):
    s = (grid[0] + grid[1])/2.0 * 0.008
    c = RegularPolygon(emitter_position, 4, s, 3.14/2.0,facecolor='r',edgecolor='k',alpha=0.8)
    return c
def make_receiver_patch(grid,x,y,color='b'):
    s = (grid[0] + grid[1])/2.0 * 0.005
    c = Circle((x,y),s,facecolor=color,edgecolor='k',alpha=0.6)
    return c
def make_prediction_patch(grid,x,y):
    s = (grid[0] + grid[1])/2.0 * 0.003
    c = Circle((x,y),s,facecolor='k',edgecolor='k',alpha=0.2)
    return c
def make_receiver_path(from_x,from_y,to_x,to_y):
    c = Arrow(from_x,from_y,to_x-from_x,to_y-from_y,width=1.0, alpha=0.2)
    return c




class PhenoView(object):   
    subfolder = "Pheno_view"
    def __init__(self,conf,index=0,hidden=False):
        
        self.conf = conf
        self.index = index
        
        plt.figure(2+self.index,figsize=(8, 8))
        plt.clf()
        
        text = "Phenome"
        plt.gcf().canvas.set_window_title(text)
        
        self.view = plt.gcf().gca()
        self.view_ax = plt.gca()
        self.setup_view()
        
    def setup_view(self):
        self.view.set_xlabel("X-axis")
        self.view.set_ylabel("Y-axis")
        self.view_ax.axis([0,self.conf.grid[0],0,self.conf.grid[1]])
        self.view_ax.set_aspect('equal')
        self.view.grid(b=True)
    def simulate_predictions(self,positions,num_trials):
        env = Environment(self.conf.emitter_position,10.0,self.conf.noise_stddev)

        samples = []
        for trial in xrange(num_trials):
            t = []
            for position in positions:
                x,y = position
                t.append((x,y,env.MeasuredPower(x,y)))
            samples.append(t)
            
            
        results = pyPredict(samples,[256,256],self.conf.grid)

        return results

    def plot_pheno(self,view,grid,emitter_position,positions):

        c1 = make_emitter_patch(self.conf.grid,self.conf.emitter_position)
        view.add_artist(c1)
        
        for index in xrange(self.conf.NUM_UAVS):
            
            p_x, p_y = self.conf.BASE_POSITION
            
            c0 = make_receiver_patch(self.conf.grid,p_x,p_y, color = (0.0,1.0,0.5))
            view.add_artist(c0)
            
            for position in positions[index*self.conf.NUM_STEPS:(index+1)*self.conf.NUM_STEPS]:
                x,y = position
                c1 = make_receiver_patch(self.conf.grid,x,y)
                view.add_artist(c1)
                if p_x is not None and  p_y is not None:
                    c2 = make_receiver_path(p_x,p_y,x,y)
                    view.add_artist(c2)
                p_x, p_y = x,y
    def update(self,gen,pop,hof):
        if gen%100 != 0:
            return
        
        plt.figure(2+self.index)
        plt.cla()
        self.setup_view()
        try:
            individual = hof[self.index]
        except:
            return
            
        positions = convert_ind_to_positions(self.conf,individual)

        predictions = self.simulate_predictions(positions,1000)

        for x,y in predictions:
            c = make_prediction_patch(self.conf.grid,x,y)
            self.view.add_artist(c)


        self.plot_pheno(self.view,self.conf.grid,self.conf.emitter_position,  positions)

        text = "%s: %s" % (self.conf.label_objective,round(individual.fitness.values[1],2))
        self.view_ax.text(0.05, 0.94, text,
            verticalalignment='bottom', horizontalalignment='left',
            transform=self.view_ax.transAxes,
            color='green', fontsize=15)
            
        text = "Deviation (m): %s" % round(individual.fitness.values[0],2)
        self.view_ax.text(0.05, 0.89, text,
            verticalalignment='bottom', horizontalalignment='left',
            transform=self.view_ax.transAxes,
            color='green', fontsize=15)

        c1 = make_emitter_patch(self.conf.grid,[0,0])
        rp = make_receiver_patch(self.conf.grid,0,0)
        plt.legend([c1, rp], ["Emitter", "Receiver"],loc=4)
        
        #text = "Fitness: " + str(round(best.fitness(),2))
        #plt.text(0.85,0.95,text, horizontalalignment='center', verticalalignment='center',transform=self.bpf_predictions_ax.transAxes)
        plt.draw()
        
        folder = os.path.join(self.conf.logfolder,self.subfolder,"Generation_%s" % gen)
        if not os.path.exists(folder):
            os.makedirs(folder)   
        plt.savefig(os.path.join(folder, "Pareto_%s.png" % self.index))
      
            
class ParetoView(object):
    subfolder = "Pareto_view"
    def __init__(self,conf):
        plt.figure(1)
        plt.clf()
        
        self.conf = conf
        self.lim_axis = None
        
        self.view = plt.gcf().gca()
        self.view_ax = plt.gca()
        
    def setup_view(self):
        self.view.set_ylabel("Deviation (m)")
        self.view.set_xlabel(self.conf.label_objective)
        self.view_ax.axis([0,self.lim_axis[0],0,self.lim_axis[1]])
        self.view.grid(b=True)
        
    def update(self,gen,pop,hof):
        plt.figure(1)
        
        self.view.cla()
        
        results =  [i.fitness.values for i in hof]
        data_x = map(lambda x: x[1],results)
        data_y = map(lambda x: x[0],results)
        
        if self.lim_axis is None:
            self.lim_axis = (max(data_x)*2,max(data_y)*2)
        
        
        self.setup_view()
        
        self.view.plot(data_x, data_y)
        
        plt.draw()
        folder = os.path.join(self.conf.logfolder, self.subfolder)
        if not os.path.exists(folder):
            os.makedirs(folder)   
        plt.savefig(os.path.join(folder,"Paretofront_%s.png"%gen))

class Progress(object):
    def __init__(self, conf):
        plt.close("all")
        
        self.conf = conf
        self.views = []
        self.num_pheno_views = 0
        
        view = ParetoView(conf)
        self.views.append(view)
        
        self.conf.experiment_name = str(datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S"))
        
        self.conf.logfolder = os.path.join("experiments", self.conf.experiment_name)
        if not os.path.exists(self.conf.logfolder):
            os.makedirs(self.conf.logfolder)   
            
        self.pop_dump_folder = os.path.join(self.conf.logfolder, "Population_dump")
        
        if not os.path.exists(self.pop_dump_folder):
            os.makedirs(self.pop_dump_folder)   
            
        config_filename = os.path.join(self.conf.logfolder, "%s.yaml" % self.conf.name)
        self.conf.save(config_filename)
        #plt.ion()
        #plt.show()
    def update_pareto_count(self,hof):
        if len(hof) > self.num_pheno_views:
            for x in xrange(len(hof)-self.num_pheno_views):
                view = PhenoView(self.conf, self.num_pheno_views,hidden=True)
                self.views.append(view)
                self.num_pheno_views += 1
    def update(self,gen,pop,hof):   
        self.update_pareto_count(hof)
        print "Increase size to ", len(hof)
        for view in self.views:
            view.update(gen,pop,hof)
        self.dump_population(gen,pop,hof)
    def dump_population(self,gen,pop,hof):
        population_file = os.path.join(self.pop_dump_folder, "generation_%s.txt" % gen)
        paretofront_file = os.path.join(self.pop_dump_folder, "paretofront_%s.txt" % gen)
        
        f = open(population_file,"w")
        for individual in pop:
            d = json.dumps(individual)
            f.write(d + "\n")
        f.close()
        
        f = open(paretofront_file,"w")
        for individual in hof:
            d = json.dumps(individual)
            f.write(d + "\n")
        f.close()
            
        
        
            
    def hold(self):
        plt.ioff()
        plt.show()
