import numpy as np
import pandas as pd
from materials import *

ratios = generate_ratios(10)

#r = [{'element': 'earth', 'bonus_stat': 'hardness', 'extra': 20., 'ratio': .5}]

fe = Metal(.4, .02, .2, 0, .1)
pb = Metal(.1, .03, 1, .2, .05)
s = Weapon(fe, .2)

f = np.linspace(0, 1, 100)
b = [fe.alloy_bonus(pb, x, 'earth', 4, 5) for x in f]

v = alloy_experiment(fe, pb, r)

#plt.plot(f, b)
#plt.show()