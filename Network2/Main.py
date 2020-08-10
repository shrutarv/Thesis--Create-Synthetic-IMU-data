import matplotlib
matplotlib.use('Agg')
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import numpy as np
import sys
import time
import torch.optim as optim
import pickle
from DataLoader import CustomDataSet, CustomDataSetTest
from torch.utils.data import DataLoader
from Network import Network
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import csv
import pickle


cuda = "True"
torch.manual_seed(1111)
if torch.cuda.is_available():
    if not cuda:
        print("WARNING: You have a CUDA device, so you should probably run with --cuda")
        
def getTrainData(path,batch_size):
        
    all_datasets = []
    train_data = []
    #path = '/data/sawasthi/data/trainData/'
    #path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/'
    #while folder_counter < 10:
        #some code to get path_to_imgs which is the location of the image folder
    train_dataset = CustomDataSet(path)
    all_datasets.append(train_dataset)
    
        
    final_dataset = torch.utils.data.ConcatDataset(all_datasets)
    train_loader = DataLoader(final_dataset, shuffle=False,
                                      batch_size=batch_size,
                                       num_workers=0,
                                       pin_memory=True,
                                       drop_last=True)
    for idx, input_seq  in enumerate(train_loader):
        train_data.append(input_seq)
        
    return train_data

def getTrainDataLabels(path,batch_size):
        
    all_datasets = []
    train_data = []
    #path = '/data/sawasthi/data/testData/'
    #path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/'
    #while folder_counter < 10:
        #some code to get path_to_imgs which is the location of the image folder
    train_dataset = CustomDataSetTest(path)
    all_datasets.append(train_dataset)
    
        
    final_dataset = torch.utils.data.ConcatDataset(all_datasets)
    train_loader = DataLoader(final_dataset, shuffle=False,
                                      batch_size=batch_size,
                                       num_workers=0,
                                       pin_memory=True,
                                       drop_last=True)
    for idx, input_seq  in enumerate(train_loader):
        train_data.append(input_seq)
        
    return train_data

# not called anymore. This method normalizes each attribute of a 2D matrix separately
def normalize(data,ws):
    for k in range(len(data)):
        list1 = []
        temp = torch.tensor(list1)
        data_new = data[k]    
        data_new = torch.reshape(data_new,(200,30))
        data_new = data_new.cpu().detach().numpy()
        for i in range(data_new.shape[1]):
            max = np.max(data_new[:,i])
            min = np.min(data_new[:,i])
            for j in range(ws-1):
                data_new[j,i] = (data_new[j,i] - min)/(max - min)
        data_new = np.reshape(data_new,(1,200,30))
        data_new = torch.tensor(data_new).float()
        temp = torch.cat((temp, data_new), 0)
        #data_new = torch.tensor(data_new)        
        return data_new

def Testing(test_x, test_y, batch_size):
    index = 0
    model.eval()
    # n_classes = 8
    loss = 0
    loss = torch.tensor(loss)
    trueValue = []
    prediction = []
    total = 0
    correct = 0
    with torch.no_grad():
        for batch in range(0,len(test_x),batch_size):
            
            x = test_x[index]
            y = test_y[index]
            x = torch.tensor(x)
            x = np.reshape(x,(batch_size,ws,features))
            x = x.float()
            out = model(x.unsqueeze(1).contiguous())
            print("Next Batch result",out)
            _,predicted = torch.max(out, 1)
            #loss = criterion(out.view(-1, n_classes), y.view(-1))
            #pred = out.view(-1, n_classes).data.max(1, keepdim=True)[1]
            #print(pred)
            for m in range(len(y)):
                
                trueValue.append(y.tolist()[m])
                prediction.append(predicted.tolist()[m])
            #flat_list_pred = [item for sublist in prediction for item in sublist]
            #flat_list_true = [item for sublist in trueValue for item in sublist]
            #print("predicted list")
            #unique(flat_list_pred)
           # print("true list")
            #unique(flat_list_true)
            #correct = pred.eq(y.data.view_as(pred)).cpu().sum()
            total += y.size(0)
            correct += (predicted == y).sum().item()
            #counter = out.view(-1, n_classes).size(0)
            index += 1
        print('\nTest set:  Accuracy: {:.4f}\n'.format(100. * correct / total))
            
        cm = confusion_matrix(trueValue, prediction)
        print(cm)
        #precision, recall = performance_metrics(cm)
        precision, recall = get_precision_recall(trueValue, prediction)
        print(precision)
        print(recall)
        return loss.item()
    
def unique(list1): 
      
    # insert the list to the set 
    list_set = set(list1) 
    # convert the set to the list 
    unique_list = (list(list_set)) 
    for x in unique_list: 
        print(x)
 
def get_precision_recall(targets, predictions):
        precision = torch.zeros((8))
        recall = torch.zeros((8))
        predictions = torch.tensor(predictions)
        targets = torch.tensor(targets)
        x = torch.ones(predictions.size())
        y = torch.zeros(predictions.size())

        #x = x.to('cuda', dtype=torch.long)
        #y = y.to('cuda', dtype=torch.long)

        for c in range(8):
            selected_elements = torch.where(predictions == c, x, y)
            non_selected_elements = torch.where(predictions == c, y, x)

            target_elements = torch.where(targets == c, x, y)
            non_target_elements = torch.where(targets == c, y, x)

            true_positives = torch.sum(target_elements * selected_elements)
            false_positives = torch.sum(non_target_elements * selected_elements)

            false_negatives = torch.sum(target_elements * non_selected_elements)

            try:
                precision[c] = true_positives.item() / float((true_positives + false_positives).item())
                recall[c] = true_positives.item() / float((true_positives + false_negatives).item())

            except:
                # logging.error('        Network_User:    Train:    In Class {} true_positives {} false_positives {} false_negatives {}'.format(c, true_positives.item(),
                #                                                                                                                              false_positives.item(),
                #                                                                                                                              false_negatives.item()))
                continue

        return precision, recall
        
def performance_metrics(cm):
    precision = []
    recall = []
    for i in range(len(cm)):
        tp = cm[i,i]
        fp = cm.sum(axis=0)[i] - cm[i,i]
        fn = cm.sum(axis=1)[i] - cm[i,i]
        precision.append(tp/(tp + fp))
        recall.append(tp/(tp+fn))
        print("Class",i," - precision", precision[i], "Recall",recall[i] )
    
    prec_avg = sum(precision)/len(precision)
    rec_avg = sum(recall)/len(recall)
    return precision, recall

def Training(train_x, train_y, noise, model_path,batch_size, total_loss):
          
    #global i, total_loss, counter
    index = 0
    correct = 0
    counter = 0 
    model.train()
    total_loss = 0
    n_classes = 8
    for j in range(0,int(len(train_x)/batch_size)):
        #start_ind = batch
        #end_ind = start_ind + batch_size
        
        x = train_x[index]
        y = train_y[index]
        
        optimizer.zero_grad()
        x = x.float()
        x = x + noise
        x = np.reshape(x,(batch_size,ws,features))
        #x = np.reshape(x,(batch_size,features,ws))
        out = model(x.unsqueeze(1).contiguous())
        #out = model(x)
        loss = criterion(out.view(-1, n_classes), y.view(-1))
        pred = out.view(-1, n_classes).data.max(1, keepdim=True)[1]
        correct += pred.eq(y.data.view_as(pred)).cpu().sum().item()
        counter += out.view(-1, n_classes).size(0)
        
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        #if index % 50 == 49:    # print every 2000 mini-batches
        print(' loss: ', (total_loss / (index + 1)))
       
        index +=1
        print(index)
    #torch.save(model.state_dict(), model_path)
    print(index)
    index +=1
    counter+=1
    return total_loss/index, 100.*correct/counter

config = {
    "NB_sensor_channels":30,
    "sliding_window_length":100,
    "filter_size":5,
    "num_filters":64,
    "network":"cnn",
    "output":"softmax",
    "num_classes":8,
    "reshape_input":False
    }
ws=100
features = 30
model = Network(config)
model = model.float()
#model.load_state_dict(torch.load())
#print("model loaded")
#model.cuda()
#train_x = train_x.cuda()
#train_y = train_y.cuda()
#test_x = test_x.cuda()
#test_y = test_y.cuda()
#data=[]
#file = open('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/seq_S07_1_0.pkl', 'rb')
#data = pickle.load(file)
# close the file
#file.close()
#criterion = nn.CrossEntropyLoss()
#lr = args.lr
#optimizer = getattr(optim, args.optim)(model.parameters(), lr=lr)
epochs = 30
batch_size = 64
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)
print('getting train and test data')
model_path = '/data/sawasthi/data/model/model.pth'
#model_path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/'
path = '/data/sawasthi/data/trainData/'
#path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/'
train_x = getTrainData(path, batch_size)
train_y = getTrainDataLabels(path, batch_size)
path = '/data/sawasthi/data/testData/'
#path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows/'

test_x = getTrainData(path, batch_size)
test_y = getTrainDataLabels(path, batch_size)
#train_y = torch.tensor(train_y)
noise = np.random.normal(0,1,(batch_size,ws,features))
#noise = np.random.normal(0,1,(batch_size,features,ws))
noise = torch.tensor(noise)
noise = noise.float()
l = []
tot_loss = 0
temp = []
accuracy = []
print('Start Training')
for i in range(epochs):
    lo, acc = Training(train_x, train_y, noise, model_path, batch_size, tot_loss)
    l.append(lo)
    accuracy.append(acc)
print('Finished Training')
ep = list(range(1,epochs+1))   
plt.subplot(1,2,1)
plt.title('epoch vs loss')
plt.plot(ep,l)
plt.subplot(1,2,2)
plt.title('epoch vs accuracy')
plt.plot(ep,accuracy)
plt.savefig('/data/sawasthi/data/result.png') 
#plt.savefig('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/result.png') 

print('Start Testing')
Testing(test_x, test_y, batch_size)
print('Finished Testing')
#with open('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/result.csv', 'w', newline='') as myfile:
with open('/data/sawasthi/data/result.csv', 'w') as myfile:
     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
     wr.writerow(accuracy)
     wr.writerow(l)
         
