# Imports
import csv
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
# Parallel files
from model import PositionPredictor
from data import datacaller, Data


def Train(model,dataloader, epoches, learning_rate):
    _ = torch.rand(20,20) #wake up the gpu
    optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)
    criterion = torch.nn.MSELoss()
    dataset = dataloader
    pred = torch.zeros(8000,2)
    y = torch.zeros(8000,2)
    for epoch in range(epoches):
        train_loss = 0
        train_error = 0
        val_loss = 0
        val_error = 0
        # Training
        # ----------------------------------------------
        model.train()
        for data in dataset:
            x,y = data
            x = x.float()
            y = y.float()
            if torch.cuda.is_available():
                x = x.cuda()
                y = y.cuda()
            
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
            train_loss += loss.item()
            train_error += torch.mean(torch.abs(y-pred))

        
        # Validation
        # ----------------------------------------------
        model.eval()
        
        with torch.no_grad():
            for data in dataset:
                x,y = data
                x = x.float()
                y = y.float()
                if torch.cuda.is_available():
                    x = x.cuda()
                    y = y.cuda()
                
                pred = model(x)
                
                loss = criterion(pred, y)
                
                optimizer.zero_grad()
                
                val_loss += loss.item()
                val_error += torch.mean(torch.abs(y-pred))
                
                if (epoch != 0 and epoch % 100 == 0):
                    
                    print("Epoche: ", epoch)
                    print("Train Loss: ",  train_loss)
                    print("Train Error: ", train_error)
    
    
    data = open('results10kepoches.csv', 'w', newline='')
    writer = csv.writer(data)
    fill = "|"
    for i in range(y.size(0)):
        text =[y[i].tolist(),fill,pred[i].tolist()]
        writer.writerow(text)
    return val_loss, val_error
        
            

    
    
if __name__ == '__main__':
    
    data = Data(datacaller())
    
    dataset = DataLoader(data, batch_size=int(data.__len__()), shuffle=False)

    # parameters for PP class
    input_size = 6
    out_size = 2
    hidden_size = 6
    network = PositionPredictor(input_size, out_size, hidden_size)
    if torch.cuda.is_available():
        network = network.cuda()
    # Parameters for Training
    epoches = 10001
    learning_rate = 0.1
    a,b = Train(network,dataset, epoches, learning_rate)