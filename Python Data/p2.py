import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import sys
from shapely.geometry import LineString


df = pd.read_excel('Book3.xlsx', index_col ="pH")
#print(df)
#print(df.T)
df1 = df.T
#print(df1)

df2 = pd.DataFrame(df1, columns=['log(LHS)','log(RHS)'])
df2['pH'] = np.arange(15)
print(df2)

'''
# plot multiple columns such as log(LHS) and log(RHS) from dataframe
df2.plot(x="pH", y=["log(LHS)","log(RHS)"], kind="line", figsize=(10, 8))
 
# display plot
plt.grid()
plt.show()
'''

# plot multiple columns such as log(LHS) and log(RHS) from dataframe 
# and look for intersection point between 2 graphs
plt.plot(df2['pH'], df2['log(LHS)'], label='log(LHS)')
plt.plot(df2['pH'], df2['log(RHS)'], label='log(LHS)')

first_line = LineString(np.column_stack((df2['pH'], df2['log(LHS)'])))
second_line = LineString(np.column_stack((df2['pH'], df2['log(RHS)'])))
intersection = first_line.intersection(second_line)

if intersection.geom_type == 'MultiPoint':
    plt.plot(*LineString(intersection).xy, 'ro') # 'o' green; 'bo' blue
elif intersection.geom_type == 'Point':
    plt.plot(*intersection.xy, 'ro') #, label = 'Intersection points')

# display plot
tmp = str(intersection)
print(tmp[7:15])

#adding text inside the plot
plt.text(0, -12.5, intersection, fontsize = 10, c = 'g')
plt.text(0, -13.5, 'pH = ' + tmp[7:15], fontsize = 10, c = 'r')
plt.grid()
plt.xlabel("pH", fontsize = 15)
plt.ylabel("logC",fontsize = 15)
plt.title('Determination of pH based on TOTH and Proton Condition Equation')
plt.legend(loc='center right')
plt.show()
