from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# Two example plots
fig = plt.figure()
ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)

spacing = 0.1 # This can be your user specified spacing. 
minorLocator = MultipleLocator(spacing)
ax1.plot(9 * np.random.rand(10))
# Set minor tick locations.
ax1.yaxis.set_minor_locator(minorLocator)
ax1.xaxis.set_minor_locator(minorLocator)
# Set grid to use minor tick locations. 
ax1.grid(which = 'minor')
ax1.grid(which = 'major')

spacing = 1
minorLocator = MultipleLocator(spacing)
ax2.plot(9 * np.random.rand(10))
# Set minor tick locations.
ax2.yaxis.set_minor_locator(minorLocator)
ax2.xaxis.set_minor_locator(minorLocator)
# Set grid to use minor tick locations. 
ax2.grid(which = 'minor')
ax2.grid(which = 'major')

plt.show()