#!/usr/bin/python


from matplotlib.patches import Rectangle, Circle, RegularPolygon, Arrow
from fitness import FITNESS_SECTION

class BasicDrawing(object):
    def __init__(self,config):
        self.config = config
        
        self.grid_x = self.config.getint(FITNESS_SECTION,"grid_x")
        self.grid_y = self.config.getint(FITNESS_SECTION,"grid_y")
        
        self.emitter_x = self.config.getint(FITNESS_SECTION,"emitter_pos_x")
        self.emitter_y = self.config.getint(FITNESS_SECTION,"emitter_pos_y")
        
    def make_emitter_patch(self):
        s = (self.grid_x + self.grid_y)/2.0 * 0.008
        c = RegularPolygon((self.emitter_x,self.emitter_y), 4, s, 3.14/2.0,facecolor='r',edgecolor='k',alpha=0.8)
        return c
    def make_receiver_patch(self,x,y,color='b'):
        s = (self.grid_x + self.grid_y)/2.0 * 0.005
        c = Circle((x,y),s,facecolor=color,edgecolor='k',alpha=0.6)
        return c
    def make_prediction_patch(self,x,y):
        s = (self.grid_x + self.grid_y)/2.0 * 0.003
        c = Circle((x,y),s,facecolor='k',edgecolor='k',alpha=0.2)
        return c
    def plot_pheno(self,view,pheno,**args):
        c1 = self.make_emitter_patch()
        view.add_artist(c1)
        for position in pheno.get_position():
            try:
                x,y,z = position
            except ValueError:
                x,y = position
            c1 = self.make_receiver_patch(x,y)
            view.add_artist(c1)

class PathDrawing(BasicDrawing):
    def make_receiver_path(self,from_x,from_y,to_x,to_y, alpha=0.2):
        c = Arrow(from_x,from_y,to_x-from_x,to_y-from_y,width=1.0, alpha=alpha)
        return c
    def plot_pheno(self,view,pheno,draw_points=True, draw_lines=True):
        c1 = self.make_emitter_patch()
        view.add_artist(c1)
        
        
        
        for index in xrange(pheno.get_receiver_count()):
            
            p_x, p_y = pheno.get_receiver_origin(index)
            
            c0 = self.make_receiver_patch(p_x,p_y, color = (0.0,1.0,0.5))
            view.add_artist(c0)
            
            for position in pheno.get_receiver_path(index):
                x,y = position
                if draw_points:
                    c1 = self.make_receiver_patch(x,y)
                    view.add_artist(c1)
                if p_x is not None and  p_y is not None and draw_lines:
                    c2 = self.make_receiver_path(p_x,p_y,x,y)
                    view.add_artist(c2)
                p_x, p_y = x,y


   
class PathIncrDrawing(PathDrawing):
    def plot_pheno(self,view,pheno,draw_points=True, draw_lines=True):
        c1 = self.make_emitter_patch()
        view.add_artist(c1)
        for index in xrange(pheno.get_receiver_count()):
            
            p_x, p_y = pheno.get_receiver_origin(index)
            
            c0 = self.make_receiver_patch(p_x,p_y, color = (0.0,1.0,0.5))
            view.add_artist(c0)
            
            for position in pheno.get_receiver_fixed_path(index):
                x,y = position
                
                if draw_points:
                    c1 = self.make_receiver_patch(x,y,color=(1.0,0.3,0))
                    view.add_artist(c1)
                if p_x is not None and  p_y is not None and draw_lines:
                    c2 = self.make_receiver_path(p_x,p_y,x,y)
                    view.add_artist(c2)
                p_x, p_y = x,y    
            
            
            for position in pheno.get_receiver_path(index):
                x,y = position
                if draw_points:
                    c1 = self.make_receiver_patch(x,y)
                    view.add_artist(c1)
                if p_x is not None and  p_y is not None and draw_lines:
                    c2 = self.make_receiver_path(p_x,p_y,x,y)
                    view.add_artist(c2)
                p_x, p_y = x,y
