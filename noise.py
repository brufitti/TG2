import random
import torch 
from time import time


x = torch.normal(1,0.05)
print(x)
print(torch.linalg.det(x))
det = torch.linalg.det(x)

