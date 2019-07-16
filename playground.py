import numpy as np
import matplotlib.pyplot as plt

height = 2
spread = 5
x_pos = 20
x = np.arange(0, 100, 1)
y = np.exp(-((x-x_pos)/(spread*height))**2)*height
y2 = np.exp(-((x-x_pos)/(8*height))**2)*height


plt.plot(x, y)
plt.plot(x, y2)
plt.show()