

import os, os.path
# path joining version for other paths
DIR = 'C:\\Users\\Stefan-PC\\Desktop\\letters'
print(len([name for name in os.listdir(DIR)]))
names = os.listdir(DIR)
print(names)
names = sorted(names, key=lambda x: x[-1])
charaters = []
values = []

for name in names:
    charaters.append(name[-1])
    values.append(len([name for name in os.listdir(DIR+"\\"+name)]))

import matplotlib.pyplot as plt
import numpy as npx

plt.bar(charaters, values,   color='g')
plt.show()