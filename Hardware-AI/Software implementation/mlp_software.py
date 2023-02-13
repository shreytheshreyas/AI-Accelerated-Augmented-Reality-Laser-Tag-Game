import pandas as pd
import numpy as np

import os
import json

import torch
from torch import nn, Tensor
from torch.utils.data import Dataset

from sklearn.metrics import confusion_matrix, roc_auc_score, balanced_accuracy_score

TRAIN_FILE = "processed_filtered_train_dataset.csv"
TEST_FILE = "processed_filtered_test_dataset.csv"

class FeatureDataset(Dataset):
    def __init__(self, file_name):
        file_out = pd.read_csv(file_name, header=0)
        x = file_out.iloc[:, 1:61].values
        y = file_out.iloc[:, 62].values

        self.X_train = torch.tensor(x, dtype=torch.float32)
        self.Y_train = torch.tensor(y)

    def __len__(self):
        return len(self.Y_train)

    def __getitem__(self, idx):
        return self.X_train[idx], self.Y_train[idx]


class MLP(nn.Module):
    '''
    Multilayer Perceptron.
    '''
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(60, 40),
            nn.Sigmoid(),
            nn.Linear(40, 4),
            nn.Softmax(dim=1)
    )

    def forward(self, x):
        '''Forward pass'''
        return self.layers(x)
  

def save_weights_txt(param):
    f = open("weights_tensor.txt", "w")
    with torch.no_grad():
        param[0] = np.array(param[0])
        for i in range(len(param[0][0])): #iterate through the cols = = 61
            f.write('{')
            for j in range(len(param[0])): #iterate through the rows = 40
                f.write(str(param[0][j][i]))
                if j != len(param[0]) - 1:
                    f.write(',')
            f.write('}, \n')

        f.write('\n end \n')

        param[2] = np.array(param[2])
        for i in range(len(param[2][0])):
            f.write('{')
            for j in range(len(param[2])):
                f.write(str(param[2][j][i]))
                if j != len(param[2]) - 1:
                    f.write(',')
            f.write('}, \n')
        f.close()

def save_biases_txt(param):
    f = open("biases_tensor.txt", "w")
    with torch.no_grad():
        param[1] = np.array(param[1])
        f.write('{')
        for i in range(len(param[1])):
            f.write(str(param[1][i]))
            if i != len(param[1]) - 1:
                f.write(',')
        f.write('} \n')

        f.write('\n end \n')

        param[3] = np.array(param[3])
        f.write('{')
        for i in range(len(param[3])):
            f.write(str(param[3][i]))
            if i != len(param[3]) - 1:
                f.write(',')

        f.write('} \n')
    f.close()

if __name__ == '__main__':
    torch.manual_seed(42)

    test_set = FeatureDataset(TEST_FILE)

    training_set = FeatureDataset(TRAIN_FILE)

    trainloader = torch.utils.data.DataLoader(training_set)
    testloader = torch.utils.data.DataLoader(test_set)

    mlp = MLP()

    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(mlp.parameters(), lr=1e-4)

    for epoch in range(0, 5):
        current_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, targets = data

            optimizer.zero_grad()

            outputs = mlp(inputs)

            loss = loss_function(outputs, targets)

            loss.backward()

            optimizer.step()

    print('Training process has finished.')

    predictions = []
    predictions_raw = []
    actuals = []

    for i, data in enumerate(testloader, 0):
        x_test, y_test = data

        yhat_raw = mlp(x_test)
        yhat_raw = yhat_raw.detach().numpy()
        yhat = np.argmax(yhat_raw)

        actual = y_test.numpy()
        actual = actual.reshape((len(actual), 1))

        predictions.append(yhat)
        predictions_raw.append(yhat_raw)
        actuals.append(actual)

    print(x_test.numpy())
    print(yhat_raw)
    print(actual)
    predictions, actuals = np.vstack(predictions), np.vstack(actuals)

    acc = balanced_accuracy_score(actuals, predictions)
    print('acc: ', acc)

    params = list(mlp.parameters())
    #print('shape: ', len(params), ' layer 1 row: ', len(params[0]), ' layer 2 row: ', len(params[1]), ' layer 3 row: ', len(params[2]), ' layer 4 row: ', len(params[3]))
    #print('shape: ', np.shape(weights))
    #print('layer 1 shape: ', np.shape(params[0]), ' layer 2 shape: ', np.shape(params[1]), ' layer 3 shape: ', np.shape(params[2]), ' layer 4 shape: ', np.shape(params[3]))

    #save_weights_txt(params)
    #save_biases_txt(params)
