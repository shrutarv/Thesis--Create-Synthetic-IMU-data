import pandas as pd
import sys
import numpy as np
import os
import pickle
from sliding_window import sliding_window
from pre_processing import *
import glob
import csv
import scipy.interpolate as sp
import matplotlib.pyplot as plt

NUM_CLASSES = 8
def opp_sliding_window(data_x, data_y, ws, ss, label_pos_end = True):
    '''
    Performs the sliding window approach on the data and the labels
    
    return three arrays.
    - data, an array where first dim is the windows
    - labels per window according to end, middle or mode
    - all labels per window
    
    @param data_x: ids for train
    @param data_y: ids for train
    @param ws: ids for train
    @param ss: ids for train
    @param label_pos_end: ids for train
    '''    


    print("Sliding window: Creating windows {} with step {}".format(ws, ss))
    
    data_x = sliding_window(data_x,(ws,data_x.shape[1]),(ss,1))
    
    # Label from the end
    if label_pos_end:
        data_y = np.asarray([[i[-1]] for i in sliding_window(data_y,(ws,data_y.shape[1]),(ss,1))])
    else:
    
        #Label from the middle
        if False:
            data_y_labels = np.asarray([[i[i.shape[0] // 2]] for i in sliding_window(data_y,(ws,data_y.shape[1]),(ss,1))])
        else:
            count_l=[]
            idy = []
            #Label according to mode
            try:
                
                data_y_labels = []
                for sw in sliding_window(data_y,(ws,data_y.shape[1]),(ss,1)):
                    labels = np.zeros((20)).astype(int)
                    count_l = np.bincount(sw[:,0], minlength = NUM_CLASSES)
                    idy = np.argmax(count_l)
                    attrs = np.sum(sw[:,1:], axis = 0)
                    attrs[attrs > 0] = 1
                    labels[0] = idy  
                    labels[1:] = attrs
                    data_y_labels.append(labels)
                print(len(data_y_labels))
                data_y_labels = np.asarray(data_y_labels)
                
            
            except:
                print("Sliding window: error with the counting {}".format(count_l))
                print("Sliding window: error with the counting {}".format(idy))
                return np.Inf
            
            #All labels per window
            data_y_all = np.asarray([i[:] for i in sliding_window(data_y,(ws,data_y.shape[1]),(ss,1))])
    
    return data_x.astype(np.float32), data_y_labels.astype(np.uint8), data_y_all.astype(np.uint8)

def example_creating_windows_file(k, data_x, labels, data_dir):
        # Sliding window approach

    print("Starting sliding window")
    print(data_x.shape)
    print(labels.shape)
    X, y, y_all = opp_sliding_window(data_x, labels,
                                     sliding_window_length,
                                     sliding_window_step, label_pos_end = False)
    print(X.shape)
    print(y.shape)
    print(y_all.shape)
    counter_seq = 0
    value = 0
    if (X.shape[0]<y.shape[0]):
        value = X.shape[0]
    else:
        value = y.shape[0]
   # for f in range(X.shape[0]):
    for f in range(value):
       # try:
        sys.stdout.write('\r' + 'Creating sequence file '
                                'number {} with id {}'.format(f, counter_seq))
        sys.stdout.flush()

        # print "Creating sequence file number {} with id {}".format(f, counter_seq)
        seq = np.reshape(X[f], newshape = (1, X.shape[1], X.shape[2]))
        seq = np.require(seq, dtype=np.float)
        # interpolation
        dir = data_dir + "seq_"  + "_" + str(k) + "_" + str(counter_seq) + ".pkl"
        obj = {"data" : seq, "label" : y[f], "labels" : y_all[f]}
        #f = open(os.path.join(dir, 'seq_{0:06}.pkl'.format(counter_seq)), 'wb')
        f = open(dir, 'wb')
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        counter_seq += 1
        print("dumping")
        f.close()
 
def max_min_values(data):
    values = []
    
    #print(data.shape)
    
    for attr in range(data.shape[1]):
        attribute = []
        temp_max = np.max(data[:,attr])
        temp_min = np.min(data[:,attr])
        attribute.append(temp_min)
        attribute.append(temp_max)
        values.append(attribute)  
    
    return values


def normalize(data, min_max, string):
    #print(len(min_max), len(min_max[0]))
    
    for j in range(1,len(data[0])-1):
        data[:,j] = (data[:,j] - min_max[j-1][0])/(min_max[j-1][1] - min_max[j-1][0]) 
    test = np.array(data[:,1:31])
        
    if (string=="train"):
        if(np.max(test)>1.001):
            print("Error",np.max(test))
        if(np.min(test)<-0.001):
            print("Error",np.min(test))
    else:
        test[test > 1] = 1
        test[test < 0] = 0
    #data = data.reshape(data.shape[0],1,data.shape[1], data.shape[2])
    #data = torch.tensor(data)
    return data

def derivative(f,a,method='central',h=0.00001):
    '''Compute the difference formula for f'(a) with step size h.

    Parameters
    ----------
    f : function
        Vectorized function of one variable
    a : number
        Compute derivative at x = a
    method : string
        Difference formula: 'forward', 'backward' or 'central'
    h : number
        Step size in difference formula

    Returns
    -------
    float
        Difference formula:
            central: f(a+h) - f(a-h))/2h
            forward: f(a+h) - f(a))/h
            backward: f(a) - f(a-h))/h            
    '''
    ret = []
    for i in range(len(a)):
        res = (f(a[i] + h) - f(a[i] - h))/(2*h)
        ret.append(res)
    return ret  
        
if __name__ == '__main__':
    # The training, test and validation data have been separately interpolated and 
    # up sampled
    # up sampling rate
    
    #ws = (100,31)
    ws = (25,30) 
    ss = (10,30)     
    #ss = (25,31)
    sliding_window_length = 25   
    #sliding_window_length = 100    
    sliding_window_step = 5
    
    df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/JHMDB/train_data.csv')
    #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/train_data.csv')
    data = df.values
    data_new = data[:,1:31]
    attr = np.zeros((100,1))
    value = max_min_values(data_new)
 
    
    data = normalize(data,value, "train")
    print("train data normalized")
    data_new = data[:,1:31]
    
    #data_dir = "/media/shrutarv/Drive1/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/"
    #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/train_data25_39.csv')
    data_dir =  '/data/sawasthi/data/JHMDB/trainData/'
    #data_dir = 'S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/pkl/'
    label = data[:,31].astype(int)
    lab = np.zeros((len(label),20), dtype=int)
    lab[:,0] = label
    #X = data[:,1:31]
    X = data_new
    k = 0
    example_creating_windows_file(k, X, lab, data_dir)
    print("train data pickled")
    
    #data_dir = 'S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/pkl'
    data_dir =  '/data/sawasthi/data/JHMDB/testData/'
    df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/JHMDB/test_data.csv')
    data = df.values
    data = normalize(data,value, "test")
    print("test data normalized")
    data_new = data[:,1:31]
    label = data[:,31].astype(int)
    lab = np.zeros((len(label),20), dtype=int)
    lab[:,0] = label
    X = data_new
    k = 0
    example_creating_windows_file(k, X, lab, data_dir)
    print("test data pickled")
    
    data_dir =  '/data/sawasthi/data/JHMDB/validationData/'
    #data_dir =  '/data/sawasthi/data/JHMDB/validationData/'
    df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/JHMDB/validation_data.csv')
    data = df.values
    data = normalize(data,value, "validation")
    print("validation data normalized")
    data_new = data[:,1:31]

    label = data[:,31].astype(int)
    lab = np.zeros((len(label),20), dtype=int)
    lab[:,0] = label
    X = data_new
    k = 0
    example_creating_windows_file(k, X, lab, data_dir)
    print("validation data pickled")
    #os.chdir('/vol/actrec/DFG_Project/2019/Mbientlab/recordings_2019/07_IMU_synchronized_annotated/' + folder_name)
    #os.chdir("/vol/actrec/DFG_Project/2019/MoCap/recordings_2019/14_Annotated_Dataset/" + folder_name)
    #os.chdir("/media/shrutarv/Drive1/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/S13/")
    #os.chdir("S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/" + folder_name)
    #os.chdir("S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/OMoCap data/" + folder_name)
    
    
          
    
