import numpy as np

a = np.array(['a', 'b', 'c'])
b = np.array([4, 5, 6])
c = np.array([7, 8, 9])
result = np.dstack((a,b,c)).flatten()

print(result)