#%%
import torch; torch.manual_seed(0)
import torch.nn as nn
import torch.nn.functional as F
import torch.utils
import torch.distributions
import torchvision
import numpy as np
import matplotlib.pyplot as plt
from fuzzy_layer import FuzzyLayer

device = 'cuda' if torch.cuda.is_available() else 'cpu'
#%%
def plot_clusters(z, labels):
    plt.scatter(z[:, 0], z[:, 1], c=labels, s=3)
    plt.colorbar()
#%%
class SimpleClustering(nn.Module):
    def __init__(self):
        super(SimpleClustering, self).__init__()
        self.fuzzy = FuzzyLayer.fromcenters(initial_centers=[
            [ -1.,  1], 
            [  1., -1]], trainable=True)

    def forward(self, x):
        return self.fuzzy(x)
#%%
sample_size = 300
dataset = 1 * np.random.randn(sample_size,2) + 1
labels  = np.repeat([1,0],sample_size) 

dataset = np.append(dataset, 0.1 * np.random.randn(sample_size,2) - 1, axis=0)
labels = np.append(labels, np.repeat([0,1],sample_size) , axis=0)

dataset = torch.FloatTensor(dataset)
labels = torch.FloatTensor(labels).to(device)
#%%
model = SimpleClustering()
processed_dataset = model(dataset).detach().numpy()
assigned_classes =[np.argmax(a) for a in model(dataset).detach().numpy()]
plot_clusters(dataset,assigned_classes)
#%%
def train(model, data, labels, epochs=20):
    opt = torch.optim.Adadelta(model.parameters())
    ploss = nn.CrossEntropyLoss(reduction="sum")

    for epoch in range(epochs):
        sum_ploss = 0
        count= 0
        for x, y in zip(data, labels):
            x = x.to(device) 
            opt.zero_grad()
            f_c = model(dataset).to(device)
            poison_loss_value = ploss(f_c, y)
            poison_loss_value.backward()
            opt.step()
            count+=1
            sum_ploss += poison_loss_value
                    
        print(f"Epoch {epoch}: ploss {sum_ploss/count}")
        count = 0
        sum_ploss = 0

    return model
#%%
train(model, dataset, labels, 20)
#%%
processed_dataset = model(dataset).detach().numpy()
assigned_classes =[np.argmax(a) for a in model(dataset).detach().numpy()]
plot_clusters(dataset,assigned_classes)
# %%
