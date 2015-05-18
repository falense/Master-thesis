
#!/usr/bin/python

from BasePheno import BasePhenotype

from math import cos, sin, acos, asin, pow, sqrt
def degToRad(deg):
	return deg/360.0 * 3.14*2
class Phenotype(BasePhenotype):
    def __init__(self,genome):
        super(Phenotype,self).__init__(genome)
    def __convert_receiver_to_path(self,receiver):
        positions = []
        x = receiver[0]
        y = receiver[1]
        previous = 0
        for angle in receiver[2:]:
            vector = (cos(degToRad(previous+angle)),sin(degToRad(previous+angle)))
            abs_vector = sqrt(vector[0]**2 + vector[1]**2)
            
            x += vector[0]/abs_vector * 50
            y += vector[1]/abs_vector * 50
            positions.append((x,y))
            previous += angle
        return positions
    def get_receiver_origin(self,index):
        return self.genome.settings.base_positions[index][0]
    def get_receiver_path(self,index):
        return self.__convert_receiver_to_path(self.receiver_set[index])
    def get_receiver_fixed_path(self,index):
        return self.genome.settings.base_positions[index][1:]
    def get_receiver_count(self):
        return len(self.receiver_set)
    def get_receiver_step_count(self):
        return self.genome.settings.get_receiver_step_count()
    def get_position(self,max_steps=None):
        positions = []
        for index,receiver in enumerate(self.receiver_set):
            path = []
            p = self.__convert_receiver_to_path(receiver)
            path.extend(p)
            p  = self.genome.settings.base_positions[index]
            if len(p) > 1:
                path.extend(p[1:])
                
            if max_steps is None:
                positions.extend(path)
            else:
                positions.extend(path[:max_steps])
        return positions
    def combine(self,other):
        child1, child2 = self.genome.combine(other.get_genome())
        return Phenotype(child1),Phenotype(child2)

