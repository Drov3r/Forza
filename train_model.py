# train_model.py

import numpy as np
from alexnet import alexnet
# WIDTH = 160
# HEIGHT = 120
LR = 1e-3
EPOCHS = 10
MODEL_NAME = 'pygta5-car-fast-{}-{}-{}-epochs-300K-data.model'.format(LR, 'alexnetv2',EPOCHS)

model = alexnet(1, 4, LR)

hm_data = 22
for i in range(EPOCHS):
    for i in range(1,hm_data+1):
        np_load_old = np.load

        # modify the default parameters of np.load
        np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)
        train_data = np.load('training_datav2.npy')
        np.load = np_load_old
        train = train_data[:-100]
        test = train_data[-100:]

        X = ([i[0] for i in train])
        Y = [i[1] for i in train]

        test_x = ([i[0] for i in test])
        test_y = [i[1] for i in test]

        model.fit({'input': X}, {'targets': Y}, n_epoch=1, validation_set=({'input': test_x}, {'targets': test_y}), 
            snapshot_step=500, show_metric=True, run_id=MODEL_NAME)

        model.save(MODEL_NAME)



# tensorboard --logdir=foo:C:/path/to/log





