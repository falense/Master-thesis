
#!/usr/bin/python

from BasePheno import BasePhenotype
from math import cos, sin

class Phenotype(BasePhenotype):
    def __init__(self,genome):
        super(Phenotype,self).__init__(genome)
    def get_position(self):
        rset = self.genome.get_receiver_set()
        base_pos = self.genome.get_base_pos()
        receiver_set = []
        for r,th in rset:
            t = (cos(th)*r+base_pos[0],sin(th)*r+base_pos[1])
            receiver_set.append(t)
        return receiver_set
    def combine(self,other):
        child1, child2 = self.genome.combine(other.get_genome())
        return Phenotype(child1),Phenotype(child2)
