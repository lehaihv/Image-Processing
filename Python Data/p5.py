import numpy as np
import pandas as pd

df1 = pd.DataFrame({'id':['ball','pencil','pen','mug','ashtray'],
                    'color': ['white','red','red','black','green']})

print(df1)

df2 = pd.DataFrame({'id':['pencil','pencil','ball','pen'],
                    'color': ['white','red','red','black']})

print(df2)
print(pd.merge(df1,df2))

print(pd.merge(df1,df2,on=['id','color']))#,right_on='color'))