from federatedlearner import *
import numpy as np
import os
import sys
import requests
from urllib.parse import urljoin

ETA = 0.1 # Aggregation factor T = T + ETA*grad
URL = 'http://localhost:3000'
API_URL = urljoin(URL, 'api/')
ORG = 'org.martinezfrancis.federatedlearning'
API_ORG_URL =  urljoin(API_URL, ORG)
TRAINING_MODEL_ID = 'trainingmodel'
RESTAPI_BOOL = True

def main(version):
    # Initialize model
    if version == 0:
        model = NNWorker()
        model.build_base()
        initial_path = 'model/global_model_0.npy'
        model.model_to_npy(initial_path)
        if RESTAPI_BOOL:
            try:
                # Create Training Model in Hyperledger
                post_data = {
                    "$class": ORG + ".TrainingModel",
                    "modelId": TRAINING_MODEL_ID,
                    "version": 0
                }
                response = requests.post(url=API_ORG_URL + ".TrainingModel", data=post_data)
                if(response.status_code == 200):
                    print('Training model version %d successfully created' % int(version))
            except:
                sys.exit('Could not record Training Model in Hyperledger')
        print('--- %s saved in directory /model ---' % initial_path)

    else:
        # Aggregate
        prev_version = version-1
        files = [f for f in os.listdir('clients/') if 'v' + str(prev_version) + '.npy' in f]
        client_num = len(files)
        if client_num <= 0:
            sys.exit('No gradients to aggregate')
        aggregated_grad = np.load('clients/' + files[0], allow_pickle=True)
        aggregated_grad = aggregated_grad.item()
        for f in files[1:]:
            grad = np.load('clients/' + f, allow_pickle=True)
            grad = grad.item()
            for key in grad:
                aggregated_grad[key] = np.add(aggregated_grad[key], grad[key])
        for key in aggregated_grad: # Do this after adding to avoid round-off errors of too small of values
            aggregated_grad[key] *= (ETA/client_num)

        global_model_path = 'model/global_model_%d.npy' % prev_version
        global_model_parameters = np.load(global_model_path, allow_pickle=True)
        global_model_parameters = global_model_parameters.item()
        for key in global_model_parameters:
            if key == 'size':
                pass
            else:
                global_model_parameters[key] = np.add(global_model_parameters[key], aggregated_grad[key])
        global_model_path = 'model/global_model_%d.npy' % version
        np.save(global_model_path, global_model_parameters )
        if RESTAPI_BOOL:
            try:
                # Create Training Model in Hyperledger
                new_version = {"version": version}
                response = requests.put(url=API_ORG_URL + ".TrainingModel/%s" %TRAINING_MODEL_ID, data=new_version)
                if(response.status_code == 200):
                    print('Training model successfully updated to version %d' % int(version))
            except:
                sys.exit('Could not record Training Model in Hyperledger')
        print('--- %s saved in directory /model ---' % global_model_path)

        # TODO Check accuracy of previous version with current version

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-v', '--version', default=0, type=int, help='Training version number')
    parser.add_argument('-a', '--RESTAPI', action='store_true', help='REST API boolean')

    import os

    if not os.path.exists("model"):
        os.makedirs("model")

    args = parser.parse_args()
    RESTAPI_BOOL = args.RESTAPI
    main(args.version)