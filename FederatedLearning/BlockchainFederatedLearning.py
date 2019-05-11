import os
import random
import data.federated_data_extractor 
from federatedlearner import NNWorker
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
N = 5
V = 3

def main():
    ids = random.sample(range(10000, 99999 + 1), N)
    # Distribute data into N subsets
    os.system('python3 -d data/federated_data_extractor.py -n %d' %N)


    # Version 0
    ## Create model
    os.system('python3 globalmodel.py -v 0 -a')

    for version in range(0, V): # V-1 is the final version
        ## Train N clients - Record and Reward in Blockchain
        for i in range(N):

            os.system('python3 client.py -v %d -d data/federated_data_%d.d -e 1 -i %s -a' % (version, i, str(ids[i])))

        # Version n > 0

        ## Aggregate model
        next_version = version + 1
        os.system('python3 globalmodel.py -v %d -a' % next_version)

    create_csv()
    version_accuracy()

def version_accuracy():

    path = 'model/'
    models = []
    acc = []
    version = []

    for file in os.listdir(path):
        weights = np.load(path + file, allow_pickle=True)
        m = dict(weights.item())
        dataset = data.federated_data_extractor.load_data("data/mnist.d")
        worker = NNWorker(None, None, dataset['test_images'], dataset['test_labels'], 0, "validation")
        worker.build(m)
        accuracy = worker.evaluate()
        models.append(file)
        acc.append(accuracy)
        model_re = 'global\_model\_(.+?)\.npy'
        match = re.search(model_re, file)
        model_version = match.group(1)
        version.append(int(model_version))


        worker.close()

    accuracy_df = pd.DataFrame({'model':models, 'acc': acc, 'version': version})
    accuracy_df = accuracy_df.sort_values(by='version').reset_index(drop=True)

    for idx, row in accuracy_df.iterrows():
        print('Accuracy of {} is {}'.format(row['model'], row['acc']))

    plt.plot(accuracy_df['acc'].values)
    plt.xticks(accuracy_df['version'].values)
    plt.xlabel('Version No.')
    plt.ylabel('Accuracy')
    plt.title('Federation Learning with %d devices' % N)
    plt.show()




def create_csv():
    os.system('python3 offchain-database.py')
    offchain_df = pd.read_csv('DeltaOffChainDatabase.csv')
    print(offchain_df.loc[:, :])




if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-n', '--Clients', default=5, type=int, help='Number of clients')
    parser.add_argument('-v', '--versions', default=3, type=int, help='Number of training rounds')

    args = parser.parse_args()
    N = args.Clients
    V = args.versions

    main()