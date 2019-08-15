import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_ratios(number):
    elements = ['fire', 'air', 'earth', 'water', 'spirit']
    stats = ['density', 'durability', 'hardness', 'meltability']
    means = [4, .2, .2, 0 ]
    stds = [8, .3, .3, 200]
    output = []
    for i in range(number):
        new_dict = {}
        new_dict['element'] = np.random.choice(elements)
        num = int(np.random.randint(0, len(stats)-1, 1))
        new_dict['bonus_stat'] = stats[num]
        new_dict['extra'] = np.random.normal(means[num], stds[num])
        new_dict['ratio'] = np.random.rand()
        output += [new_dict]
    return output


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

    def __init__(self, fire=0, air=0, earth=0, water=0, spirit=0, alloy_bonuses={}):
        self.makeup = pd.Series([fire, air, earth, water, spirit], index=['fire', 'air', 'earth', 'water', 'spirit'])
        self.relative_makeup = self.makeup/self.makeup.sum()
        self.alloy_bonuses = alloy_bonuses

    @property
    def density(self):
        base = (self.relative_makeup*self.base_props['density']).sum()*self.max_density
        bonus = self.alloy_bonuses.get('density', 0)
        return base + bonus

    @property
    def durability(self):
        base = (self.relative_makeup * self.base_props['durability']).sum() * self.max_durability
        bonus = self.alloy_bonuses.get('durability', 0)
        return base + bonus

    @property
    def hardness(self):
        base = (self.relative_makeup * self.base_props['hardness']).sum() * self.max_hardness
        bonus = self.alloy_bonuses.get('hardness', 0)
        return base + bonus

    @property
    def melting_point(self):
        melt = 1 - (self.relative_makeup * self.base_props['meltability']).sum()
        bonus = self.alloy_bonuses.get('meltability', 0)
        return (self.max_melt - self.min_melt) * melt + self.min_melt + bonus

    def similarity(self, other_metal):
        return 2-((self.relative_makeup - other_metal.relative_makeup)**2).sum()

    def miscible(self, other_metal, first_frac=.5):
        if self.similarity(other_metal) > min(first_frac, 1-first_frac):
            return True
        else:
            return False

    def combine(self, other_metal, first_frac=.5, ratios=[]):
        if self.miscible(other_metal, first_frac):
            new_amounts = first_frac*self.makeup + (1-first_frac)*other_metal.makeup
            return Metal(**dict(new_amounts),
                         alloy_bonuses=self._find_alloy_bonuses(
                             other_metal, first_frac, ratios))
        else:
            raise Immiscible(f'These two metals may not be mixed with a ratio of {first_frac:.3}:{1-first_frac:.3}')

    def _find_alloy_bonuses(self, other_metal, first_frac, ratios):
        """Determine the property bonuses that would be produced by combining the two
        metals.

        Args:
            other_metal (Metal): Second metal being combined.
            first_frac (float): Fraction of the alloy that metal 1 comprises.
            ratios (list): Element ratios and the bonuses they provide.
        """
        alloy_bonuses = {}
        for bonus in ratios:
            bonus_amount = self.alloy_bonus(
                other_metal, first_frac, bonus['element'], bonus['ratio'], bonus['extra'])
            stat = bonus['bonus_stat']
            alloy_bonuses[stat] = alloy_bonuses.get(stat, 0) + bonus_amount
        return alloy_bonuses

    def proximity(self, target, broadness, value):
        return np.exp(-(target-value)**2/broadness)

    def alloy_bonus(self, other_metal, first_frac, element, ratio, extra):
        if other_metal.makeup[element]*(1 - first_frac) == 0:
            return 0
        eratio = self.makeup[element]*first_frac/(other_metal.makeup[element]*(1 - first_frac))
        if eratio == 0:
            return 0

        eratio = max(eratio, 1/eratio)
        val = self.proximity(ratio, .1, eratio)*extra
        return val


def alloy_experiment(first_metal, second_metal, ratios):
    fracs = np.linspace(0, 1, 1000)
    vals = {'density': [], 'durability': [], 'hardness': [], 'melting_point': []}
    for f in fracs:
        alloy = first_metal.combine(second_metal, f, ratios)
        vals['density'] += [alloy.density]
        vals['durability'] += [alloy.durability]
        vals['hardness'] += [alloy.hardness]
        vals['melting_point'] += [alloy.melting_point]
    fig, axs = plt.subplots(2,2)
    for i, k in enumerate(vals.keys()):
        ax = axs[i//2, i%2]
        ax.plot(fracs, vals[k])
        ax.set_ylabel(k)
    plt.show()


class Immiscible(Exception):
    """Raised when two metals are immiscible at a given ratio."""
