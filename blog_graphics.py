import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

gamma = 1
val = np.array([0,0,0,0,0,0,0]).reshape(1,7)

np.random.seed(0)
sns.set()

# plt.figure(figsize=(10,1))

ax = sns.heatmap(val,
                cmap=ListedColormap(['white']),
                linewidths=1,
                linecolor='black',
                cbar=False,
                square=True,
                annot=np.array([-1,0,0,0,0,0,10]).reshape(1,7),
                yticklabels=False)
ax.set_xticklabels([1,2,3,4,5,6,7])
for _,spine in ax.spines.items():
    spine.set_visible(True)

plt.show()