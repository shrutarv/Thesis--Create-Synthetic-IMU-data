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
import logging
import pandas as pd
#import torchvision.models as model

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
def max_min_values(data, values):
    temp_values = []
    data = data.numpy()
    data = data.reshape(data.shape[0],data.shape[2], data.shape[3])
    
    temp_values = []
    for attr in range(data.shape[2]):
        attribute = []
        temp_max = np.max(data[:,:,attr])
        temp_min = np.min(data[:,:,attr])
        if (values[attr][0] > temp_max):
            attribute.append(values[attr][0])
        else:
            attribute.append(temp_max)
        if(values[attr][1] < temp_min):
            attribute.append(values[attr][1])
        else:
            attribute.append(temp_min)
        temp_values.append(attribute)  
    values = temp_values
    return values
   
'''
Input
data - input matrix to normalize
min_max - list of max and min values for all channels across the entire training and test data

output
returns normalized data between [0,1]

'''
def normalize(data, min_max, string):
    #print(len(min_max), len(min_max[0]))
    data = data.numpy()
    #print(data.shape)
    data = data.reshape(data.shape[0],data.shape[2], data.shape[3])
    for i in range(data.shape[0]):
        for j in range(data.shape[2]):
            data[i,:,j] = (data[i,:,j] - min_max[j][1])/(min_max[j][0] - min_max[j][1])
    test = np.array(data[:,:,:])
    if (string=="train"):
        if(np.max(test)>1.001):
            print("Error",np.max(test))
        if(np.min(test)<-0.001):
            print("Error",np.min(test))
    if (string=="test"):
        test[test > 1] = 1
        test[test < 0] = 0
    data = data.reshape(data.shape[0],1,data.shape[1], data.shape[2])
    data = torch.tensor(data)
    return data

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
    accuracy = 100.*correct.item()/counter
    return accuracy, correct
    
def validation(dataLoader_validation):
    total = 0.0
    correct = 0.0
    trueValue = np.array([], dtype=np.int64)
    prediction = np.array([], dtype=np.int64)
    total_loss = 0.0
    with torch.no_grad():
            
        for b, harwindow_batched in enumerate(dataLoader_validation):
            test_batch_v = harwindow_batched["data"]
            test_batch_l = harwindow_batched["label"][:, 0]
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
            trueValue = np.concatenate((trueValue, test_batch_l.cpu()))
            prediction = np.concatenate((prediction,predicted_classes))
            total += test_batch_l.size(0) 
            test_batch_l = test_batch_l.long()
            predicted_classes = predicted_classes.to(device)
            correct += (predicted_classes == test_batch_l).sum().item()
            total_loss += loss.item()
            #counter = out.view(-1, n_classes).size(0)
        
    print('\nValidation set:  Percent Validation Accuracy: {:.4f}\n'.format(100. * correct / total))
    return (100. * correct / total, total_loss/(b+1))

def set_required_grad(network):
        model_dict = network.state_dict()
        # 1. filter out unnecessary keys
        logging.info('        Network_User:        Setting Required_grad to Weights')

        if config["network"] == 'cnn':
            list_layers = ['conv1_1.weight', 'conv1_1.bias']
        elif config["network"] == 'cnn_imu':
            list_layers = ['conv_LA_1_1.weight', 'conv_LA_1_1.bias', 'conv_LA_1_2.weight', 'conv_LA_1_2.bias',
                           'conv_LA_2_1.weight', 'conv_LA_2_1.bias', 'conv_LA_2_2.weight', 'conv_LA_2_2.bias',
                           'conv_LL_1_1.weight', 'conv_LL_1_1.bias', 'conv_LL_1_2.weight', 'conv_LL_1_2.bias',
                           'conv_LL_2_1.weight', 'conv_LL_2_1.bias', 'conv_LL_2_2.weight', 'conv_LL_2_2.bias',
                           'conv_N_1_1.weight', 'conv_N_1_1.bias', 'conv_N_1_2.weight', 'conv_N_1_2.bias',
                           'conv_N_2_1.weight', 'conv_N_2_1.bias', 'conv_N_2_2.weight', 'conv_N_2_2.bias',
                           'conv_RA_1_1.weight', 'conv_RA_1_1.bias', 'conv_RA_1_2.weight', 'conv_RA_1_2.bias',
                           'conv_RA_2_1.weight', 'conv_RA_2_1.bias', 'conv_RA_2_2.weight', 'conv_RA_2_2.bias',
                           'conv_RL_1_1.weight', 'conv_RL_1_1.bias', 'conv_RL_1_2.weight', 'conv_RL_1_2.bias',
                           'conv_RL_2_1.weight', 'conv_RL_2_1.bias', 'conv_RL_2_2.weight', 'conv_RL_2_2.bias']

        for pn, pv in network.named_parameters():
            if pn in list_layers:
                pv.requires_grad = False

        return network
    
def load_weights(network):
        model_dict = network.state_dict()
        # 1. filter out unnecessary keys
        logging.info('        Network_User:        Loading Weights')

        #print(torch.load(self.config['folder_exp_base_fine_tuning'] + 'network.pt')['state_dict'])
        pretrained_dict = torch.load(config['folder_exp_base_fine_tuning'], map_location='cuda:1').state_dict()
        #pretrained_dict = torch.load(config['folder_exp_base_fine_tuning'])['state_dict']
        logging.info('        Network_User:        Pretrained model loaded')

        #for k, v in pretrained_dict.items():
        #    print(k)

        if config["network"] == 'cnn':
            list_layers = ['conv1_1.weight', 'conv1_1.bias']
        elif config["network"] == 'cnn_imu':
            list_layers = ['conv_LA_1_1.weight', 'conv_LA_1_1.bias', 'conv_LA_1_2.weight', 'conv_LA_1_2.bias',
                           'conv_LA_2_1.weight', 'conv_LA_2_1.bias', 'conv_LA_2_2.weight', 'conv_LA_2_2.bias',
                           'conv_LL_1_1.weight', 'conv_LL_1_1.bias', 'conv_LL_1_2.weight', 'conv_LL_1_2.bias',
                           'conv_LL_2_1.weight', 'conv_LL_2_1.bias', 'conv_LL_2_2.weight', 'conv_LL_2_2.bias',
                           'conv_N_1_1.weight', 'conv_N_1_1.bias', 'conv_N_1_2.weight', 'conv_N_1_2.bias',
                           'conv_N_2_1.weight', 'conv_N_2_1.bias', 'conv_N_2_2.weight', 'conv_N_2_2.bias',
                           'conv_RA_1_1.weight', 'conv_RA_1_1.bias', 'conv_RA_1_2.weight', 'conv_RA_1_2.bias',
                           'conv_RA_2_1.weight', 'conv_RA_2_1.bias', 'conv_RA_2_2.weight', 'conv_RA_2_2.bias',
                           'conv_RL_1_1.weight', 'conv_RL_1_1.bias', 'conv_RL_1_2.weight',  'conv_RL_1_2.bias',
                           'conv_RL_2_1.weight', 'conv_RL_2_1.bias', 'conv_RL_2_2.weight', 'conv_RL_2_2.bias']

        pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in list_layers}
        #print(pretrained_dict)

        logging.info('        Network_User:        Pretrained layers selected')
        # 2. overwrite entries in the existing state dict
        model_dict.update(pretrained_dict)
        logging.info('        Network_User:        Pretrained layers selected')
        # 3. load the new state dict
        network.load_state_dict(model_dict)
        logging.info('        Network_User:        Weights loaded')

        return network
        
        
def training(dataLoader_train, dataLoader_validation, device,flag):
    print('Start Training')
    correct = 0
    total_loss = 0
    total_correct = 0
    best_acc = 0.0
    validation_loss = []
    validation_acc = []
    accuracy = []
    l = []
    for e in range(epochs):
          model.train()
          print("next epoch is",e)
          #loop per batch:
          for b, harwindow_batched in enumerate(dataLoader_train):
             
              train_batch_v = harwindow_batched["data"]
              train_batch_l = harwindow_batched["label"][:, 0]
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
              loss = criterion(out,train_batch_l)/accumulation_steps
              #predicted_classes = torch.argmax(out, dim=1).type(dtype=torch.LongTensor)
              #predicted_classes = predicted_classes.to(device)
              
              #correct += torch.sum(train_batch_l == predicted_classes)
              #counter += out.size(0)
             # a = list(model.parameters())[0].clone() 
              loss.backward()
              
              if (b + 1) % accumulation_steps == 0:   
                optimizer.step()
                # zero the parameter gradients
                optimizer.zero_grad()
              #c = list(model.parameters())[0].clone()
              #print(torch.equal(a.data, c.data))
              acc, correct = metrics(out, train_batch_l)
              #print(' loss: ', loss.item(), 'accuracy in percent',acc)
                      
              #lo, correct = Training(train_batch_v, train_batch_l, noise, model_path, batch_size, tot_loss, accumulation_steps)
              total_loss += loss.item()
              total_correct += correct
          
          model.eval()
          val_acc, val_loss =  validation(dataLoader_validation)
          validation_loss.append(val_loss)
          validation_acc.append(val_acc)
          if (val_acc >= best_acc):
              torch.save(model, model_path_tl)
              print("model saved on epoch", e)
              best_acc = val_acc
          l.append(total_loss/((e+1)*(b + 1)))
          accuracy.append(100*total_correct.item()/((e+1)*(b + 1)*batch_size))
          #torch.save(model, model_path)
    if(flag):
            
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
        plt.savefig('/data/sawasthi/JHMDB/results/result_tl_50.png') 
        #plt.savefig('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/result.png') 
        #plt.savefig('S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/result.png')
        
        
def testing(config):
    print('Start Testing')
    test_acc = 0
    total = 0.0
    correct = 0.0
    trueValue = np.array([], dtype=np.int64)
    prediction = np.array([], dtype=np.int64)
    model = torch.load(model_path_tl)
    model.eval()
    with torch.no_grad():
            
        for b, harwindow_batched in enumerate(dataLoader_test):
            test_batch_v = harwindow_batched["data"]
            test_batch_l = harwindow_batched["label"][:, 0]
           # test_batch_v = normalize(test_batch_v, value,"test")
            test_batch_v = test_batch_v.float()
            test_batch_v = test_batch_v.to(device)
            test_batch_l = test_batch_l.to(device)
            
            out = model(test_batch_v)
            #print("Next Batch result")
            predicted_classes = torch.argmax(out, dim=1).type(dtype=torch.LongTensor)
            #predicted = Testing(test_batch_v, test_batch_l)
            trueValue = np.concatenate((trueValue, test_batch_l.cpu()))
            prediction = np.concatenate((prediction,predicted_classes))
            total += test_batch_l.size(0) 
            test_batch_l = test_batch_l.long()
            predicted_classes = predicted_classes.to(device)
            correct += (predicted_classes == test_batch_l).sum().item()
            #counter = out.view(-1, n_classes).size(0)
        
    print('\nTest set:  Percent Accuracy: {:.4f}\n'.format(100. * correct / total))
    test_acc = 100. * correct / total        
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
    return F1_weighted, test_acc
   
    
if __name__ == '__main__':
    
    if torch.cuda.is_available():  
          dev = "cuda:1" 
    else:  
          dev = "cpu"  
          
    device = torch.device(dev)
    config = {
        "NB_sensor_channels":40,
        "sliding_window_length":100,
        "filter_size":5,
        "num_filters":64,
        "network":"cnn",
        "output":"softmax",
        "num_classes":16,
        "reshape_input":False,
        "folder_exp_base_fine_tuning": '/data/sawasthi/JHMDB/model/model_pose.pth'
        #"folder_exp_base_fine_tuning": 'S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/model_full.pth'
        }
    
    iterations = 3
    weighted_F1_array = []
    test_acc_array = []
    flag = True
    for iter in range(iterations):


        ws=100
        accumulation_steps = 10
        epochs = 100
        batch_size = 200
        learning_rate = 0.00001
        print("epoch: ",epochs,"batch_size: ",batch_size,"accumulation steps: ",accumulation_steps,"ws: ",ws, "learning_rate: ",learning_rate)
            
        #df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/MoCAP/norm_values.csv')
        #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/Github/Thesis- Create Synthetic IMU data/MoCAP/norm_values.csv')
        #value = df.values.tolist()
        #print(len(df),len(value), len(value[0]))
         
        PAMAP_net = Network(config)
        PAMAP_net.init_weights()
        normal = torch.distributions.Normal(torch.tensor([0.0]),torch.tensor([0.001]))
        #noise = noise.float()
        
        criterion = nn.CrossEntropyLoss()
        #model_path = '/data/sawasthi/data/JHMDB/model/model_tl.pth'
        #model_path = 'S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/model.pth'
        #model_path = 'S:/MS A&R/4th Sem/Thesis/PAMAP2_Dataset/'
        #model = torch.load(model_path)
        # transformed_net 
        model = load_weights(PAMAP_net)
        model = model.to(device)
        print("model loaded for iteration",iterations)  
        '''
        PAMAP_net.conv1_1.weight = model.conv1_1.weight
        PAMAP_net.conv1_2.weight = model.conv1_2.weight
        PAMAP_net.conv1_1.bias = model.conv1_1.bias
        PAMAP_net.conv1_2.bias = model.conv1_2.bias
        
        PAMAP_net.conv2_1.weight = model.conv2_1.weight
        PAMAP_net.conv2_2.weight = model.conv2_2.weight
        PAMAP_net.conv2_1.bias = model.conv2_1.bias
        PAMAP_net.conv2_2.bias = model.conv2_2.bias
        
        model = set_required_grad(model)
        model.fc4 = PAMAP_net.fc3
        model.fc4 = PAMAP_net.fc4
        model.fc5 = PAMAP_net.fc5
        model.softmax = PAMAP_net.softmax
        '''
        #optimizer = optim.Adam(model.parameters(), lr=0.001)
        optimizer = optim.RMSprop(model.parameters(), lr=learning_rate, alpha=0.9,weight_decay=0.0005, momentum=0.9)
        #optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)
        path = '/data/sawasthi/PAMAP2/trainData_new/'
        #path = 'S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/pkl/'
        #path = 'S:/MS A&R/4th Sem/Thesis/PAMAP2_Dataset/pkl files'
        #path = "S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/Train_data/"
        train_dataset = CustomDataSet(path)
        dataLoader_train = DataLoader(train_dataset, shuffle=True,
                                      batch_size=batch_size,
                                       num_workers=0,
                                       pin_memory=True,
                                       drop_last=True)
      
       
        # Validation data    
        path = '/data/sawasthi/PAMAP2/validationData_new/'
        #path = 'S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/pkl/'
        #path = 'S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows/'
        #path = "S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/Test_data/"
        validation_dataset = CustomDataSet(path)
        dataLoader_validation = DataLoader(validation_dataset, shuffle=False,
                                      batch_size=batch_size,
                                       num_workers=0,
                                       pin_memory=True,
                                       drop_last=True)
        
        # Test data    
        path = '/data/sawasthi/PAMAP2/testData_new/'
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
        model_path_tl = '/data/sawasthi/Penn/model/model_tl_J_PAMAP_new_pose.pth'
        training(dataLoader_train, dataLoader_validation,device,flag)
        flag = False
        WF, TA = testing(config)
        #with open('S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/result.csv', 'w', newline='') as myfile:
        #with open('S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/result.csv', 'w', newline='') as myfile:
        weighted_F1_array.append(WF)
        test_acc_array.append(TA)
        
    print("Mean Weighted F1 score after 5 runs is",np.mean(weighted_F1_array))
    print("Standard deviation of Weighted F1 score after 5 runs is",np.std(weighted_F1_array))
    
    print("Mean Test accuracy score after 5 runs is",np.mean(test_acc_array))
    print("Standard deviation of Test accuracy score after 5 runs is",np.std(test_acc_array))
    