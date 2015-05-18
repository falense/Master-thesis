
#!/usr/bin/python

from BasePheno import BasePhenotype


class Phenotype(BasePhenotype):
    def __init__(self,genome):
        super(Phenotype,self).__init__(genome)
    def get_position(self):
        receiver_set = []
        for receiver in self.receiver_set:
            x,y = receiver
            receiver_set.append((x,y))
        return receiver_set

    def combine(self,other):
        child1, child2 = self.genome.combine(other.get_genome())
        return Phenotype(child1),Phenotype(child2)

