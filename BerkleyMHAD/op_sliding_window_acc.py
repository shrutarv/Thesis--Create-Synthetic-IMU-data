import pandas as pd
import sys
import numpy as np
import os
import pickle
from sliding_window import sliding_window
#from pre_processing import *
import glob
import csv
import scipy.interpolate as sp
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline as IUS

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
    #print(data_x.shape)
    #print(labels.shape)
    X, y, y_all = opp_sliding_window(data_x, labels,
                                     sliding_window_length,
                                     sliding_window_step, label_pos_end = False)
    #print(X.shape)
    #print(y.shape)
   # print(y_all.shape)
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
        #print("dumping")
        f.close()
 
def max_min_values(data, values):
    temp_values = []
    for i in range(data.shape[1]):
        attribute = []
        temp_max = np.max(data[:,i])
        temp_min = np.min(data[:,i])
        if (values[i][0] < temp_min):
            attribute.append(values[i][0])
        else:
            attribute.append(temp_min)
        if(values[i][1] > temp_max):
            attribute.append(values[i][1])
        else:
            attribute.append(temp_max)
        temp_values.append(attribute)  
    values = temp_values
    return values


def normalize(data_n, min_max, string):
    #print(len(min_max), len(min_max[0]))
    
    for j in range(len(data_n[0])):
        data_n[:,j] = (data_n[:,j] - min_max[j][0])/(min_max[j][1] - min_max[j][0]) 
    test = np.array(data_n[:,1:data_n.shape[1]])
        
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
    return data_n


def plot_graphs(t_sampled,data,acceleration,sampled_dat):
    plt.figure()
    plt.plot(data[:500,0],data[:500,1],'k')
    #plt.plot(data[1:500,0],data[1:500,3],'b')
    #plt.plot(data[1:100,0],data[1:100,5],'g')
    #plt.plot(data[1:100,0],data[1:100,13],'r')
    #plt.plot(data[1:100,0],data[1:100,15],'y')
    #plt.plot(data[1:100,0],data[1:100,11],'c')
    
    plt.figure()
    plt.plot(t_sampled[:100],sampled_dat[:100,0],'k')
    #plt.plot(t_sampled[1:100],sampled_dat[1:100,2],'b')
    #plt.plot(t_sampled[1:300],sampled_dat[1:300,4],'g')
    #plt.plot(t_sampled[1:300],sampled_dat[1:300,12],'r')
    #plt.plot(t_sampled[1:300],sampled_dat[1:300,14],'y')
    #plt.plot(t_sampled[1:300],sampled_dat[1:300,10],'c')
    
    plt.figure()
    plt.plot(t_sampled[:100],acceleration[:100,0],'k')
    #plt.plot(t_sampled[1:100],acceleration[1:100,2],'b')
    #plt.plot(t_sampled[1:300],acceleration[1:300,4],'g')
    #plt.plot(t_sampled[1:300],acceleration[1:300,12],'r')
    #plt.plot(t_sampled[1:300],acceleration[1:300,14],'y')
    #plt.plot(t_sampled[1:300],acceleration[1:300,10],'c')



if __name__ == '__main__':   
    # The training, test and validation data have been separately interpolated and 
    # up sampled
    # up sampling rate
    down = 5
    #ws = (100,31)
    ws = (100,30) 
    ss = (15,30)     
    #ss = (25,31)
    sliding_window_length = 100   
    #sliding_window_length = 100    
    sliding_window_step = 15
    m2 = np.repeat(-999999,102)
    m1 = np.repeat(999999,102)
    m1 = np.reshape(m1,(len(m1),1))
    m2 = np.reshape(m2,(len(m2),1))
    v = np.concatenate((m1,m2),axis=1)
    #value =  np.load('S:/MS A&R/4th Sem/Thesis/Berkley MHAD/SkeletalData-20200922T160342Z-001/train/value.npy')
    value = np.load('/data/sawasthi/data/BerkleyMHAD/value.npy')
    k = 0
    #for df in pd.read_csv("S:/MS A&R/4th Sem/Thesis/Berkley MHAD/SkeletalData-20200922T160342Z-001/train/train_data.csv", chunksize=10000):
    for df in pd.read_csv("/home/sawasthi/BerkleyMHAD/train_data.csv", chunksize=10000):
        
        #df = pd.read_csv('/data/sawasthi/data/BerkleyMHAD/train_data.csv')
        #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/train_data.csv')
        data = df.values
        data_new = data[:,1:103]
        #value = max_min_values(data_new,value)
        #save_data = np.asarray(value)
        #np.save('S:/MS A&R/4th Sem/Thesis/Berkley MHAD/SkeletalData-20200922T160342Z-001/train/value.npy',save_data)
        #break;
        data_norm = normalize(data_new,value, "train")
        print("train data normalized")
        if np.any(data_norm)>1:
            print("error")
        if np.any(data_norm)<0:
            print("error")
                
                
        # time sampled
        x_sampled = np.arange(np.min(data[:,0]), np.max(data[:,0]), 0.01)
        y_sampled = np.zeros((int(np.ceil(data.shape[0]/down)),1))
        sampled_data = np.zeros((len(x_sampled),1))
        #u = IUS(data[:,0],data[:,1])
        #out = u(x_sampled)
        #u_der = u.derivative(2)
        #a = u_der(out)
        for i in range(data_norm.shape[1]):
                #for index in range(12,len(data[0])*up-12):
                    
                #data_new = data[index-12:index+12,:]   
             
             #f = sp.interp1d(data[:,0],data[:,i], kind='linear')
             #acc = np.diff(data[:,i],2)
             #sampled_data = f(x_sampled)
             resample = sp.splrep(data[:,0],data_norm[:,i])
             sampled = sp.splev(x_sampled,resample)
             acc = sp.splev(data[:,0],resample, der=2)
             acc_sampled = acc[::down].copy()
             y_sampled = np.concatenate((y_sampled,np.reshape(acc_sampled,(len(acc_sampled),1))),axis=1)
             sampled_data = np.concatenate((sampled_data,np.reshape(sampled,(len(sampled),1))),axis=1)
         
             #y_sampled.append(f(x_sampled))
            # time_sampled =data[:,0][::down] 
            # plt.plot(data[1:400,0],acc[1:400],'g',time_sampled[1:80],acc_sampled[1:80],'b')
            # plt.plot(data[1:500,0],data[1:500,70],'g')
             
        data_sampled = y_sampled[:,1:]
        #plot_graphs(x_sampled,data,data_sampled,sampled_data[:,1:])
        #print("normalizing sampled data")
        #val = max_min_values(data_sampled,v)
        #data_sampled = normalize(data_sampled,val, "train")
        #print("sampled data normalized")
        #data_dir = "/media/shrutarv/Drive1/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/"
        #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/train_data25_39.csv')
        data_dir =  '/data/sawasthi/data/BerkleyMHAD/trainData/'
        #data_dir = 'S:/MS A&R/4th Sem/Thesis/Berkley MHAD/pkl files/'
        label = np.repeat(data[:,103],down).astype(int)
        lab = np.zeros((len(label),20), dtype=int)
        lab[:,0] = label
        #X = data[:,1:31]
        X = data_sampled
        k += 1
        example_creating_windows_file(k, X, lab, data_dir)
        print("train data pickled")
    k = 0
    #for df in pd.read_csv("S:/MS A&R/4th Sem/Thesis/Berkley MHAD/SkeletalData-20200922T160342Z-001/train/test_data.csv", chunksize=10000):
    for df in pd.read_csv("/home/sawasthi/BerkleyMHAD/test_data.csv", chunksize=10000):
        #data_dir = 'S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/pkl'
        data_dir =  '/data/sawasthi/data/BerkleyMHAD/testData/'
        #df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/JHMDB/test_data.csv')
        data = df.values
        data_new = data[:,1:103]
        data_norm = normalize(data_new,value, "test")
        print("test data normalized")
        # time sampled
        #x_sampled = np.linspace(np.min(data[:,0]), np.max(data[:,0]), len(data)*up)
        print("train data normalized")
        if np.any(data_norm)>1:
            print("error")
        if np.any(data_norm)<0:
            print("error")
        
        y_sampled = np.zeros((int(np.ceil(data.shape[0]/float(down))),1))
             
        for i in range(data_norm.shape[1]):
            #for index in range(12,len(data[0])*up-12):
                    
                #data_new = data[index-12:index+12,:]   
             
             #f = sp.interp1d(data[:,0],data[:,i], kind='linear')
             #acc = np.diff(data[:,i],2)
             #sampled_data = f(x_sampled)
             resample = sp.splrep(data[:,0],data_norm[:,i])
             acc = sp.splev(data[:,0],resample, der=2)
             acc_sampled = acc[::down].copy()
             #print(y_sampled.shape, acc_sampled.shape)
             y_sampled = np.concatenate((y_sampled,np.reshape(acc_sampled,(len(acc_sampled),1))),axis=1)
              
             #y_sampled.append(f(x_sampled))
            # time_sampled =data[:,0][::down] 
            # plt.plot(data[1:400,0],acc[1:400],'g',time_sampled[1:80],acc_sampled[1:80],'b')
            # plt.plot(data[1:500,0],data[1:500,70],'g')
             
        data_sampled = y_sampled[:,1:]
        #print("normalizing sampled data")
        #data_sampled = normalize(data_sampled,val, "test")
        #print("sampled data normalized")
        #data_dir = "/media/shrutarv/Drive1/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/"
        #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/train_data25_39.csv')
       
        #data_dir = 'S:/MS A&R/4th Sem/Thesis/Berkley MHAD/pkl files/'
        label = np.repeat(data[:,103],down).astype(int)
        lab = np.zeros((len(label),20), dtype=int)
        lab[:,0] = label
        #X = data[:,1:31]
        X = data_sampled
        k += 1
        example_creating_windows_file(k, X, lab, data_dir)
        print("test data pickled")
    
    k = 0
    for df in pd.read_csv("/home/sawasthi/BerkleyMHAD/validation_data.csv", chunksize=10000):
    #for df in pd.read_csv("S:/MS A&R/4th Sem/Thesis/Berkley MHAD/SkeletalData-20200922T160342Z-001/train/validation_data.csv", chunksize=10000):
            
        data_dir =  '/data/sawasthi/data/BerkleyMHAD/validationData/'
        #data_dir =  '/data/sawasthi/data/JHMDB/validationData/'
        #df = pd.read_csv('/data/sawasthi/Thesis--Create-Synthetic-IMU-data/JHMDB/validation_data.csv')
        data = df.values
        data_new = data[:,1:103]
        data_norm = normalize(data_new,value, "validation")
        print("validation data normalized")
        if np.any(data_norm)>1:
            print("error")
        if np.any(data_norm)<0:
            print("error")
        
        # time sampled
        #x_sampled = np.linspace(np.min(data[:,0]), np.max(data[:,0]), len(data)*up)
        y_sampled = np.zeros((int(np.ceil(data.shape[0]/float(down))),1))
                
        for i in range(data_norm.shape[1]):
             resample = sp.splrep(data[:,0],data_norm[:,i])
             acc = sp.splev(data[:,0],resample, der=2)
             acc_sampled = acc[::down].copy()
             
             y_sampled = np.concatenate((y_sampled,np.reshape(acc_sampled,(len(acc_sampled),1))),axis=1)
               
        data_sampled = y_sampled[:,1:]
        #print("normalizing sampled data")
        #data_sampled = normalize(data_sampled,val, "validation")
       # print("sampled data normalized")
        #data_dir = "/media/shrutarv/Drive1/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/Windows2/"
        #df = pd.read_csv('S:/MS A&R/4th Sem/Thesis/J-HMDB/joint_positions/train/train_data25_39.csv')
       
        #data_dir = 'S:/MS A&R/4th Sem/Thesis/Berkley MHAD/pkl files/'
        label = np.repeat(data[:,103],down).astype(int)
        lab = np.zeros((len(label),20), dtype=int)
        lab[:,0] = label
        #X = data[:,1:31]
        X = data_sampled
        k += 1
        example_creating_windows_file(k, X, lab, data_dir)  
        print("validation data pickled")
        #os.chdir('/vol/actrec/DFG_Project/2019/Mbientlab/recordings_2019/07_IMU_synchronized_annotated/' + folder_name)
        #os.chdir("/vol/actrec/DFG_Project/2019/MoCap/recordings_2019/14_Annotated_Dataset/" + folder_name)
        #os.chdir("/media/shrutarv/Drive1/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/S13/")
        #os.chdir("S:/MS A&R/4th Sem/Thesis/LaRa/IMU data/IMU data/" + folder_name)
        #os.chdir("S:/MS A&R/4th Sem/Thesis/LaRa/OMoCap data/OMoCap data/" + folder_name)
        #with open('S:/MS A&R/4th Sem/Thesis/Berkley MHAD/pkl files/seq__0_67.pkl', 'rb') as f:
         #   d2 = pickle.load(f)

        
              
        
