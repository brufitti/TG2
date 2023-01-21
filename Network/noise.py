import torch 

def noise_maker(data, amp):
    """Makes a random gaussian noise on top of data values given in data tensor.
    
    Args:
        data (1D Tensor): data vector to multiply by the noise
        amp (float): Amplitude of the noise/std of the gaussian curve
    """
    num_points = data.size(0)
    mean = torch.ones(num_points)
    std = torch.ones(num_points)*amp
    x = torch.normal(mean,std)
    return data*x
#needs to make it usable for 2D tensors

def add_noise(x):
    """_Given a tensor with 6 valus, adds noise to the first 5 values and return a
    tensor of same shape.
    Must have noise_maker function

    Args:
        x (2D Tensor): Tensor of tensors to add noise, also known as your data.

    Returns:
        tensor: returns noisy data, notice that the 3rd, 4th and 5th elements are distances derived
        from RSS signals, therefore they are increassed by 5% to simulate loss by ambient impedance
        along with regular noise.
    """
    # order: [float Vel, float Aa, float dist1, float dist2, float dists3,  float dt]
    # Vector num_pointsx6x1->num_vectors 6x1
    new_data_series = torch.empty(0)
    new_values = torch.tensor([0])
    
    for values in x:
        Vel,Aa,d1,d2,d3,dt = values[0].view(1),values[1].view(1),values[2].view(1),values[3].view(1),values[4].view(1),values[5].view(1)
        Vel = noise_maker(Vel, 0.06/3.5)
        Aa = noise_maker(Aa, 0.06/3.5)
        d1 = noise_maker(d1*1.05, 0.03/3.5)
        d2 = noise_maker(d2*1.05, 0.03/3.5)
        d3 = noise_maker(d3*1.05, 0.03/3.5)
        new_values = torch.cat((Vel,Aa,d1,d2,d3,dt),0)
        new_data_series = torch.cat((new_data_series,new_values),0)
    new_x = new_data_series.reshape(-1,6)
    return new_x
            
            
            
#Test
# x = torch.tensor([[11,11,11,11,11,11],[11,11,11,11,11,11],[11,11,11,11,11,11],[11,11,11,11,11,11]])
# y = add_noise(x)
# print(x)
# print(y)
# print(torch.divide((y-x),x))