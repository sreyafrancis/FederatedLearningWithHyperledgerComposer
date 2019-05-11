# Hyperledger Fabric - REST API

Install the prerequisites and begin running Fabric.

## Getting Started

Hyperledger Fabric requires either a MacOS or a Linux OS to develop and run. These instructions are for Linux. 
If you are using Windows, follow the tutorial [here](https://medium.com/cochain/hyperledger-fabric-on-windows-10-26723116c636), though this should be done on a UNIX system.

### Prerequisites

Download all prerequisites with the following.

```
curl -O https://hyperledger.github.io/composer/latest/prereqs-ubuntu.sh

chmod u+x prereqs-ubuntu.sh
```

Execute and install the prerequisites.

```
./prereqs-ubuntu.sh
```
Close the command line and reopen before continuing. Once reopened, ensure you have `npm`, `node`, and `docker` installed with `npm --version`, `node --version` and `docker --version`.

For more details, visit [Hyperledger - Installing Prereqs](https://hyperledger.github.io/composer/v0.16/installing/installing-prereqs.html).

In addition, ensure you have the following libraries installed for Python.
`requests`, `hashlib`, `urllib`


### Installing CLI Tools

Next, we install our CLI tools that are needed to start up Fabric.

```
npm install -g composer-cli
npm install -g composer-rest-server
npm install -g generator-hyperledger-composer
```
For more details visit [Hyperledger - CLI](https://hyperledger.github.io/composer/v0.16/installing/development-tools.html).

## Install Hyperledger Fabric

cd `<path_to_projectDir>/HyperledgerComposer`

We now download and start Fabric.

```
export FABRIC_VERSION=hlfv12
cd <path_to_projectDir>/HyperledgerComposer/fabric-dev-servers
./downloadFabric.sh
./startFabric.sh
./createPeerAdminCard.sh
```

If `./downloadFabric.sh` gives you a 'Permissioned Denied' error, use `sudo` prior to the command.

IBM has a great tutorial on this [here](https://developer.ibm.com/tutorials/cl-deploy-interact-extend-local-blockchain-network-with-hyperledger-composer/) and [here](https://medium.freecodecamp.org/how-to-build-a-blockchain-network-using-hyperledger-fabric-and-composer-e06644ff801d).

### Executing the .bna file into a REST API

We are holding our `blockchain-federated-learning.bna` file in the `HyperledgerComposer\BlockFDL` directory.

`cd <path_to_projectDir>/HyperledgerComposer/BlockDFL`

Run the network and launch the REST API with the following.

```
composer network install --card PeerAdmin@hlfv1 --archiveFile blockchain-federated-learning.bna
composer network start --networkName blockchain-federated-learning --networkVersion 0.0.2-deploy.44 --networkAdmin admin --networkAdminEnrollSecret adminpw --card PeerAdmin@hlfv1 --file networkadmin.card

composer-rest-server -c admin@blockchain-federated-learning -n always -u true -w true
```


### REST API
The REST API explorer should now be viewable in the browser at `http://localhost:3000/explorer`. Use this to integrate the REST API into your code and see the effects on the network.

# FederatedLearning - Python

## Installation
------------

Before you do anything else you will first need to install the following python 
packages:

   `absl-py==0.5.0`
   `astor==0.7.1`
   `certifi==2018.10.15`
   `chardet==3.0.4`
   `Click==7.0`
   `cycler==0.10.0`
   `gast==0.2.0`
   `grpcio==1.15.0`
   `h5py==2.8.0`
   `idna==2.7`
   `Jinja2==2.10`
   `Keras-Applications==1.0.6`
   `Keras-Preprocessing==1.0.5`
   `kiwisolver==1.0.1`
   `Markdown==3.0.1`
   `MarkupSafe==1.0`
   `matplotlib==3.0.0`
   `numpy==1.15.2`
   `protobuf==3.6.1`
   `pyparsing==2.2.2`
   `python-dateutil==2.7.3`
   `requests==2.20.0`
   `six==1.11.0`
   `tensorboard==1.11.0`
   `termcolor==1.1.0`
   `urllib3==1.24`
   `Werkzeug==0.14.1`
   `ItsDangerous==1.1.0`
   `tensorflow==1.11.0`
   `matplotlib=3.0.3`
   
These are specified in the `src/packages_to_install.txt` file.

Also ensured you have python3-tk installed: `sudo apt-get install python3-tk`
   
This project was built using Python3 but may work with Python2 given a few 
minor tweaks.

## Execution
___________

All the steps for running the code from beginning to end are available in `BlockchainFederatedLearning.py`, which takes a single parameter `-n` which is the number of clients/devices used for training. The code is executed with 
```
python3 BlockchainFederatedLearning.py -n <numberOfDevices>
```

### Preprocessing

The code begins with a call to `python3 -d data/federatd_data_extractor.py -n <numberOfDevices>` which splits the MNIST dataset into n subsets and creates a file `federated_data_n.d` for each.

### Model Initialization

The model is initialized using normally distributed weights. This is a call to `python3 globalmodel.py -v 0 -a` which both creates a file `global_model_0.npy` containing the model weights and calls the Hyperledger Fabric API to create a TrainingModel asset with version 0.

### Training

The federated training is performed, where for each device, we call `python3 client.py -v 0 -d data/federated_data_i.d -e 1 -i <id> -a` which trains the model to create a gradient which is saved to a file `device<id>_model_v0.npy` and also uploads the gradient hash with version and datacost to the Hyperledger fabric API which creates a Gradient asset and a Token asset with the value equal to the datacost.

### Aggregation

The aggregation of model 0 is performed with a call to `python3 globalmodel.py -v 1 -a` which aggregates all gradients from version 0, then updates the model. The Hyperledger Fabric asset TrainingModel version is also updated.

We perform the training and aggregation for V rounds total.
