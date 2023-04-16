import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle

FULL_DATASET_RIGHT = 'combined_full_data_right.csv'
FULL_DATASET_LEFT = 'combined_full_data_left.csv'

OUTPUT_FOLDER = 'output_train_test/'

OUTPUT_PCA_TRAIN_DATASET_RIGHT = OUTPUT_FOLDER + 'train_data_pca.csv'
OUTPUT_PCA_TEST_DATASET_RIGHT = OUTPUT_FOLDER + 'test_data_pca.csv'
OUTPUT_PCA_TRAIN_DATASET_LEFT = OUTPUT_FOLDER + 'train_data_pca_l.csv'
OUTPUT_PCA_TEST_DATASET_LEFT = OUTPUT_FOLDER + 'test_data_pca_l.csv'

PCA_RIGHT = 'pca.pkl'
SCALER_RIGHT = 'scaler.pkl'

PCA_LEFT = 'pca_left.pkl'
SCALER_LEFT = 'scaler_left.pkl'

if __name__ == "__main__":
    full_dataset = pd.read_csv(FULL_DATASET_RIGHT, header=0)
    x = full_dataset.iloc[:, 2:62]
    y = full_dataset.iloc[:, 1].values

    # print correlation matrix
    matrix = x.corr()
    pd.set_option("display.max_columns", None)


    # PCA
    scaler = StandardScaler()
    scaler.fit(x)

    pca = PCA(n_components=16)
    pca_transformed = pca.fit_transform(scaler.transform(x))

    plot = plt.scatter(pca_transformed[:,0], pca_transformed[:,1], c=y)
    plt.legend(handles=plot.legend_elements()[0], labels=[0,1,2,3,4])
    plt.show()

    # split data into train test
    X_train, X_test, y_train, y_test = train_test_split(pca_transformed, y, test_size=0.2, random_state=1)

    train_dataset = np.hstack((X_train, np.reshape(y_train, (len(y_train), 1))))
    test_dataset = np.hstack((X_test, np.reshape(y_test, (len(y_test), 1))))

    column_values = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6', 'feature7', 'feature8', 'feature9', 'feature10', 'feature11', 'feature12', 'feature13', 'feature14', 'feature15', 'feature16', 'action']
     
    # make data into dataframe
    pd_train_dataset = pd.DataFrame(data=train_dataset, columns=column_values).astype({'action': 'int32'})
    pd_test_dataset = pd.DataFrame(data=test_dataset, columns=column_values).astype({'action': 'int32'})

    print(pd_train_dataset)

    
    pd_train_dataset.to_csv(OUTPUT_PCA_TRAIN_DATASET_RIGHT)
    pd_test_dataset.to_csv(OUTPUT_PCA_TEST_DATASET_RIGHT)

    with open(PCA_RIGHT, 'wb') as pickle_file:
        pickle.dump(pca, pickle_file)

    with open(SCALER_RIGHT, 'wb') as pickle_file:
        pickle.dump(scaler, pickle_file)
    