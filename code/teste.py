
import numpy as np
import matplotlib.pyplot as plt

spike = [1,2,3,5,8,10]
plt.eventplot(spike, 
              orientation = 'vertical',
              linelengths = 0.8, 
              color = [(0.5,0.5,0.8)])
plt.show()