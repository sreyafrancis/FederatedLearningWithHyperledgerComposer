# We want to use the connect Python with Hyperledger through REST APIs.
import requests
from hashlib import sha256
import random
from urllib.parse import urljoin
import urllib
import json

URL = 'http://localhost:3000'
API_URL = urljoin(URL, 'api/')
ORG = 'org.martinezfrancis.federatedlearning'
API_ORG_URL =  urljoin(API_URL, ORG)
N = 1
V = 3
TRAINING_MODEL_ID = 'trainingmodel'

r = requests.get(url=API_ORG_URL + ".Device")
d_response = r.json()
# Get current training model
r = requests.get(url=API_ORG_URL + ".TrainingModel")
t_response = r.json()

# # Create initial Training Model
post_data = {
  "$class": ORG + ".TrainingModel",
  "modelId": TRAINING_MODEL_ID,
  "version": 0
}
response = requests.post(url=API_ORG_URL+".TrainingModel", data=post_data)
print(response.status_code)
print(response.json())

# For each device, upload a Gradient. Gradient should be off-chain (csv perhaps) and only the hash is on-chain
# Create N new devices
for i in range(N):
  # Create a new device
  device_id = random.randint(000, 999)
  device_id = 5532

  post_data = {
    "$class": ORG + ".Device",
    "deviceId": device_id
  }
  #print(post_data)
  r = requests.post(url=API_ORG_URL+".Device", data=post_data)
  response = r.json()
  #print(response.status_code)
  #print(response)

# Upload new gradients for V rounds
for v in range(V):
  if v != 0:
    new_version = {"version":v} # Increment the training version
    r = requests.put(url=API_ORG_URL+".TrainingModel/" + TRAINING_MODEL_ID, data=new_version)

  # For each device, attempt to upload a Gradient
  # GET all devices. No parameters
  r = requests.get(url=API_ORG_URL+".Device")
  d_response = r.json()
  # Get current training model
  r = requests.get(url=API_ORG_URL + ".TrainingModel")
  t_response = r.json()
  t = [t for t in t_response if t['modelId'] == TRAINING_MODEL_ID][0]
  version = t['version']

  d_response = [d for d in d_response if d['deviceId'] == '5532']
  for d in d_response:
    # Upload a gradient through the smart contract UploadGradient
    data_cost = random.randint(11000, 11500)
    deviceId = str(d['deviceId'])
    device_version_id = deviceId + '_' + str(version)
    grad = 'This is going to be the hash of the 1_MB gradient_%s from version %d' % (deviceId, version)
    grad = grad.encode('utf-8')
    gradient_hash = sha256().hexdigest()

    post_data = {
    "$class": ORG + ".UploadGradient",
    "device": ORG + '.Device#' + deviceId,
    "trainingmodel": ORG + '.TrainingModel#' + TRAINING_MODEL_ID,
    "hash": gradient_hash,
    "dataCost": data_cost,
    "version": version}
    print(post_data)

    r = requests.post(url=API_ORG_URL + '.UploadGradient', data=post_data)
    response = r.json()
    if r.status_code != 200:
      print("Error: " + str(response)) # gradients already exist
    else:
      print("Success: " + str(response))

    # Get token rewarded for this upload
    token_url = API_ORG_URL+'.Token/' + deviceId + '_' + str(version)
    r = requests.get(url=token_url)
    token_response = r.json()
    #print(r.status_code)
    print(token_response)

# Filter all the gradient and tokens belonging to a given device
deviceIdQuery = 291
r = requests.get(url='http://localhost:3000/api/org.martinezfrancis.federatedlearning.Token')
response = r.json()
for res in response:
  if str(deviceIdQuery) + '_' in res['deviceVersionId']:
    print(res)

r = requests.get(url='http://localhost:3000/api/org.martinezfrancis.federatedlearning.Gradient')
response = r.json()
for res in response:
  if str(deviceIdQuery) + '_' in res['deviceVersionId']:
    print(res)