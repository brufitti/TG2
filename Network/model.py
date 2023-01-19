import torch
import torch.nn as nn

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