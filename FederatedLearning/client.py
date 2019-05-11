"""
  - Blockchain for Federated Learning - 
    Client script 
"""
from federatedlearner import *
from urllib.parse import urljoin
import requests
import data.federated_data_extractor as dataext
import numpy as np
import time
import sys
from hashlib import sha256
URL = 'http://localhost:3000'
API_URL = urljoin(URL, 'api/')
ORG = 'org.martinezfrancis.federatedlearning'
API_ORG_URL =  urljoin(API_URL, ORG)
RESTAPI_BOOL = True
TRAINING_MODEL_ID = 'trainingmodel'

class Client:
    def __init__(self,dataset):
        self.id = id
        #self.miner = miner
        self.dataset = self.load_dataset(dataset)

    def load_dataset(self,name):

        ''' 
        Function to load federated data for client side training
        '''
        if name==None:
            return None
        return dataext.load_data(name)

    def update_model(self, model_path, steps, epochs):

        ''' 
        Function to compute the client model update based on 
        client side training
        '''
        reset()
        t = time.time()
        worker = NNWorker(self.dataset['train_images'],
            self.dataset['train_labels'],
            self.dataset['test_images'],
            self.dataset['test_labels'],
            len(self.dataset['train_images']),
            self.id,
            steps)

        model = np.load(model_path, allow_pickle=True) #TODO naming convention of global model
        model = model.item()
        worker.build(model)
        for e in range(1, epochs+1):
            worker.train()
            worker.build(worker.get_model())
        update = worker.get_model()
        accuracy = worker.evaluate()
        worker.close()
        # Calculate Gradient from update and original
        gradient = {}
        for key in update:
            if key != 'size':
                gradient[key] = np.subtract(update[key], model[key])
        return gradient, accuracy, time.time()-t


    def work(self,device_id, model_path, epochs, version):
        ''' 
        Function to check the status of mining and wait accordingly to output 
        the final accuracy values 
        '''

        gradient, accuracy, cmp_time = client.update_model(model_path, 10, epochs)
        # Determine Data Cost
        data_cost = self.dataset['train_labels'].shape[0]
        print("Accuracy local update---------" + str(device_id) + "--------------:", accuracy)
        client_gradient_path = "clients/device" + str(device_id) + "_model_v" + str(version) + ".npy"
        try:
            np.save(client_gradient_path, gradient)
            #  Record and Reward
            if RESTAPI_BOOL:
                try:
                    # If device doesn't exist, create device
                    post_data = {
                        "$class": ORG + ".Device",
                        "deviceId": device_id
                    }
                    requests.post(url=API_ORG_URL + ".Device", data=post_data)

                    # Post Gradient of Device
                    # Upload a gradient through the smart contract UploadGradient
                    device_id = str(device_id)
                    grad_str = str(gradient).encode('utf-8')
                    gradient_hash = sha256(grad_str).hexdigest()

                    post_data = {
                        "$class": ORG + ".UploadGradient",
                        "device": ORG + '.Device#' + device_id,
                        "trainingmodel": ORG + '.TrainingModel#' + TRAINING_MODEL_ID,
                        "hash": gradient_hash,
                        "dataCost": data_cost,
                        "version": version
                    }

                    r = requests.post(url=API_ORG_URL + '.UploadGradient', data=post_data)
                    response = r.json()
                    if r.status_code != 200:
                        print("Error: " + str(response))  # gradients already exist
                    else:
                        print("Success: " + str(response))

                    # Get token rewarded for this upload
                    token_url = API_ORG_URL + '.Token/' + device_id + '_' + str(version)
                    r = requests.get(url=token_url)
                    token_response = r.json()
                    # print(r.status_code)
                    print(token_response)


                except:
                    sys.exit('Could not record Gradient in Hyperledger')
        except:
            print('There was an error in calculating the client\'s Gradient, for device: %s and version %s' % (str(device_id), str(version)))

if __name__ == '__main__':
    
    from argparse import ArgumentParser
    parser = ArgumentParser()
    #parser.add_argument('-m', '--trainingmodel_path', default='model/global_model_0.npy', help='Path to model')
    parser.add_argument('-d', '--dataset', default='data/mnist.d', help='Path to dataset')
    parser.add_argument('-e', '--epochs', default=1,type=int, help='Number of epochs')
    parser.add_argument('-v', '--version', default=0, type=int, help='Training version number')
    parser.add_argument('-i', '--id', default=11111, type=int, help='Device ID, 5 digit integer')
    parser.add_argument('-a', '--RESTAPI', action='store_true', help='REST API boolean')

    import os
    if not os.path.exists("clients"):
        os.makedirs("clients")

    args = parser.parse_args()
    client = Client(args.dataset)
    trainingmodel_path = 'model/global_model_%d.npy' % int(args.version)
    RESTAPI_BOOL = args.RESTAPI
    print("--------------")
    print(client.id," Dataset info:")
    dataext.get_dataset_details(client.dataset)
    #Data_size, Number_of_classes = dataext.get_dataset_details(client.dataset)
    print("--------------")
    device_id = args.id
    print(device_id,"device_id")
    print("--------------")
    client.work(device_id, trainingmodel_path, args.epochs, args.version)
