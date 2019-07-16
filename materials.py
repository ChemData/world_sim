import numpy as np
import pandas as pd


class Weapon:
    """Typical sizes (in liters):
        long sword - 0.2
        gladius - 0.1
        war hammer - 0.125
        dagger - 0.025
    """

    def __init__(self, metal, size):
        self.metal = metal
        self.size = size
        self.weight = self.size * self.metal.density

    @property
    def lifetime(self):
        return 1

    @property
    def attack_time(self):
        return 1

    @property
    def pierce_damage(self):
        return round(self.metal.hardness * 50)

    @property
    def crushing_damage(self):
        return round(.2 * self.weight * self.metal.density + self.metal.hardness * 10)


class Metal:
    base_props = pd.read_csv('material_properties.txt', index_col=0)
    max_density = 20 #g/ml
    max_durability = 1
    max_hardness = 1
    min_melt = 200
    max_melt = 3000
    max_diff = .4

    def __init__(self, fire=0, air=0, earth=0, water=0, spirit=0):
        self.makeup = pd.Series([fire, air, earth, water, spirit], index=['fire', 'air', 'earth', 'water', 'spirit'])
        self.relative_makeup = self.makeup/self.makeup.sum()

    @property
    def density(self):
        return (self.relative_makeup*self.base_props['density']).sum()*self.max_density

    @property
    def durability(self):
        return (self.relative_makeup * self.base_props['durability']).sum() * self.max_durability

    @property
    def hardness(self):
        return (self.relative_makeup * self.base_props['hardness']).sum() * self.max_hardness

    @property
    def melting_point(self):
        melt = 1 - (self.relative_makeup * self.base_props['meltability']).sum()
        return (self.max_melt - self.min_melt) * melt + self.min_melt

    def similarity(self, other_metal):
        return 2-((self.relative_makeup - other_metal.relative_makeup)**2).sum()

    def miscible(self, other_metal, first_frac=.5):
        if self.similarity(other_metal) > min(first_frac, 1-first_frac):
            return True
        else:
            return False

    def combine(self, other_metal, first_frac=.5):
        if self.miscible(other_metal, first_frac):
            new_amounts = first_frac*self.makeup + (1-first_frac)*other_metal.makeup
            return Metal(**dict(new_amounts))
        else:
            raise Immiscible(f'These two metals may not be mixed with a ratio of {first_frac:.3}:{1-first_frac:.3}')

    def proximity(self, target, broadness, value):
        return np.exp(-(target-value)**2/broadness)


class Immiscible(Exception):
    """Raised when two metals are immiscible at a given ratio."""




st = Metal(.4, 0, .2, 0, 0)
pb = Metal(0, 0, 1, 0, 0)
s = Weapon(st, .2)