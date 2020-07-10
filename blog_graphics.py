import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

gamma = 1
val = np.array([-1,0,0,0,0,0,10]).reshape(1,7)

np.random.seed(0)
sns.set()
uniform_data = np.random.rand(10, 12)
print(type(uniform_data))
ax = sns.heatmap(val,
                cmap=ListedColormap(['white']),
                linecolor='black')

plt.show()