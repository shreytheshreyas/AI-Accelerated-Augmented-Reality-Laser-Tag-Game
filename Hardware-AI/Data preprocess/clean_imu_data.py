import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew

FOLDER_LEFT_DATASETS = 'left_hand_data/'
FOLDER_RIGHT_DATASETS = 'right_hand_data/'

# idle
IDLE_DATASET = FOLDER_RIGHT_DATASETS + 'idle.csv'
IDLE_DATASET2 = FOLDER_RIGHT_DATASETS + 'idle2.csv'

IDLE_DATASET_L1 = FOLDER_LEFT_DATASETS + 'idle_l.csv'

# logout
LOGOUT_DATASET = FOLDER_RIGHT_DATASETS + 'logout.csv'
LOGOUT_DATASET2 = FOLDER_RIGHT_DATASETS + 'logout2.csv'
LOGOUT_DATASET3 = FOLDER_RIGHT_DATASETS + 'logout3.csv'

LOGOUT_DATASET_L1 = FOLDER_LEFT_DATASETS + 'logout_l.csv'
LOGOUT_DATASET_L2 = FOLDER_LEFT_DATASETS + 'logout_l2.csv'
LOGOUT_DATASET_L3 = FOLDER_LEFT_DATASETS + 'logout_l3.csv'
LOGOUT_DATASET_L6 = FOLDER_LEFT_DATASETS + 'logout_l6.csv'

# shield
SHIELD_DATASET1 = FOLDER_RIGHT_DATASETS + 'shield.csv'
SHIELD_DATASET2 = FOLDER_RIGHT_DATASETS + 'shield2.csv'
SHIELD_DATASET3 = FOLDER_RIGHT_DATASETS + 'shield3.csv'
SHIELD_DATASET4 = FOLDER_RIGHT_DATASETS + 'shield4.csv'
SHIELD_DATASET5 = FOLDER_RIGHT_DATASETS + 'shield5.csv'
SHIELD_DATASET6 = FOLDER_RIGHT_DATASETS + 'shield6.csv'

SHIELD_DATASET_L1 = FOLDER_LEFT_DATASETS + 'shield_l.csv'
SHIELD_DATASET_L2 = FOLDER_LEFT_DATASETS + 'shield_l2.csv'
SHIELD_DATASET_L4 = FOLDER_LEFT_DATASETS + 'shield_l4.csv'
SHIELD_DATASET_L5 = FOLDER_LEFT_DATASETS + 'shield_l5.csv'
SHIELD_DATASET_L7= FOLDER_LEFT_DATASETS + 'shield_l7.csv'

OUTPUT_SHIELD_DATASET = 'shield_data_clean.csv'

# reload
RELOAD_DATASET1 = FOLDER_RIGHT_DATASETS + 'reload.csv'
RELOAD_DATASET2 = FOLDER_RIGHT_DATASETS + 'reload2.csv'
RELOAD_DATASET3 = FOLDER_RIGHT_DATASETS + 'reload3.csv'
RELOAD_DATASET4 = FOLDER_RIGHT_DATASETS + 'reload4.csv'
RELOAD_DATASET5 = FOLDER_RIGHT_DATASETS + 'reload5.csv'
RELOAD_DATASET6 = FOLDER_RIGHT_DATASETS + 'reload6.csv'
RELOAD_DATASET8 = FOLDER_RIGHT_DATASETS + 'reload8.csv'

RELOAD_DATASET_L1 = FOLDER_LEFT_DATASETS + 'reload_l.csv'
RELOAD_DATASET_L2 = FOLDER_LEFT_DATASETS + 'reload_l2.csv'
RELOAD_DATASET_L4 = FOLDER_LEFT_DATASETS + 'reload_l4.csv'
RELOAD_DATASET_L6 = FOLDER_LEFT_DATASETS + 'reload_l6.csv'

OUTPUT_RELOAD_DATASET = 'reload_data_clean.csv'

# grenade
GRENADE_DATASET1 = FOLDER_RIGHT_DATASETS + 'grenade.csv'
GRENADE_DATASET2 = FOLDER_RIGHT_DATASETS + 'grenade2.csv'
GRENADE_DATASET3 = FOLDER_RIGHT_DATASETS + 'grenade3.csv'
GRENADE_DATASET4 = FOLDER_RIGHT_DATASETS + 'grenade4.csv'
GRENADE_DATASET5 = FOLDER_RIGHT_DATASETS + 'grenade5.csv'
GRENADE_DATASET6 = FOLDER_RIGHT_DATASETS + 'grenade6.csv'
GRENADE_DATASET7 = FOLDER_RIGHT_DATASETS + 'grenade7.csv'
GRENADE_DATASET8 = FOLDER_RIGHT_DATASETS + 'grenade8.csv'

GRENADE_DATASET_L1 = FOLDER_LEFT_DATASETS + 'grenade_l.csv'
GRENADE_DATASET_L2 = FOLDER_LEFT_DATASETS + 'grenade_l2.csv'
GRENADE_DATASET_L5 = FOLDER_LEFT_DATASETS + 'grenade_l5.csv'
GRENADE_DATASET_L6 = FOLDER_LEFT_DATASETS + 'grenade_l6.csv'
GRENADE_DATASET_L7 = FOLDER_LEFT_DATASETS + 'grenade_l7.csv'
GRENADE_DATASET_L8 = FOLDER_LEFT_DATASETS + 'grenade_l8.csv'

OUTPUT_GRENADE_DATASET = 'grenade_data_clean.csv'

# full data (OLD)
FULL_DATASET1 = 'dataset1.csv'
FULL_DATASET2 = 'dataset2.csv'

OUTPUT_FULL_DATASET_RIGHT = 'full_data_right.csv'
OUTPUT_FULL_DATASET_LEFT = 'full_data_left.csv'
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

# code to divide time-based data into action frames, and calculate statistic features
def rmsValue(arr, col):
    square = 0
    mean = 0.0
    root = 0.0
    n = arr.shape[0]
     
    #Calculate square
    for column_value in arr[col]:
        square += (pow(column_value,2))
     
    #Calculate Mean
    mean = (square / (float)(n))
     
    #Calculate Root
    root = math.sqrt(mean)
     
    return root

# old code
def sliding_window(dataset):
    window = 30

    start_time_arr = [*range(0, len(dataset), window)]

    action_features = {}
    counter = 0

    for start_time in start_time_arr:
        end_time = start_time + window

        rolling_sample = dataset[(dataset.index >= start_time) & (dataset.index <= end_time)]
        #graph_data(rolling_sample, rolling_sample.index)

        rolling_sample_fft = np.fft.fft(rolling_sample.iloc[:, 1:7].values, axis=0)

        action_features[counter] = {
            "action": rolling_sample.at[start_time, 'Label'],

            "acc_x_mean":rolling_sample['Linear-X'].mean(),
            "acc_x_std":rolling_sample['Linear-X'].std(),
            "acc_x_rms":rmsValue(rolling_sample, 'Linear-X'),
            "acc_x_kurt":kurtosis(rolling_sample['Linear-X']),
            "acc_x_skew":skew(rolling_sample['Linear-X']),
            "acc_x_iqr":np.percentile(rolling_sample['Linear-X'], 75) - np.percentile(rolling_sample['Linear-X'], 25),
            "acc_x_mad":np.median(np.absolute(rolling_sample['Linear-X'] - np.median(rolling_sample['Linear-X']))),
            "acc_x_fmean":rolling_sample_fft[:, 0].mean().real,
            "acc_x_frange":(rolling_sample_fft[:,0].max() - rolling_sample_fft[:,0].min()).real,
            "acc_x_fskew":skew(rolling_sample_fft[:,0]).real,

            "acc_y_mean":rolling_sample['Linear-Y'].mean(),
            "acc_y_std":rolling_sample['Linear-Y'].std(),
            "acc_y_rms":rmsValue(rolling_sample, 'Linear-Y'),
            "acc_y_kurt":kurtosis(rolling_sample['Linear-Y']),
            "acc_y_skew":skew(rolling_sample['Linear-Y']),
            "acc_y_iqr":np.percentile(rolling_sample['Linear-Y'], 75) - np.percentile(rolling_sample['Linear-Y'], 25),
            "acc_y_mad":np.median(np.absolute(rolling_sample['Linear-Y'] - np.median(rolling_sample['Linear-Y']))),
            "acc_y_fmean":rolling_sample_fft[:, 1].mean().real,
            "acc_y_frange":(rolling_sample_fft[:,1].max() - rolling_sample_fft[:,1].min()).real,
            "acc_y_fskew":skew(rolling_sample_fft[:,1]).real,

            "acc_z_mean":rolling_sample['Linear-Z'].mean(),
            "acc_z_std":rolling_sample['Linear-Z'].std(),
            "acc_z_rms":rmsValue(rolling_sample, 'Linear-Z'),
            "acc_z_kurt":kurtosis(rolling_sample['Linear-Z']),
            "acc_z_skew":skew(rolling_sample['Linear-Z']),
            "acc_z_iqr":np.percentile(rolling_sample['Linear-Z'], 75) - np.percentile(rolling_sample['Linear-Z'], 25),
            "acc_z_mad":np.median(np.absolute(rolling_sample['Linear-Z'] - np.median(rolling_sample['Linear-Z']))),
            "acc_z_fmean":rolling_sample_fft[:,2].mean().real,
            "acc_z_frange":(rolling_sample_fft[:,2].max() - rolling_sample_fft[:,2].min()).real,
            "acc_z_fskew":skew(rolling_sample_fft[:,2]).real,

            "gyro_x_mean":rolling_sample['Gyro-X'].mean(),
            "gyro_x_std":rolling_sample['Gyro-X'].std(),
            "gyro_x_rms":rmsValue(rolling_sample, 'Gyro-X'),
            "gyro_x_kurt":kurtosis(rolling_sample['Gyro-X']),
            "gyro_x_skew":skew(rolling_sample['Gyro-X']),
            "gyro_x_iqr":np.percentile(rolling_sample['Gyro-X'], 75) - np.percentile(rolling_sample['Gyro-X'], 25),
            "gyro_x_mad":np.median(np.absolute(rolling_sample['Gyro-X'] - np.median(rolling_sample['Gyro-X']))),
            "gyro_x_fmean":rolling_sample_fft[:,3].mean().real,
            "gyro_x_frange":(rolling_sample_fft[:,3].max() - rolling_sample_fft[:,3].min()).real,
            "gyro_x_fskew":skew(rolling_sample_fft[:,3]).real,

            "gyro_y_mean":rolling_sample['Gyro-Y'].mean(),
            "gyro_y_std":rolling_sample['Gyro-Y'].std(),
            "gyro_y_rms":rmsValue(rolling_sample, 'Gyro-Y'),
            "gyro_y_kurt":kurtosis(rolling_sample['Gyro-Y']),
            "gyro_y_skew":skew(rolling_sample['Gyro-Y']),
            "gyro_y_iqr":np.percentile(rolling_sample['Gyro-Y'], 75) - np.percentile(rolling_sample['Gyro-Y'], 25),
            "gyro_y_mad":np.median(np.absolute(rolling_sample['Gyro-Y'] - np.median(rolling_sample['Gyro-Y']))),
            "gyro_y_fmean":rolling_sample_fft[:,4].mean().real,
            "gyro_y_frange":(rolling_sample_fft[:,4].max() - rolling_sample_fft[:,4].min()).real,
            "gyro_y_fskew":skew(rolling_sample_fft[:,4]).real,

            "gyro_z_mean":rolling_sample['Gyro-Z'].mean(),
            "gyro_z_std":rolling_sample['Gyro-Z'].std(),
            "gyro_z_rms":rmsValue(rolling_sample, 'Gyro-Z'),
            "gyro_z_kurt":kurtosis(rolling_sample['Gyro-Z']),
            "gyro_z_skew":skew(rolling_sample['Gyro-Z']),
            "gyro_z_iqr":np.percentile(rolling_sample['Gyro-Z'], 75) - np.percentile(rolling_sample['Gyro-Z'], 25),
            "gyro_z_mad":np.median(np.absolute(rolling_sample['Gyro-Z'] - np.median(rolling_sample['Gyro-Z']))),
            "gyro_z_fmean":rolling_sample_fft[:,5].mean().real,
            "gyro_z_frange":(rolling_sample_fft[:,5].max() - rolling_sample_fft[:,5].min()).real,
            "gyro_z_fskew":skew(rolling_sample_fft[:,5]).real
            
        }
        counter = counter + 1

    results = pd.DataFrame.from_dict(action_features).T
    #print(results)
    return results

# =============================================== start of move algo ======================================================
WINDOW_SIZE = 8
NUMBER_OF_SENSOR_FEATURES= 6
THRESHOLD = 0.12
PREDICTION_WINDOW_SIZE = 30
NUMBER_OF_FEATURES = 60

def replace_nan(arr):
    for idx, val in enumerate(arr[WINDOW_SIZE-1]):
        if np.isnan(val):
            arr[WINDOW_SIZE-1, idx] = np.nan_to_num(arr[WINDOW_SIZE-1, idx], np.median(arr[0:WINDOW_SIZE-2, idx]))
    return arr

def start_of_move_sliding(raw_data):
    window_data = np.empty((0,NUMBER_OF_SENSOR_FEATURES))
    action_feature_data = np.empty((0, NUMBER_OF_FEATURES))

    # variables to be used when start of move is identified
    start_of_move_flag = 0
    action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES))

    # to graph out energy
    energy_arr = []
    time_arr = []

    for time, data in enumerate(raw_data.to_numpy()):
        data = np.reshape(data, (1,NUMBER_OF_SENSOR_FEATURES))

        if start_of_move_flag == 0:
            
            # replace any NaNs at the start of data stream with 0
            if len(window_data) < WINDOW_SIZE:
                if np.isnan(data).any():
                    data = np.nan_to_num(data)
            

            prev_window_data = window_data
            window_data = np.append(window_data, data, axis=0)

            if len(window_data) > WINDOW_SIZE:
                window_data = np.delete(window_data, 0, axis=0)

                # replace any NaNs with the median of the previous datapoints
                if np.isnan(data).any():
                    window_data = replace_nan(window_data)
            
                # calculate energy of window and prev window
                rms_acc_curr_window = 0
                rms_acc_prev_window = 0
                for idx, row in enumerate(window_data):
                    rms_acc_curr_window = rms_acc_curr_window + rmsValue_np(window_data.T[0:3], idx)
                    rms_acc_prev_window = rms_acc_prev_window + rmsValue_np(prev_window_data.T[0:3], idx)
                    
                energy_curr_window = rms_acc_curr_window / WINDOW_SIZE
                energy_prev_window = rms_acc_prev_window / len(prev_window_data)

                #print("time: ", time, "energy curr: ", energy_curr_window)

                # to graph out energy
                energy_arr.append(energy_curr_window)
                time_arr.append(time)

                if energy_curr_window - energy_prev_window > THRESHOLD:
                    #print("start of move at: ", time)
                    action_arr = np.append(action_arr, window_data, axis=0)
                    start_of_move_flag = 1
        else: 
            action_arr = np.append(action_arr, data, axis=0)
            if len(action_arr) == PREDICTION_WINDOW_SIZE:
                action_features = segment_move(action_arr)
                action_feature_data = np.append(action_feature_data, np.reshape(action_features, (1,NUMBER_OF_FEATURES)), axis=0)

                # reset flags and action window
                start_of_move_flag = 0
                action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES))

    return action_feature_data

        
def segment_move(window):
    # find statistical features of window and feed it to model

    window_fft = np.fft.fft(window, axis=0)

    action = {
        "acc_x_mean":window[:, 0].mean(),
        "acc_x_std":window[:, 0].std(),
        "acc_x_rms":rmsValue_np(window, 0),
        "acc_x_kurt":kurtosis(window[:, 0]),
        "acc_x_skew":skew(window[:, 0]),
        "acc_x_iqr":np.percentile(window[:, 0], 75) - np.percentile(window[:, 0], 25),
        "acc_x_mad":np.median(np.absolute(window[:,0] - np.median(window[:,0]))),
        "acc_x_fmean":window_fft[:, 0].mean().real,
        "acc_x_frange":(window_fft[:, 0].max() - window_fft[:,0].min()).real,
        "acc_x_fskew":skew(window_fft[:, 0]).real,

        "acc_y_mean":window[:, 1].mean(),
        "acc_y_std":window[:, 1].std(),
        "acc_y_rms":rmsValue_np(window, 1),
        "acc_y_kurt":kurtosis(window[:, 1]),
        "acc_y_skew":skew(window[:, 1]),
        "acc_y_iqr":np.percentile(window[:, 1], 75) - np.percentile(window[:, 1], 25),
        "acc_y_mad":np.median(np.absolute(window[:,1] - np.median(window[:,1]))),
        "acc_y_fmean":window_fft[:, 1].mean().real,
        "acc_y_frange":(window_fft[:, 1].max() - window_fft[:,1].min()).real,
        "acc_y_fskew":skew(window_fft[:, 1]).real,

        "acc_z_mean":window[:, 2].mean(),
        "acc_z_std":window[:, 2].std(),
        "acc_z_rms":rmsValue_np(window, 2),
        "acc_z_kurt":kurtosis(window[:, 2]),
        "acc_z_skew":skew(window[:, 2]),
        "acc_z_iqr":np.percentile(window[:, 2], 75) - np.percentile(window[:, 2], 25),
        "acc_z_mad":np.median(np.absolute(window[:,2] - np.median(window[:,2]))),
        "acc_z_fmean":window_fft[:, 2].mean().real,
        "acc_z_frange":(window_fft[:, 2].max() - window_fft[:,2].min()).real,
        "acc_z_fskew":skew(window_fft[:, 2]).real,

        "gyro_x_mean":window[:, 3].mean(),
        "gyro_x_std":window[:, 3].std(),
        "gyro_x_rms":rmsValue_np(window, 3),
        "gyro_x_kurt":kurtosis(window[:, 3]),
        "gyro_x_skew":skew(window[:, 3]),
        "gyro_x_iqr":np.percentile(window[:, 3], 75) - np.percentile(window[:, 3], 25),
        "gyro_x_mad":np.median(np.absolute(window[:,3] - np.median(window[:,3]))),
        "gyro_x_fmean":window_fft[:, 3].mean().real,
        "gyro_x_frange":(window_fft[:, 3].max() - window_fft[:,3].min()).real,
        "gyro_x_fskew":skew(window_fft[:, 3]).real,

        "gyro_y_mean":window[:, 4].mean(),
        "gyro_y_std":window[:, 4].std(),
        "gyro_y_rms":rmsValue_np(window, 4),
        "gyro_y_kurt":kurtosis(window[:, 4]),
        "gyro_y_skew":skew(window[:, 4]),
        "gyro_y_iqr":np.percentile(window[:, 4], 75) - np.percentile(window[:, 4], 25),
        "gyro_y_mad":np.median(np.absolute(window[:,4] - np.median(window[:,4]))),
        "gyro_y_fmean":window_fft[:, 4].mean().real,
        "gyro_y_frange":(window_fft[:, 4].max() - window_fft[:,4].min()).real,
        "gyro_y_fskew":skew(window_fft[:, 4]).real,

        "gyro_z_mean":window[:, 5].mean(),
        "gyro_z_std":window[:, 5].std(),
        "gyro_z_rms":rmsValue_np(window, 5),
        "gyro_z_kurt":kurtosis(window[:, 5]),
        "gyro_z_skew":skew(window[:, 5]),
        "gyro_z_iqr":np.percentile(window[:, 5], 75) - np.percentile(window[:, 5], 25),
        "gyro_z_mad":np.median(np.absolute(window[:,5] - np.median(window[:,5]))),
        "gyro_z_fmean":window_fft[:, 5].mean().real,
        "gyro_z_frange":(window_fft[:, 5].max() - window_fft[:,5].min()).real,
        "gyro_z_fskew":skew(window_fft[:, 5]).real

        }

    action_features = list(action.values())
    return np.array(action_features)

def rmsValue_np(arr, col):
    square = 0
    mean = 0.0
    root = 0.0
    n = arr.shape[0]
     
    #Calculate square
    for column_value in arr[:,col]:
        square += (pow(column_value,2))
     
    #Calculate Mean
    mean = (square / (float)(n))
     
    #Calculate Root
    root = math.sqrt(mean)
     
    return root


def join_and_shuffle_dataset(dataset1, dataset2, dataset3, dataset4, dataset5):
    joined_dataset = pd.concat([dataset1, dataset2, dataset3, dataset4, dataset5])
    shuffled_dataset = joined_dataset.sample(frac=1).reset_index(drop=True)
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


def graph_action_stats(line1_x, line1_y, line2_x, line2_y):
    plt.plot(line1_x, line1_y, label = "1")
    plt.plot(line2_x, line2_y, label = "2")
    plt.show()



# ===================== main clean methods ====================
def clean_right_glove_data():
    idle_dataset = pd.read_csv(IDLE_DATASET, header=0)
    idle_dataset2 = pd.read_csv(IDLE_DATASET2, header=0)

    # read all datasets
    shield_dataset1 = pd.read_csv(SHIELD_DATASET1, header=0)
    grenade_dataset1 = pd.read_csv(GRENADE_DATASET1, header=0)
    reload_dataset1 = pd.read_csv(RELOAD_DATASET1, header=0)
    logout_dataset = pd.read_csv(LOGOUT_DATASET, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset2 = pd.read_csv(SHIELD_DATASET2, header=0)
    grenade_dataset2 = pd.read_csv(GRENADE_DATASET2, header=0)
    reload_dataset2 = pd.read_csv(RELOAD_DATASET2, header=0)
    logout_dataset2 = pd.read_csv(LOGOUT_DATASET2, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset3 = pd.read_csv(SHIELD_DATASET3, header=0)
    grenade_dataset3 = pd.read_csv(GRENADE_DATASET3, header=0)
    reload_dataset3 = pd.read_csv(RELOAD_DATASET3, header=0)
    logout_dataset3 = pd.read_csv(LOGOUT_DATASET3, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset4 = pd.read_csv(SHIELD_DATASET4, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset4 = pd.read_csv(GRENADE_DATASET4, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset4 = pd.read_csv(RELOAD_DATASET4, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset5 = pd.read_csv(SHIELD_DATASET5, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset5 = pd.read_csv(GRENADE_DATASET5, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset5 = pd.read_csv(RELOAD_DATASET5, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset6 = pd.read_csv(SHIELD_DATASET6, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset6 = pd.read_csv(GRENADE_DATASET6, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset6 = pd.read_csv(RELOAD_DATASET6, header=0).drop(['Timestamp', 'Label'], axis=1)

    grenade_dataset7 = pd.read_csv(GRENADE_DATASET7, header=0).drop(['Timestamp', 'Label'], axis=1)

    grenade_dataset8 = pd.read_csv(GRENADE_DATASET8, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset8 = pd.read_csv(RELOAD_DATASET8, header=0).drop(['Timestamp', 'Label'], axis=1)

    # join them
    joined_idle_dataset = pd.concat([idle_dataset, idle_dataset2]).reset_index(drop=True)
    joined_shield_dataset = pd.concat([shield_dataset1, shield_dataset2, shield_dataset3]).reset_index().drop(['index', 'Timestamp', 'Label'], axis=1)
    joined_grenade_dataset  = pd.concat([grenade_dataset1, grenade_dataset2, grenade_dataset3]).reset_index().drop(['index', 'Timestamp', 'Label'], axis=1)
    joined_reload_dataset = pd.concat([reload_dataset1, reload_dataset2, reload_dataset3]).reset_index().drop(['index', 'Timestamp', 'Label'], axis=1)

    #graph_data(joined_shield_dataset, joined_shield_dataset.index)
    
    labelled_idle = convert_label_to_binary(joined_idle_dataset)

    feature_idle_dataset = sliding_window(labelled_idle).apply(lambda x: pd.to_numeric(x))
    feature_shield_dataset = start_of_move_sliding(joined_shield_dataset)
    feature_grenade_dataset = start_of_move_sliding(joined_grenade_dataset)
    feature_reload_dataset = start_of_move_sliding(joined_reload_dataset)
    feature_logout_dataset = np.delete(start_of_move_sliding(logout_dataset), [0, 2, 3, 4], axis=0) # drop 0, 2, 3, 4 move

    feature_shield_dataset2 = np.delete(start_of_move_sliding(shield_dataset4), [0, 1, 7, 8, 9, 10, 11], axis=0) # drop 0, 1, 7, 8, 9, 10, 11 move
    feature_grenade_dataset2 = np.delete(start_of_move_sliding(grenade_dataset4), [0, 1, 3, 32, 33], axis=0) # drop 0, 1, 3, 32, 33 move
    feature_reload_dataset2 = np.delete(start_of_move_sliding(reload_dataset4), [0, 1, 2, 3, 5], axis=0) # drop 0, 1, 2, 3, 5 move
    feature_logout_dataset2 = start_of_move_sliding(logout_dataset2)

    feature_shield_dataset3 = np.delete(start_of_move_sliding(shield_dataset5), [0,2,4], axis=0) # drop 0, 2, 4 move
    feature_grenade_dataset3 = np.delete(start_of_move_sliding(grenade_dataset5), 0, axis=0) # drop 0 move
    feature_reload_dataset3 = start_of_move_sliding(reload_dataset5) # drop 2, last move
    feature_reload_dataset3 = np.delete(feature_reload_dataset3, [2, len(feature_reload_dataset3)-1], axis=0)
    feature_logout_dataset3 = start_of_move_sliding(logout_dataset3) # drop 0, 6, last
    feature_logout_dataset3 = np.delete(feature_logout_dataset3, [0, 6, len(feature_logout_dataset3)-1], axis=0)

    feature_shield_dataset6 = start_of_move_sliding(shield_dataset6)
    feature_reload_dataset6 = np.delete(start_of_move_sliding(reload_dataset6), [1,3], axis=0) # drop 1, 3 move
    feature_grenade_dataset6 = np.delete(start_of_move_sliding(grenade_dataset6), [20, 40, 42, 43, 45, 48, 51, 53,54, 55, 56,57, 60, 61, 62, 64], axis=0) # drop 20, 40, 42, 43, 45, 48, 51, 53,54, 55, 56,57, 60, 61, 62, 65

    feature_grenade_dataset7 = np.delete(start_of_move_sliding(grenade_dataset7), [1,3,13,24,26,28,40,50,57,65,72,74], axis=0) # drop 1,3,13,24,26,28,40,50,57,65,72,74

    feature_grenade_dataset8 = start_of_move_sliding(grenade_dataset8)
    feature_grenade_dataset8 = np.delete(feature_grenade_dataset8, [len(feature_grenade_dataset8)-1, len(feature_grenade_dataset8)-4, len(feature_grenade_dataset8)-6, len(feature_grenade_dataset8)-7], axis=0)
    feature_reload_dataset8 = start_of_move_sliding(reload_dataset8)
    feature_reload_dataset8 = np.delete(feature_reload_dataset8, [0, len(feature_reload_dataset8)-1], axis=0)

    # join old action feature data with new action feature data extracted from movedetection_train code
    feature_shield_dataset = np.concatenate((feature_shield_dataset, feature_shield_dataset2, feature_shield_dataset3, feature_shield_dataset6), axis=0)
    feature_grenade_dataset = np.concatenate((feature_grenade_dataset, feature_grenade_dataset2, feature_grenade_dataset3, feature_grenade_dataset6, feature_grenade_dataset7, feature_grenade_dataset8), axis=0)
    feature_reload_dataset = np.concatenate((feature_reload_dataset, feature_reload_dataset2, feature_reload_dataset3, feature_reload_dataset6, feature_reload_dataset8), axis=0)
    feature_logout_dataset = np.concatenate((feature_logout_dataset, feature_logout_dataset2, feature_logout_dataset3), axis=0)

    # graph stats features to see if theres big diff between 2 moves
    #graph_action_stats(np.arange(len(feature_shield_dataset)), feature_shield_dataset[:,3], np.arange(len(feature_grenade_dataset)), feature_grenade_dataset[:,3])

    # add label column
    feature_shield_dataset = np.hstack((np.full((len(feature_shield_dataset), 1), SHIELD_LABEL, dtype=int), feature_shield_dataset))
    feature_grenade_dataset = np.hstack((np.full((len(feature_grenade_dataset), 1), GRENADE_LABEL, dtype=int), feature_grenade_dataset))
    feature_reload_dataset = np.hstack((np.full((len(feature_reload_dataset), 1), RELOAD_LABEL, dtype=int), feature_reload_dataset))
    feature_logout_dataset = np.hstack((np.full((len(feature_logout_dataset), 1), LOGOUT_LABEL, dtype=int), feature_logout_dataset))

    
    column_values = ['action', 'acc_x_mean', 'acc_x_std', 'acc_x_rms', 'acc_x_kurt', 'acc_x_skew', 'acc_x_iqr', 'acc_x_mad', 'acc_x_fmean', 'acc_x_frange', 'acc_x_fskew' ,
                     'acc_y_mean', 'acc_y_std', 'acc_y_rms', 'acc_y_kurt', 'acc_y_skew', 'acc_y_iqr', 'acc_y_mad', 'acc_y_fmean', 'acc_y_frange', 'acc_y_fskew',
                     'acc_z_mean', 'acc_z_std', 'acc_z_rms', 'acc_z_kurt', 'acc_z_skew', 'acc_z_iqr', 'acc_z_mad', 'acc_z_fmean', 'acc_z_frange', 'acc_z_fskew',
                     'gyro_x_mean', 'gyro_x_std', 'gyro_x_rms', 'gyro_x_kurt', 'gyro_x_skew', 'gyro_x_iqr', 'gyro_x_mad', 'gyro_x_fmean', 'gyro_x_frange', 'gyro_x_fskew',
                     'gyro_y_mean', 'gyro_y_std', 'gyro_y_rms', 'gyro_y_kurt', 'gyro_y_skew', 'gyro_y_iqr', 'gyro_y_mad',  'gyro_y_fmean', 'gyro_y_frange', 'gyro_y_fskew',
                     'gyro_z_mean', 'gyro_z_std', 'gyro_z_rms', 'gyro_z_kurt', 'gyro_z_skew', 'gyro_z_iqr', 'gyro_z_mad', 'gyro_z_fmean', 'gyro_z_frange', 'gyro_z_fskew']

    pd_shield = pd.DataFrame(data=feature_shield_dataset, columns=column_values)
    pd_grenade = pd.DataFrame(data=feature_grenade_dataset, columns=column_values)
    pd_reload = pd.DataFrame(data=feature_reload_dataset, columns=column_values)
    pd_logout = pd.DataFrame(data=feature_logout_dataset, columns=column_values)

    print("no. of idle datapoints: ", len(feature_idle_dataset), "\nno. of shield datapoints: ", len(pd_shield), "\nno. of grenade datapoints: ", len(pd_grenade), "\nno. of reload datapoints: ", len(pd_reload), "\nno. of logout datapoints: ", len(pd_logout))

    joined_dataset = join_and_shuffle_dataset(pd_shield, pd_grenade, pd_reload, feature_idle_dataset, pd_logout)
    joined_dataset = joined_dataset.astype({'action': 'int32'})

    print(joined_dataset)
    joined_dataset.to_csv(OUTPUT_FULL_DATASET_RIGHT)

def clean_left_glove_data():
    idle_dataset_l = pd.read_csv(IDLE_DATASET_L1, header=0)

    # label idle dataset correctly and extract features
    labelled_idle_l = convert_label_to_binary(idle_dataset_l)
    feature_idle_dataset_l1 = sliding_window(labelled_idle_l).apply(lambda x: pd.to_numeric(x))

    shield_dataset_l1 = pd.read_csv(SHIELD_DATASET_L1, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset_l1 = pd.read_csv(GRENADE_DATASET_L1, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset_l1 = pd.read_csv(RELOAD_DATASET_L1, header=0).drop(['Timestamp', 'Label'], axis=1)
    logout_dataset_l1 = pd.read_csv(LOGOUT_DATASET_L1, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset_l2 = pd.read_csv(SHIELD_DATASET_L2, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset_l2 = pd.read_csv(GRENADE_DATASET_L2, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset_l2 = pd.read_csv(RELOAD_DATASET_L2, header=0).drop(['Timestamp', 'Label'], axis=1)
    logout_dataset_l2 = pd.read_csv(LOGOUT_DATASET_L2, header=0).drop(['Timestamp', 'Label'], axis=1)

    logout_dataset_l3 = pd.read_csv(LOGOUT_DATASET_L3, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset_l4 = pd.read_csv(SHIELD_DATASET_L4, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset_l4 = pd.read_csv(RELOAD_DATASET_L4, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset_l5 = pd.read_csv(SHIELD_DATASET_L5, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset_l5 = pd.read_csv(GRENADE_DATASET_L5, header=0).drop(['Timestamp', 'Label'], axis=1)

    grenade_dataset_l6 = pd.read_csv(GRENADE_DATASET_L6, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset_l6 =pd.read_csv(RELOAD_DATASET_L6, header=0).drop(['Timestamp', 'Label'], axis=1)

    grenade_dataset_l7 = pd.read_csv(GRENADE_DATASET_L7, header=0).drop(['Timestamp', 'Label'], axis=1)

    shield_dataset_l7 = pd.read_csv(SHIELD_DATASET_L7, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset_l8 = pd.read_csv(GRENADE_DATASET_L8, header=0).drop(['Timestamp', 'Label'], axis=1)
    logout_dataset_l6 = pd.read_csv(LOGOUT_DATASET_L6, header=0).drop(['Timestamp', 'Label'], axis=1)

    # feature extraction of first dataset
    feature_shield_dataset_l = np.delete(start_of_move_sliding(shield_dataset_l1), 52, axis=0) # drop 52 move
    feature_grenade_dataset_l =  np.delete(start_of_move_sliding(grenade_dataset_l1), [0, 5], axis=0) # drop 1 and 5 move
    feature_reload_dataset_l = start_of_move_sliding(reload_dataset_l1)
    feature_logout_dataset_l = np.delete(start_of_move_sliding(logout_dataset_l1), [1,9,11,13,68,69], axis=0) # drop 1, 9, 11, 13, 68, 69 move
    
    # feature extraction of second dataset
    feature_shield_dataset_l2 = start_of_move_sliding(shield_dataset_l2) # drop 0, 3, 4, 5, last move
    feature_grenade_dataset_l2 = start_of_move_sliding(grenade_dataset_l2) # drop 0, 17, last, last-1, last-2, last-3, last-4
    feature_reload_dataset_l2 = np.delete(start_of_move_sliding(reload_dataset_l2), [0, 2], axis=0) # drop 0, 2 move
    feature_shield_dataset_l2 = np.delete(feature_shield_dataset_l2, [0, 3, 4, 5, len(feature_shield_dataset_l2)-1], axis=0) # drop 0, 3, 4, 5, last move
    feature_grenade_dataset_l2 = np.delete(feature_grenade_dataset_l2, [0, 17, len(feature_grenade_dataset_l2)-1, len(feature_grenade_dataset_l2)-2, len(feature_grenade_dataset_l2)-3, len(feature_grenade_dataset_l2)-4, len(feature_grenade_dataset_l2)-5], axis=0) # drop 0, 17, last, last-1, last-2, last-3, last-4

    # feature extraction of third dataset
    feature_shield_dataset_l4 = start_of_move_sliding(shield_dataset_l4)
    feature_reload_dataset_l4 = start_of_move_sliding(reload_dataset_l4)
    feature_logout_dataset_l2 = np.delete(start_of_move_sliding(logout_dataset_l2), 0, axis=0) # drop 0 move
    feature_logout_dataset_l2 = np.delete(feature_logout_dataset_l2, len(feature_logout_dataset_l2)-1, axis=0) # drop last move

    # feature extraction of forth dataset
    feature_shield_dataset_l5 = start_of_move_sliding(shield_dataset_l5)
    feature_grenade_dataset_l5 = start_of_move_sliding(grenade_dataset_l5) #drop last-1, last-5, last-6
    feature_grenade_dataset_l5 = np.delete(feature_grenade_dataset_l5, [len(feature_grenade_dataset_l5)-2, len(feature_grenade_dataset_l5)-6, len(feature_grenade_dataset_l5)-7], axis=0)
    feature_logout_dataset_l3 = start_of_move_sliding(logout_dataset_l3)
   
    # feature extraction of fifth dataset
    feature_grenade_dataset_l6 = start_of_move_sliding(grenade_dataset_l6) # drop last-7, last-8, last-12
    feature_grenade_dataset_l6 = np.delete(feature_grenade_dataset_l6, [len(feature_grenade_dataset_l6)-8, len(feature_grenade_dataset_l6)-9, len(feature_grenade_dataset_l6)-13], axis=0)
    feature_reload_dataset_l6 = start_of_move_sliding(reload_dataset_l6)

    # feature extraction 6
    feature_grenade_dataset_l7 = start_of_move_sliding(grenade_dataset_l7) # drop 3, 5, last, last-2, last-5, last-6, last-13, last-19, last-31, last-33, last-36, last-41
    feature_grenade_dataset_l7 = np.delete(feature_grenade_dataset_l7, [3, 5, len(feature_grenade_dataset_l7)-1, len(feature_grenade_dataset_l7)-3, len(feature_grenade_dataset_l7)-14, len(feature_grenade_dataset_l7)-20, len(feature_grenade_dataset_l7)-32, len(feature_grenade_dataset_l7)-34, len(feature_grenade_dataset_l7)-37, len(feature_grenade_dataset_l7)-42], axis=0)

    # feature extraction 7
    feature_shield_dataset_l7 = start_of_move_sliding(shield_dataset_l7)
    feature_shield_dataset_l7 = np.delete(feature_shield_dataset_l7, 0, axis=0)
    feature_grenade_dataset_l8 = start_of_move_sliding(grenade_dataset_l8) 
    feature_grenade_dataset_l8 = np.delete(feature_grenade_dataset_l8, [0,5,9,13,15,19,25,27,36,45,48,50,56,59,62,66,69,71,74,77,79,81,84,86,90,92,97,99,101], axis=0)
    feature_logout_dataset_l6 = start_of_move_sliding(logout_dataset_l6)
    feature_logout_dataset_l6 = np.delete(feature_logout_dataset_l6, [9,35,40,45,61], axis=0)

    # combine action features from both datasets
    feature_shield_dataset_l = np.concatenate((feature_shield_dataset_l, feature_shield_dataset_l2, feature_shield_dataset_l4, feature_shield_dataset_l5, feature_shield_dataset_l7), axis=0)
    feature_grenade_dataset_l = np.concatenate((feature_grenade_dataset_l, feature_grenade_dataset_l2, feature_grenade_dataset_l5, feature_grenade_dataset_l6, feature_grenade_dataset_l7,feature_grenade_dataset_l8), axis=0)
    feature_reload_dataset_l = np.concatenate((feature_reload_dataset_l, feature_reload_dataset_l2, feature_reload_dataset_l4, feature_reload_dataset_l6), axis=0)
    feature_logout_dataset_l = np.concatenate((feature_logout_dataset_l, feature_logout_dataset_l2, feature_logout_dataset_l3, feature_logout_dataset_l6), axis=0)

    # add label column
    feature_shield_dataset_l = np.hstack((np.full((len(feature_shield_dataset_l), 1), SHIELD_LABEL, dtype=int), feature_shield_dataset_l))
    feature_grenade_dataset_l = np.hstack((np.full((len(feature_grenade_dataset_l), 1), GRENADE_LABEL, dtype=int), feature_grenade_dataset_l))
    feature_reload_dataset_l = np.hstack((np.full((len(feature_reload_dataset_l), 1), RELOAD_LABEL, dtype=int), feature_reload_dataset_l))
    feature_logout_dataset_l = np.hstack((np.full((len(feature_logout_dataset_l), 1), LOGOUT_LABEL, dtype=int), feature_logout_dataset_l))

    column_values = ['action', 'acc_x_mean', 'acc_x_std', 'acc_x_rms', 'acc_x_kurt', 'acc_x_skew', 'acc_x_iqr', 'acc_x_mad', 'acc_x_fmean', 'acc_x_frange', 'acc_x_fskew' ,
                     'acc_y_mean', 'acc_y_std', 'acc_y_rms', 'acc_y_kurt', 'acc_y_skew', 'acc_y_iqr', 'acc_y_mad', 'acc_y_fmean', 'acc_y_frange', 'acc_y_fskew',
                     'acc_z_mean', 'acc_z_std', 'acc_z_rms', 'acc_z_kurt', 'acc_z_skew', 'acc_z_iqr', 'acc_z_mad', 'acc_z_fmean', 'acc_z_frange', 'acc_z_fskew',
                     'gyro_x_mean', 'gyro_x_std', 'gyro_x_rms', 'gyro_x_kurt', 'gyro_x_skew', 'gyro_x_iqr', 'gyro_x_mad', 'gyro_x_fmean', 'gyro_x_frange', 'gyro_x_fskew',
                     'gyro_y_mean', 'gyro_y_std', 'gyro_y_rms', 'gyro_y_kurt', 'gyro_y_skew', 'gyro_y_iqr', 'gyro_y_mad',  'gyro_y_fmean', 'gyro_y_frange', 'gyro_y_fskew',
                     'gyro_z_mean', 'gyro_z_std', 'gyro_z_rms', 'gyro_z_kurt', 'gyro_z_skew', 'gyro_z_iqr', 'gyro_z_mad', 'gyro_z_fmean', 'gyro_z_frange', 'gyro_z_fskew']

    pd_shield = pd.DataFrame(data=feature_shield_dataset_l, columns=column_values)
    pd_grenade = pd.DataFrame(data=feature_grenade_dataset_l, columns=column_values)
    pd_reload = pd.DataFrame(data=feature_reload_dataset_l, columns=column_values)
    pd_logout = pd.DataFrame(data=feature_logout_dataset_l, columns=column_values)

    print("no. of idle datapoints: ", len(feature_idle_dataset_l1), "\nno. of shield datapoints: ", len(pd_shield), "\nno. of grenade datapoints: ", len(pd_grenade), "\nno. of reload datapoints: ", len(pd_reload), "\nno. of logout datapoints: ", len(pd_logout))

    joined_dataset = join_and_shuffle_dataset(pd_shield, pd_grenade, pd_reload, feature_idle_dataset_l1,pd_logout)
    joined_dataset = joined_dataset.astype({'action': 'int32'})

    print(joined_dataset)
    joined_dataset.to_csv(OUTPUT_FULL_DATASET_LEFT)

if __name__ == "__main__":
    clean_right_glove_data()

    clean_left_glove_data()

    