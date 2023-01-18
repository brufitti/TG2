# Imports
import csv
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader

# Parallel files

# Loading the data
# order: [float V, float Aa, list(float) Pos,  float dt, list(float) Real Position]
def datacaller():
    x = []
    y = []
    data = open('data.csv',newline='')
    reader = csv.reader(data, delimiter = ",")
    dataset = []
    for row in reader:
        dataset.append(row)
    for values in dataset:
        _temp2 = values[2].strip('][').split(',')
        _temp2[0] = float(_temp2[0])
        _temp2[1] = float(_temp2[1])
        _temp2[2] = float(_temp2[2])
        _temp4 = values[4].strip('][').split(',')
        _temp4[0] = float(_temp4[0])
        _temp4[1] = float(_temp4[1])
        
        _x= [float(values[0]), float(values[1]), float(_temp2[0]), float(_temp2[1]), float(_temp2[2]), float(values[3])]
        _y= [_temp4[0], _temp4[1]]
        
        x.append(_x)
        y.append(_y)
    data.close()
    
    return np.array(x),np.array(y)

class Data(Dataset):
    def __init__(self,x,y):
        self.x, self.y = x,y
        
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        x = self.x[idx]
        y = self.y[idx]
        return x,y

class PositionPredictor(nn.Module):
    # aka PP
    def __init__(self, input_size, out_size, hidden_size):
        super(PositionPredictor, self).__init__()
        
        self.out_size = out_size
        self.input_size = input_size
        self.hidden_size = hidden_size  # might change to hidden features
        
        self.lstm1 = nn.LSTMCell(input_size=self.input_size, hidden_size=self.hidden_size)
        self.lstm2 = nn.LSTMCell(input_size=self.hidden_size, hidden_size=self.hidden_size)
        self.linear = nn.Linear(in_features=hidden_size, out_features=out_size)
        
    def forward(self, x):
        outputs = []
        data_size = len(x)
        #set the parameters for LSTM
        h_t = torch.zeros(data_size, self.hidden_size)
        c_t = torch.zeros(data_size, self.hidden_size)
        h_t2 = torch.zeros(data_size, self.hidden_size)
        c_t2 = torch.zeros(data_size, self.hidden_size)
        if torch.cuda.is_available():
            h_t = h_t.cuda()
            c_t = c_t.cuda()
            h_t2 = h_t2.cuda()
            c_t2 = c_t2.cuda()

        h_t, c_t = self.lstm1(x, (h_t, c_t))
        h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2)) # new hidden and cell states
        output = self.linear(h_t2) # output from the last FC layer
        #maybe add another RNN classic
        outputs.append(output)
        
        outputs = torch.cat(outputs, dim=0).view(-1,2)
        
        return outputs

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
    x,y = datacaller()
    data = Data(x,y)
    
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