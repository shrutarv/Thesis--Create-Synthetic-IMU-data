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
from DataLoader import CustomDataSet
from torch.utils.data import DataLoader
from Network import Network
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import csv
import os
import random
import platform

import pandas as pd


# not called anymore. This method normalizes each attribute of a 2D matrix separately
'''
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
'''

'''
Calculates precision and recall for all class using confusion matrix (cm)
returns list of precision and recall values
'''  
def get_precision_recall(targets, predictions):
        precision = torch.zeros((config['num_classes']))
        recall = torch.zeros((config['num_classes']))
        predictions = torch.tensor(predictions)
        targets = torch.tensor(targets)
        x = torch.ones(predictions.size())
        y = torch.zeros(predictions.size())

        #x = x.to('cuda', dtype=torch.long)
        #y = y.to('cuda', dtype=torch.long)

        for c in range(len(precision)):
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

'''
Create a list with max and min values for each channel for the input data
data - input in form [batch size, 1, window size, channels]
values - input argument having the max and min values of all channels from the previous iteration.
         Compares these previous values to current min and max values and updates
output - returns a list with max and min values for all channels

'''  # Calculate max min and save it to save time.


'''
returns a list of F1 score for all classes
'''
def F1_score(targets, preds, precision, recall):
        # Accuracy
        targets = torch.tensor(targets)
        #predictions = torch.argmax(preds, dim=1)
        #precision, recall = get_precision_recall(targets, preds)
        proportions = torch.zeros(config['num_classes'])

        for c in range(config['num_classes']):
            proportions[c] = torch.sum(targets == c).item() / float(targets.size()[0])
        
        multi_pre_rec = precision * recall
        sum_pre_rec = precision + recall
        multi_pre_rec[torch.isnan(multi_pre_rec)] = 0
        sum_pre_rec[torch.isnan(sum_pre_rec)] = 0

        # F1 weighted
        weighted_f1 = proportions * (multi_pre_rec / sum_pre_rec)
        weighted_f1[torch.isnan(weighted_f1)] = 0
        F1_weighted = torch.sum(weighted_f1) * 2

        # F1 mean
        f1 = multi_pre_rec / sum_pre_rec
        f1[torch.isnan(f1)] = 0
        F1_mean = torch.sum(f1) * 2 / config['num_classes']

        return F1_weighted, F1_mean
    
def metrics(predictions, true):
    counter = 0.0
    correct = 0.0
    predicted_classes = torch.argmax(predictions, dim=1).type(dtype=torch.LongTensor)
    predicted_classes = predicted_classes.to(device)
    
    correct = torch.sum(true == predicted_classes)
    counter = true.size(0)
    accuracy = 100.*correct.item()/float(counter)
    return accuracy, correct
    
def validation(dataLoader_validation, model):
    model.eval()
    total = 0.0
    correct = 0.0
    #trueValue = torch.array([], dtype=np.int64)
    #prediction = torch.array([], dtype=np.int64)
    total_loss = 0.0
    with torch.no_grad():
            
        for b, harwindow_batched in enumerate(dataLoader_validation):
            test_batch_v = harwindow_batched["data"]
            test_batch_l = harwindow_batched["label"]
            #test_batch_v = normalize(test_batch_v, value,"test")
            test_batch_v = test_batch_v.float()
            test_batch_v = test_batch_v.to(device)
            test_batch_l = test_batch_l.to(device)
            test_batch_l = test_batch_l.long()
            out = model(test_batch_v)
            loss = criterion(out,test_batch_l)
            #print("Next Batch result")
            predicted_classes = torch.argmax(out, dim=1).type(dtype=torch.LongTensor)
            #predicted = Testing(test_batch_v, test_batch_l)
            if(b==0):
                trueValue = harwindow_batched["label"]
                prediction = predicted_classes
            else:
                trueValue = torch.cat((trueValue,harwindow_batched["label"]),dim = 0)
                prediction = torch.cat((prediction,predicted_classes),dim = 0)
                
            #trueValue = torch.tenate((trueValue, test_batch_l.cpu()))
            #prediction = torch.concatenate((prediction,predicted_classes))
            total_loss += loss.item()
        #total += test_batch_l.size(0) 
        total = trueValue.size()[0]
       
        #test_batch_l = test_batch_l.long()
        #predicted_classes = predicted_classes.to(device)
        #correct += (predicted_classes == test_batch_l).sum().item()
        correct = (trueValue == prediction).sum().item()
        
        #counter = out.view(-1, n_classes).size(0)
    print('validation set: test batch {}'.format(test_batch_l[0]))  
    print('validation set: label {}'.format(harwindow_batched["label"][0]))  
    print('output out: {}'.format(out[0]))
    print('output predicted classes: {}'.format(predicted_classes[0]))
    
    print('\nValidation set:  Percent Validation Accuracy: {:.4f}\n'.format(100. * correct / float(total)))
    return (100. * correct / float(total), total_loss/float((b+1)))

def train(model):
    print('Start Training')
    correct = 0
    total_loss = 0
    
    best_acc = 0.0
    validation_loss = []
    validation_acc = []
    optimizer.zero_grad()
    for e in range(epochs):
          model.train()
          print("next epoch",e)
          #loop per batch:
          
          for b, harwindow_batched in enumerate(dataLoader_train):
              model.train()
              train_batch_v = harwindow_batched["data"]
              train_batch_l = harwindow_batched["label"]
              #print(train_batch_l.shape)
              #train_batch_v.to(device)
              train_batch_l = train_batch_l.to(device)
              
              train_batch_v = train_batch_v.float()
              train_batch_v = train_batch_v.to(device)
              noise = normal.sample((train_batch_v.size()))
              noise = noise.reshape(train_batch_v.size())
              noise = noise.to(device, dtype=torch.float)

              train_batch_v = train_batch_v + noise
              
              #print(train_batch_v.device)
              out = model(train_batch_v)
              train_batch_l = train_batch_l.long()
              #loss = criterion(out.view(-1, n_classes), train_y.view(-1))
              loss = criterion(out,train_batch_l)
              #loss = criterion(out,train_batch_l)*float((1/accumulation_steps))
              #predicted_classes = torch.argmax(out, dim=1).type(dtype=torch.LongTensor)
              #predicted_classes = predicted_classes.to(device)
              
              #correct += torch.sum(train_batch_l == predicted_classes)
              #counter += out.size(0)
              # a = list(model.parameters())[0].clone() 
              loss.backward()
              
              #if (b + 1) % accumulation_steps == 0:   
              optimizer.step()
              # zero the parameter gradients
              optimizer.zero_grad()
              #c = list(model.parameters())[0].clone()
              #print(torch.equal(a.data, c.data))
              acc, correct = metrics(out, train_batch_l)
              print(' loss: ', loss.item(), 'accuracy in percent',acc)
                      
              #lo, correct = Training(train_batch_v, train_batch_l, noise, model_path, batch_size, tot_loss, accumulation_steps)
              total_loss = loss.item()
              total_correct = correct
          
              if(b%50)==0:
                  
                  val_acc, val_loss =  validation(dataLoader_validation, model)
                  validation_loss.append(val_loss)
                  validation_acc.append(val_acc)
                  if (val_acc >= best_acc):
                      torch.save(model, model_path)
                      print("model saved on epoch", e)
                      best_acc = val_acc
                  l.append(total_loss/float(batch_size))
                  accuracy.append(100*total_correct.item()/float(batch_size))
                  #torch.save(model, model_path)
    print('Finished Training')
    ep = list(range(1,e+2))   
    plt.subplot(1,2,1)
    plt.title('epoch vs loss')
    plt.plot(ep,l, 'r', label='training loss')
    plt.plot(ep,validation_loss, 'g',label='validation loss')
    plt.legend()
    plt.subplot(1,2,2)
    plt.title('epoch vs accuracy')
    plt.plot(ep,accuracy,label='training accuracy')
    plt.plot(ep,validation_acc, label='validation accuracy')
    plt.legend()
    plt.savefig('/data/sawasthi/data/opportunity/results/result.png') 
    #plt.savefig('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/result.png') 
    #plt.savefig('S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/result.png')
    
def test():
    print('Start Testing')
    
    total = 0.0
    correct = 0.0
    total_loss = 0.0
    model = torch.load(model_path)
    model.eval()
    with torch.no_grad():
            
        for b, harwindow_batched in enumerate(dataLoader_test):
            test_batch_v = harwindow_batched["data"]
            test_batch_l = harwindow_batched["label"]
           # test_batch_v = normalize(test_batch_v, value,"test")
            test_batch_v = test_batch_v.float()
            test_batch_v = test_batch_v.to(device)
            test_batch_l = test_batch_l.to(device)
            
            out = model(test_batch_v)
            #print("Next Batch result")
            predicted_classes = torch.argmax(out, dim=1).type(dtype=torch.LongTensor)
            #predicted = Testing(test_batch_v, test_batch_l)
            if(b==0):
                trueValue = harwindow_batched["label"]
                prediction = predicted_classes
            else:
                trueValue = torch.cat((trueValue,harwindow_batched["label"]),dim = 0)
                prediction = torch.cat((prediction,predicted_classes),dim = 0)
            
            #trueValue = np.concatenate((trueValue, test_batch_l.cpu()))
            #prediction = np.concatenate((prediction,predicted_classes))
        total = trueValue.size()[0]
        print(trueValue.size())
        print(prediction.size())
        #test_batch_l = test_batch_l.long()
        #predicted_classes = predicted_classes.to(device)
        #correct += (predicted_classes == test_batch_l).sum().item()
        correct = (trueValue == prediction).sum().item()
    
    print('\nTest set:  Percent Accuracy: {:.4f}\n'.format(100. * correct / float(total)))
        
    cm = confusion_matrix(trueValue, prediction)
    print(cm)
    #precision, recall = performance_metrics(cm)
    precision, recall = get_precision_recall(trueValue, prediction)
    F1_weighted, F1_mean = F1_score(trueValue, prediction, precision, recall)
    print("precision", precision)
    print("recall", recall)
    print("F1 weighted", F1_weighted)
    print("F1 mean",F1_mean)
    
    print('Finished Validation')
    #with open('S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/result.csv', 'w', newline='') as myfile:
    #with open('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/result.csv', 'w', newline='') as myfile:
    with open('/data/sawasthi/data/opportunity/results/result.csv', 'w') as myfile:
         wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
         wr.writerow(accuracy)
         wr.writerow(l)
                 
    
if __name__ == '__main__':
    seed = 42
    os.environ['PYTHONHASHSEED'] = str(seed)
    # Torch RNG
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # Python RNG
    np.random.seed(seed)
    random.seed(seed)

    if torch.cuda.is_available():  
          dev = "cuda:1" 
    else:  
          dev = "cpu"  
          
    device = torch.device(dev)
    config = {
        "NB_sensor_channels":113,
        "sliding_window_length":24,
        "filter_size":5,
        "num_filters":64,
        "network":"cnn",
        "output":"softmax",
        "num_classes":18,
        "reshape_input":False
        }


   
    accumulation_steps = 5
    correct = 0
    total_loss = 0.0
    total_correct = 0
    epochs = 10
    batch_size = 200
    l = []
    tot_loss = 0
    accuracy = []
        
    #df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/MoCAP/norm_values.csv')
    #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/Github/Thesis- Create Synthetic IMU data/MoCAP/norm_values.csv')
    #value = df.values.tolist()
    #print(len(df),len(value), len(value[0]))
    model = Network(config)
    model = model.float()
    model = model.to(device)
    #model.load_state_dict(torch.load())
    #print("model loaded")   # 
    normal = torch.distributions.Normal(torch.tensor([0.0]),torch.tensor([0.001]))
    #noise = noise.float()
    
    criterion = nn.CrossEntropyLoss()
    #optimizer = optim.Adam(model.parameters(), lr=0.001)
    optimizer = optim.RMSprop(model.parameters(), lr=0.00001, alpha=0.9,weight_decay=0.0005, momentum=0.9)
    #optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)
    model_path = '/data/sawasthi/data/opportunity/model/model_ges.pth'
    #model_path = 'S:/MS A&R/4th Sem/Thesis/OpportunityUCIDataset/OpportunityUCIDataset/dataset/'
    path = '/data/sawasthi/data/opportunity/trainData/'
    #path = 'S:/MS A&R/4th Sem/Thesis/OpportunityUCIDataset/OpportunityUCIDataset/pklfile/train'
    #path = "S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/Train_data/"
    train_dataset = CustomDataSet(path)
    dataLoader_train = DataLoader(train_dataset, shuffle=True,
                                  batch_size=batch_size,
                                   num_workers=0,
                                   pin_memory=True,
                                   drop_last=True)
  
   
    # Validation data    
    path = '/data/sawasthi/data/opportunity/validationData/'
    #path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows/'
    #path = "S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/Test_data/"
    validation_dataset = CustomDataSet(path)
    dataLoader_validation = DataLoader(validation_dataset, shuffle=False,
                                  batch_size=batch_size,
                                   num_workers=0,
                                   pin_memory=True,
                                   drop_last=True)
    
    # Test data    
    path = '/data/sawasthi/data/opportunity/testData/'
    #path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows/'
    #path = "S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/Test_data/"
    test_dataset = CustomDataSet(path)
    dataLoader_test = DataLoader(test_dataset, shuffle=False,
                                  batch_size=batch_size,
                                   num_workers=0,
                                   pin_memory=True,
                                   drop_last=True)
    '''
    for b, harwindow_batched in enumerate(dataLoader_test):
        data_x = harwindow_batched["data"]
        data_x.to(device)
        value = max_min_values(data_x,value)
    '''
    #train(model)
    test()
    
    
   
