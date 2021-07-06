import numpy as np
import pandas as pd
from collections import Counter
from random import shuffle





np_load_old = np.load

    # modify the default parameters of np.load
np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)

train_data = np.load('training_data.npy')
np.load = np_load_old

# df = pd.DataFrame(train_data)
# print(df.head())
# print(Counter(df[1].apply(str)))

lefts = []
rights = []
forwards = []
brakes =[]

#shuffle(train_data)

for data in train_data:
    img = data[0]
    choice = data[1]

    if choice[0] == 1:
        forwards.append([img,choice])
    elif choice[1] ==1:
        lefts.append([img,choice])
    elif choice[2] == 1:
        brakes.append([img,choice])
    elif choice[3] == 1:
        rights.append([img,choice])
    else:
        print('no matches')

length = min(len(forwards),len(rights),len(lefts))
forwards = forwards[:length]
lefts = lefts[:length]
rights = rights[:length]

print(length)

final_data = forwards + lefts + rights+brakes
#shuffle(final_data)

np.save('training_datav2.npy', final_data)