#import glob
import os
import csv
import re
from urllib.parse import urljoin
import requests

path = os.path.join(os.getcwd(),'clients')
URL = 'http://localhost:3000'
API_URL = urljoin(URL, 'api/')
ORG = 'org.martinezfrancis.federatedlearning'
API_ORG_URL =  urljoin(API_URL, ORG)

i = 1

#Device_gradient_path = glob.glob(path+"*.npy")
Device_gradient_path = [f for f in os.listdir('clients/')]
print (Device_gradient_path)
n_devices = len(Device_gradient_path)

client_details = dict()


for gradient_file in Device_gradient_path:
    # Device ID
    device_re = 'device(\d+)'
    match = re.search(device_re, gradient_file)
    device_id = match.group(1)
    # Version
    model_re = 'v(.+?)\.npy'
    match = re.search(model_re, gradient_file[6:])
    model_version = match.group(1)
    # Get DataCost of gradient with id deviceID_version
    gradient_url = API_ORG_URL + '.Gradient/' + device_id + '_' + str(model_version)
    r = requests.get(url=gradient_url)
    gradient_response = r.json()
    if r.status_code == 200:
        data_cost = gradient_response['dataCost']

        client_details[gradient_file] = {"device_id": device_id, "version": model_version, "data_cost": data_cost}
    else:
        print('No Gradient present with device_version_id = %s' % str(device_id) + '_' + str(model_version))

csvData = [['Device_id', 'Device_delta_path', 'Model_version', 'dataCost']]
csvData = [[] for _ in range(n_devices+1)]
csvData[0] = ['Device_id', 'Device_delta_path', 'Model_version', 'dataCost']

for k,v in client_details.items():
    path = 'clients/' + k
    csvData[i].append(v['device_id'])
    csvData[i].append(path)
    csvData[i].append(v['version'])
    csvData[i].append(v['data_cost'])
    i += 1

with open('DeltaOffChainDatabase.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(csvData)

csvFile.close()
    
