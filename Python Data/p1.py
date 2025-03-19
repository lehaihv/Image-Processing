from functools import reduce
import pandas as pd
import numpy as np

''''''
dict = {'name':'William', 'age':25, 'city':'London', 'name1':'Peter'}

#print(dict["name"])

for key, value in dict.items():
    print(key,value)

for value in dict.values():
    print(value)

''''''
items = [1,2,3,4,5]
for i in items:
    print(i + 1)

''''''
def inc(x): 
    return x+1

new_items = list(map(inc,items))
print(new_items)
for i in new_items:
    print(i)

''''''
print(list(map((lambda x: x+1),new_items)))

''''''
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x**2, numbers))
print(squares)  # Output: [1, 4, 9, 16, 25]

even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)  # Output: [2, 4]

points = [(6, 5), (3, 9), (2, 8)]
sorted_points = sorted(points, key=lambda p: p[0])
print(sorted_points) # Output: [(3, 2), (1, 5), (2, 8)]

''''''
print(reduce((lambda x,y: x/y), items))

''''''
a = np.array([1, 2, 3])
print(a)
print(type(a))

''''''
e = np.array([(1, 2, 3), [4, 5, 6], (7, 8, 9), (7, 8, 9)])
print(e)
print(e.shape)

''''''
print('---------------------------------------------------------')
mydict = {'red': 2000, 'blue': 1000, 'yellow': 500, 'orange': 1000}
myseries = pd.Series(mydict)
print(myseries)

''''''
print('---------------------------------------------------------')
''''''
print('---------------------------------------------------------')

''''''
print('---------------------------------------------------------')
''''''
print('---------------------------------------------------------')
''''''
print('---------------------------------------------------------')
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
''''''
