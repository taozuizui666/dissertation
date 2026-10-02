import pandas as pd
import numpy as np
from tqdm import tqdm
import time

# data = np.round(np.random.random(100),4)
# data = data.reshape(-1,10)
# pd.DataFrame(data=data).to_csv('ran.csv',sep=',',index=False) #header=False

# df = pd.read_csv('ran.csv')
# # print(df.info())
# print(df[['2','3']])
# print(df.iloc[2:4])
# cc = df[df['2']>0.5]
# print(cc) 
for i in tqdm(range(100)):
    time.sleep(0.1) 
    
      