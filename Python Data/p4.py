import pandas as pd
import numpy as np

frame = pd.DataFrame(np.arange(20).reshape(4,5),
                     columns=['Small0','Small1','Small2','Small3','Small4'],
                     index=['Large0','Large1','Large2','Large3']) # ,'Large4'])
                        
print(frame)
large = 2
small = 3
print(frame.iat[large, small])

''''''
df1 = pd.DataFrame(np.arange(20).reshape(4,5),
                   columns=['Small0','Small1','Small2','Small3','Small4'])

print(df1)
results = [15,16,17,18]
print(len(df1.index))   # number of rows in table
print(len(df1.columns)) # number of columns in table
for x in range(len(df1.index)):
    # print(x)
    sources = df1.iloc[x].to_list() # get a row and convert to list
    if results == sources[0:(len(df1.columns)-1)]:
        print("equal and value is: " + str(sources[(len(df1.columns)-1)]))
        break
    #else:
        #print("not equal")
    

# print(results)
# print(sources)
# print(sources[0:4])
'''
if results == sources[0:4]:
    print("equal and value is: " + str(sources[4]))
else:
    print("not equal")
    
'''
#print(df1.[0])