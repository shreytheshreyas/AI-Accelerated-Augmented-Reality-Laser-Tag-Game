import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

SHIELD_DATASET = 'shield_data.csv'
OUTPUT_SHIELD_DATASET = 'shield_data_clean.csv'

RELOAD_DATASET = 'reload_data.csv'
OUTPUT_RELOAD_DATASET = 'reload_data_clean.csv'

GRENADE_DATASET = 'grenade_data.csv'
OUTPUT_GRENADE_DATASET = 'grenade_data_clean.csv'

FULL_DATASET1 = 'dataset1.csv'
FULL_DATASET2 = 'dataset2.csv'

OUTPUT_FULL_DATASET = 'full_data.csv'
OUTPUT_TRAIN_DATASET = 'train_data.csv'
OUTPUT_TEST_DATASET = 'test_data.csv'

# +--------- labels ----------+
# |   None     |      0       |
# |   Shield   |      1       |
# |   Grenade  |      2       |
# |   Reload   |      3       |
# |   Logout   |      4       |
# +---------------------------+

NONE_LABEL = 0
SHIELD_LABEL = 1
GRENADE_LABEL = 2
RELOAD_LABEL = 3
LOGOUT_LABEL = 4

def clean_dataset(dataset):
    for line in dataset:
        split = line.split("->")
        
        #write dataset into new file with correct delinators
        write_file(split[0].strip())
        write_file(',')
        write_file(split[1].strip())
        write_file('\n')

def write_file(line):
    with open(NEW_DATASET_FILE, 'a') as f:
        f.write(line)
        f.close()

# =========================== segment full dataset into action components ========================================
def segment_dataset(dataset):
    idle_dataset = dataset.loc[dataset['Label'] == NONE_LABEL].reset_index()
    shield_dataset = dataset.loc[dataset['Label'] == SHIELD_LABEL].reset_index()
    grenade_dataset = dataset.loc[dataset['Label'] == GRENADE_LABEL].reset_index()
    reload_dataset = dataset.loc[dataset['Label'] == RELOAD_LABEL].reset_index()
    logout_dataset = dataset.loc[dataset['Label'] == LOGOUT_LABEL].reset_index()

    return idle_dataset, shield_dataset, grenade_dataset, reload_dataset, logout_dataset


def graph_data(data, x_axis):
    
    graph, axis = plt.subplots(nrows=6,
           sharex='col')
    axis[0].plot(x_axis, 'Linear-X', data=data, color="#1f77b4")
    axis[1].plot(x_axis, 'Linear-Y', data=data, color="#6DD3CE")
    axis[2].plot(x_axis, 'Linear-Z', data=data, color="#C8E9A0")
    axis[3].plot(x_axis, 'Gyro-X', data=data, color="#F7A278")
    axis[4].plot(x_axis, 'Gyro-Y', data=data, color="#A13D63")
    axis[5].plot(x_axis, 'Gyro-Z', data=data, color="#9BC1BC")

    plt.show()

# calculate roll pitch yaw
def calculate_secondary_features(GyroX, GyroY, GyroZ, accAngleX, accAngleY, elapsedTime):
    gyroAngleX = gyroAngleX + GyroX * elapsedTime;
    gyroAngleY = gyroAngleY + GyroY * elapsedTime;
    yaw =  yaw + GyroZ * elapsedTime;
    # Complementary filter - combine acceleromter and gyro angle values
    roll = 0.96 * gyroAngleX + 0.04 * accAngleX;
    pitch = 0.96 * gyroAngleY + 0.04 * accAngleY;


# clean csv data from internal comms
def fill_nan(dataset):
    acc_x_median = dataset['imuDataLinearAccelX'].median()
    dataset['imuDataLinearAccelX'] = dataset['imuDataLinearAccelX'].replace(np.nan,acc_x_median)

    acc_y_median = dataset['imuDataLinearAccelY'].median()
    dataset['imuDataLinearAccelY'] = dataset['imuDataLinearAccelY'].replace(np.nan, acc_y_median)

    acc_z_median = dataset['imuDataLinearAccelZ'].median()
    dataset['imuDataLinearAccelZ'] = dataset['imuDataLinearAccelZ'].replace(np.nan,acc_z_median)

    gyro_x_median = dataset['imuDataGyroAccelX'].median()
    dataset['imuDataGyroAccelX'] = dataset['imuDataGyroAccelX'].replace(np.nan,gyro_x_median)

    gyro_y_median = dataset['imuDataGyroAccelY'].median()
    dataset['imuDataGyroAccelY'] = dataset['imuDataGyroAccelY'].replace(np.nan,gyro_y_median)

    gyro_z_median = dataset['imuDataGyroAccelXZ'].median()
    dataset['imuDataGyroAccelXZ'] = dataset['imuDataGyroAccelXZ'].replace(np.nan,gyro_z_median)

    roll_median = dataset['roll'].median()
    dataset['roll'] = dataset['roll'].replace(np.nan,roll_median)

    pitch_median = dataset['pitch'].median()
    dataset['pitch'] = dataset['pitch'].replace(np.nan,pitch_median)

    yaw_median = dataset['yaw'].median()
    dataset['yaw'] = dataset['yaw'].replace(np.nan,yaw_median)

    print(dataset)
    return dataset


# code to divide time-based data into action frames, and calculate statistic features
def rmsValue(arr, col):
    square = 0
    mean = 0.0
    root = 0.0
    n = arr.shape[0]
     
    #Calculate square
    for column in arr[col]:
        square += (pow(column,2))
     
    #Calculate Mean
    mean = (square / (float)(n))
     
    #Calculate Root
    root = math.sqrt(mean)
     
    return root

def sliding_window(dataset):
    window = 30

    mydic = {}
    counter = 0

    for end_time in range(43, len(dataset), window):
        start_time = end_time - window

        rolling_sample = dataset[(dataset.index >= start_time) & (dataset.index <= end_time)]

        mydic[counter] = {
            "action": rolling_sample.at[start_time, 'Label'],

            "acc_x_mean":rolling_sample['Linear-X'].mean(),
            "acc_x_std":rolling_sample['Linear-X'].std(),
            "acc_x_rms":rmsValue(rolling_sample, 'Linear-X'),
            "acc_x_min":rolling_sample['Linear-X'].min(),
            "acc_x_max":rolling_sample['Linear-X'].max(),

            "acc_y_mean":rolling_sample['Linear-Y'].mean(),
            "acc_y_std":rolling_sample['Linear-Y'].std(),
            "acc_y_rms":rmsValue(rolling_sample, 'Linear-Y'),
            "acc_y_min":rolling_sample['Linear-Y'].min(),
            "acc_y_max":rolling_sample['Linear-Y'].max(),

            "acc_z_mean":rolling_sample['Linear-Z'].mean(),
            "acc_z_std":rolling_sample['Linear-Z'].std(),
            "acc_z_rms":rmsValue(rolling_sample, 'Linear-Z'),
            "acc_z_min":rolling_sample['Linear-Z'].min(),
            "acc_z_max":rolling_sample['Linear-Z'].max(),

            "gyro_x_mean":rolling_sample['Gyro-X'].mean(),
            "gyro_x_std":rolling_sample['Gyro-X'].std(),
            "gyro_x_rms":rmsValue(rolling_sample, 'Gyro-X'),
            "gyro_x_min":rolling_sample['Gyro-X'].min(),
            "gyro_x_max":rolling_sample['Gyro-X'].max(),

            "gyro_y_mean":rolling_sample['Gyro-Y'].mean(),
            "gyro_y_std":rolling_sample['Gyro-Y'].std(),
            "gyro_y_rms":rmsValue(rolling_sample, 'Gyro-Y'),
            "gyro_y_min":rolling_sample['Gyro-Y'].min(),
            "gyro_y_max":rolling_sample['Gyro-Y'].max(),

            "gyro_z_mean":rolling_sample['Gyro-Z'].mean(),
            "gyro_z_std":rolling_sample['Gyro-Z'].std(),
            "gyro_z_rms":rmsValue(rolling_sample, 'Gyro-Z'),
            "gyro_z_min":rolling_sample['Gyro-Z'].min(),
            "gyro_z_max":rolling_sample['Gyro-Z'].max()
            
        }
        counter = counter + 1

    results = pd.DataFrame.from_dict(mydic).T
    #print(results)
    return results

def join_and_shuffle_dataset(dataset1, dataset2, dataset3, dataset4, dataset5, dataset6, dataset7, dataset8):
    joined_dataset = pd.concat([dataset1, dataset2, dataset3, dataset4, dataset5, dataset6, dataset7, dataset8])
    shuffled_dataset = joined_dataset.sample(frac=1).reset_index()
    return shuffled_dataset


# +--------- labels ----------+
# |   None     |      0       |
# |   Shield   |      1       |
# |   Grenade  |      2       |
# |   Reload   |      3       |
# |   Logout   |      4       |
# +---------------------------+

def convert_label_to_binary(dataset):
    dataset['Label'] = dataset['Label'].replace('Idle', NONE_LABEL)
    dataset['Label'] = dataset['Label'].replace('idle', NONE_LABEL)
    dataset['Label'] = dataset['Label'].replace('shield',SHIELD_LABEL) 
    dataset['Label'] = dataset['Label'].replace('grenade',GRENADE_LABEL)
    dataset['Label'] = dataset['Label'].replace('reload',RELOAD_LABEL) 
    dataset['Label'] = dataset['Label'].replace('exit', LOGOUT_LABEL)
    return dataset

if __name__ == "__main__":
    """
    reload_dataset = pd.read_csv(GRENADE_DATASET, header=0)
    filled_reload_dataset = fill_nan(reload_dataset)
    feature_reload_dataset = sliding_window(filled_reload_dataset)
    feature_reload_dataset.to_csv(OUTPUT_GRENADE_DATASET, index=True)
    
    reload_dataset = pd.read_csv(OUTPUT_RELOAD_DATASET, header=0, index_col=0)
    shield_dataset = pd.read_csv(OUTPUT_SHIELD_DATASET, header=0, index_col=0)
    grenade_dataset = pd.read_csv(OUTPUT_GRENADE_DATASET, header=0, index_col=0)
    joined_dataset = convert_label_to_binary(join_and_shuffle_dataset(shield_dataset, reload_dataset, grenade_dataset))

    print(joined_dataset)
    train_dataset.reset_index().to_csv(OUTPUT_TRAIN_DATASET)
    test_dataset.reset_index().to_csv(OUTPUT_TEST_DATASET)
    """

    # new code to clean and segment data after internal comms fix
    full_dataset1 = pd.read_csv(FULL_DATASET1, header=0)
    labelled_dataset1 = convert_label_to_binary(full_dataset1)
    idle_dataset1, shield_dataset1, grenade_dataset1, reload_dataset1, logout_dataset1 = segment_dataset(labelled_dataset1)
    
    feature_reload_dataset1 = sliding_window(reload_dataset1)
    feature_grenade_dataset1 = sliding_window(grenade_dataset1)
    feature_shield_dataset1 = sliding_window(shield_dataset1)


    full_dataset2 = pd.read_csv(FULL_DATASET2, header=0)
    labelled_dataset2 = convert_label_to_binary(full_dataset2)
    idle_dataset2, shield_dataset2, grenade_dataset2, reload_dataset2, logout_dataset2 = segment_dataset(labelled_dataset2)

    #graph_data(logout_dataset2, logout_dataset2.index)

    feature_reload_dataset2 = sliding_window(reload_dataset2)
    feature_grenade_dataset2 = sliding_window(grenade_dataset2)
    feature_shield_dataset2 = sliding_window(shield_dataset2)
    feature_idle_dataset2 = sliding_window(idle_dataset2)
    feature_logout_dataset2 = sliding_window(logout_dataset2)

    # join individual action datasets and make train test sets
    joined_dataset = join_and_shuffle_dataset(feature_shield_dataset1, feature_reload_dataset1, feature_grenade_dataset1.drop([196]), feature_reload_dataset2, feature_grenade_dataset2, feature_shield_dataset2, feature_idle_dataset2, feature_logout_dataset2).drop(['index'], axis=1)
    joined_dataset = joined_dataset.astype({'action': 'int32'})
    train_dataset, test_dataset = train_test_split(joined_dataset, test_size=0.2, random_state=42)

    print(train_dataset)

    train_dataset.reset_index().to_csv(OUTPUT_TRAIN_DATASET)
    test_dataset.reset_index().to_csv(OUTPUT_TEST_DATASET)
    

    # old code to clean txt datasets
    #dataset = open(DATASET_FILE, 'r')
    #clean_dataset(dataset)