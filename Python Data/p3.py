import pandas as pd
import numpy as np
import json
# from pandas.io.json import json_normalize

'''
frame = pd.DataFrame(np.arange(16).reshape(4,4),
                     index=['white','black','red','blue'],
                     columns=['up','down','right','left'])

frame.to_json('frame.json')


df = pd.read_json('frame.json')
print(df)
'''
# pd.json_normalize(...)
file = open('books.json','r')
text = file.read()
text = json.loads(text)
# print(text)
print(pd.json_normalize(text,'books'))
# print(pd.json_normalize(text,'writer'))
print(pd.json_normalize(text,'books',['writer','nationality']))