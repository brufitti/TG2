# Imports
import csv
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
import wandb
from noise import add_noise, noise_maker
# Parallel files
from model import PositionPredictor
from data import datacaller, Data

wandb.init(project="projectPPv1.1", name= "Treino no lab 120k dados")

def Train(model,train_dataloader, val_dataloader, epoches, learning_rate):
    wandb.config = {
                    "learning_rate": learning_rate,
                    "epoches": epoches,
                    "batch_size": 8000
                    }
    
    _ = torch.rand(20,20) #wake up the gpu
    optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)
    criterion = torch.nn.MSELoss()
    train_dataset = train_dataloader
    val_dataset = val_dataloader
    pred = torch.zeros(8000,2)
    y = torch.zeros(8000,2)
    
    for epoche in range(epoches):
        train_loss = 0
        train_error = 0
        val_loss = 0
        val_error = 0
        # Training
        # ----------------------------------------------
        model.train()
        for data in train_dataset:
            x,y = data
            x = add_noise(x)
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
        train_loss = train_loss/len(train_dataset)
        
        # Validation
        # ----------------------------------------------
        model.eval()
        
        with torch.no_grad():
            for data in val_dataset:
                x,y = data
                x = add_noise(x)
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
                
                if (epoche != 0 and epoche % 100 == 0):
                    
                    print("Epoche: ", epoche)
                    print("Validation Loss: ", val_loss)
        val_loss = val_loss/len(val_dataset)
        wandb.log({
            "Training loss": train_loss,
            "Validation loss": val_loss,
        })
    
    # Saving the last predictions to a file along with the original positions   
    data = open('results10kepoches.csv', 'w', newline='')
    writer = csv.writer(data)
    fill = "|"
    y_list = y.tolist()
    pred_list = pred.tolist()
    for i in range(len(y_list)):
        text =[y_list[i],fill,pred_list[i],fill,np.subtract(y_list[i],pred_list[i])]
        writer.writerow(text)
    data.close
    return val_loss, val_error
        
def filecaller():
    filename = []
    for speedtxt in range(3,6):
        for degrees in range (0,300,60):
            filename.append("data/data-{degree}-0{speeddecimal}mps.csv".format(degree = degrees, speeddecimal = speedtxt))
    return filename
    
    
if __name__ == '__main__':
    filename = filecaller() # vector of paths
    train_files = [name for idx,name in enumerate(filename) if (((idx+1)!=2) and ((idx+1)!= 6 and ((idx+1)!=13)))]
    tx,ty = datacaller(train_files)
    tdata = Data(tx,ty)
    train_dataset = DataLoader(tdata, batch_size=int(tdata.__len__()), shuffle=False)

    val_files = [filename[1], filename[5], filename[12]]
    vx,vy = datacaller(val_files)
    vdata = Data(vx,vy)
    val_dataset = DataLoader(vdata, batch_size=int(vdata.__len__()), shuffle=False)
    
    # parameters for PP class
    input_size = 6
    out_size = 2
    hidden_size = 8
    network = PositionPredictor(input_size, out_size, hidden_size)
    if torch.cuda.is_available():
        network = network.cuda()
    # Parameters for Training
    epoches = 4501 # Previously 10k
    learning_rate = 0.003333333
    a,b = Train(network,train_dataset,val_dataset, epoches, learning_rate)