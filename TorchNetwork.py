import torch
import torchvision
from torchvision import transforms, datasets
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

np_load_old = np.load
np.load = lambda *a, **k: np_load_old(*a, allow_pickle=True, **k)
train_data = np.load('training_datav2.npy')

np.load = np_load_old

training_inputs = []
training_outputs = []

for row in train_data:
    training_inputs.append(row[0])
    training_outputs.append(row[1])

trainX = training_inputs[:len(training_inputs) // 2]
testX = training_inputs[len(training_inputs) // 2:]
trainY = training_outputs[:len(training_outputs) // 2]
testY = training_outputs[len(training_outputs) // 2:]

my_x = np.array(trainX)  # a list of numpy arrays
my_y = np.array(trainY)  # another list of numpy arrays (targets)

tensor_x = torch.Tensor(my_x)  # transform to torch tensor
tensor_y = torch.Tensor(my_y)

trainDataset = TensorDataset(tensor_x, tensor_y)

my_testx = np.array(testX)  # a list of numpy arrays
my_testy = np.array(testY)  # another list of numpy arrays (targets)

tensor_testx = torch.Tensor(my_testx)  # transform to torch tensor
tensor_testy = torch.Tensor(my_testy)

testDataset = TensorDataset(tensor_testx, tensor_testy)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5, 5)
        self.fc2 = nn.Linear(5, 4)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = (self.fc2(x))

        return x


net = Net()
# print(net)

optimizer = optim.Adam(net.parameters(), lr=0.001)
criterion = torch.nn.BCEWithLogitsLoss()
print("QUEUE ROCKEY MUSIC")
EPOCHS = 100

for epoch in range(EPOCHS):

    for data in trainDataset:
        x, y = data

        net.zero_grad()
        out = net(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()

    print(epoch,loss)
correct = 0
total = 0
with torch.no_grad():
    for data in trainDataset:
        x, y = data
        out = net(x)
        #for idx, i in enumerate(out):
        #print(torch.round(torch.sigmoid(out)))
        #print(round(torch.sigmoid(out)))
        #print(y)
        #if torch.eq(torch.round(torch.sigmoid(out)), y):
            #         # print("out:",out)
            #         # print("rounded",torch.round_(out))
            #         # print("X:",x)
            #         # print("yidx",y)
            #         # print("i",i)
            #         # print("torch",torch.argmax(i))
            #correct += 1
        #total += 1

guessright = net(torch.tensor([6, 0, 1, 0, 0.3971354166666663]))
guessleft = net(torch.tensor([6, 0, 1, 0, -0.3971354166666663]))
guessstraight = net(torch.tensor([6, 0, 1, 0, 0.0]))

print("right", (guessright > 0.5).float())
print("left", (guessleft > 0.5).float())
print("right Sigmoid",  torch.round(torch.sigmoid(guessright)))
print("left Sigmoid", torch.round(torch.sigmoid(guessright)))
print("straight Sigmoid", torch.round(torch.sigmoid(guessstraight)))
print("right", (guessright))
print("left", (guessleft))

#print("Accuraccy:", (correct / total))
