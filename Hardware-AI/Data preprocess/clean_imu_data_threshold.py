import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew

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


# =============================================== start of move algo ======================================================
WINDOW_SIZE = 8
NUMBER_OF_SENSOR_FEATURES= 6
THRESHOLD = 0.10
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

def join_and_shuffle_dataset2(dataset1, dataset2, dataset3, dataset4):
    joined_dataset = pd.concat([dataset1, dataset2, dataset3, dataset4])
    shuffled_dataset = joined_dataset.sample(frac=1).reset_index(drop=True)
    return shuffled_dataset

# ===================== main clean methods ====================
FULL_DATASET_RIGHT = 'full_data_right.csv'
FULL_DATASET_LEFT = 'full_data_left.csv'

# right glove
FOLDER_RIGHT_DATA = 'right_hand_data/'

SHIELD_DATASET7 = FOLDER_RIGHT_DATA + 'shield7.csv'
GRENADE_DATASET7 = FOLDER_RIGHT_DATA + 'grenade7.csv' 
RELOAD_DATASET7 = FOLDER_RIGHT_DATA + 'reload7.csv'
LOGOUT_DATASET4 = FOLDER_RIGHT_DATA + 'logout4.csv'


# left glove
FOLDER_LEFT_DATA = 'left_hand_data/'

SHIELD_DATASET_L6 = FOLDER_LEFT_DATA + 'shield_l6.csv'
GRENADE_DATASET_L4 = FOLDER_LEFT_DATA + 'grenade_l4.csv'
RELOAD_DATASET_L5 = FOLDER_LEFT_DATA + 'reload_l5.csv'
LOGOUT_DATASET_L4 = FOLDER_LEFT_DATA + 'logout_l4.csv'

RELOAD_DATASET_L7 = FOLDER_LEFT_DATA + 'reload_l7.csv'

LOGOUT_DATASET_L5 = FOLDER_LEFT_DATA + 'logout_l5.csv'
RELOAD_DATASET_L8 = FOLDER_LEFT_DATA + 'reload_l8.csv'

RELOAD_DATASET_L9 = FOLDER_LEFT_DATA + 'reload_l9.csv'

# output
OUTPUT_FULL_DATASET_RIGHT = 'final_full_data_right.csv'
OUTPUT_FULL_DATASET_LEFT = 'final_full_data_left.csv'

def clean_right_glove_data():
    # read full dataset to append to
    full_dataset = pd.read_csv(FULL_DATASET_RIGHT, header=0, index_col=0)

    # read all datasets
    shield_dataset7 = pd.read_csv(SHIELD_DATASET7, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset7 = pd.read_csv(RELOAD_DATASET7, header=0).drop(['Timestamp', 'Label'], axis=1)
    logout_dataset4 = pd.read_csv(LOGOUT_DATASET4, header=0).drop(['Timestamp', 'Label'], axis=1)


    # feature extraction of first dataset
    feature_shield_dataset7 = start_of_move_sliding(shield_dataset7)
    feature_reload_dataset7 = start_of_move_sliding(reload_dataset7)
    feature_logout_dataset4 = start_of_move_sliding(logout_dataset4)

    # add label column
    feature_shield_dataset7 = np.hstack((np.full((len(feature_shield_dataset7), 1), SHIELD_LABEL, dtype=int), feature_shield_dataset7))
    feature_reload_dataset7 = np.hstack((np.full((len(feature_reload_dataset7), 1), RELOAD_LABEL, dtype=int), feature_reload_dataset7))
    feature_logout_dataset4 = np.hstack((np.full((len(feature_logout_dataset4), 1), LOGOUT_LABEL, dtype=int), feature_logout_dataset4))

    column_values = ['action', 'acc_x_mean', 'acc_x_std', 'acc_x_rms', 'acc_x_kurt', 'acc_x_skew', 'acc_x_iqr', 'acc_x_mad', 'acc_x_fmean', 'acc_x_frange', 'acc_x_fskew' ,
                     'acc_y_mean', 'acc_y_std', 'acc_y_rms', 'acc_y_kurt', 'acc_y_skew', 'acc_y_iqr', 'acc_y_mad', 'acc_y_fmean', 'acc_y_frange', 'acc_y_fskew',
                     'acc_z_mean', 'acc_z_std', 'acc_z_rms', 'acc_z_kurt', 'acc_z_skew', 'acc_z_iqr', 'acc_z_mad', 'acc_z_fmean', 'acc_z_frange', 'acc_z_fskew',
                     'gyro_x_mean', 'gyro_x_std', 'gyro_x_rms', 'gyro_x_kurt', 'gyro_x_skew', 'gyro_x_iqr', 'gyro_x_mad', 'gyro_x_fmean', 'gyro_x_frange', 'gyro_x_fskew',
                     'gyro_y_mean', 'gyro_y_std', 'gyro_y_rms', 'gyro_y_kurt', 'gyro_y_skew', 'gyro_y_iqr', 'gyro_y_mad',  'gyro_y_fmean', 'gyro_y_frange', 'gyro_y_fskew',
                     'gyro_z_mean', 'gyro_z_std', 'gyro_z_rms', 'gyro_z_kurt', 'gyro_z_skew', 'gyro_z_iqr', 'gyro_z_mad', 'gyro_z_fmean', 'gyro_z_frange', 'gyro_z_fskew']

    pd_shield = pd.DataFrame(data=feature_shield_dataset7, columns=column_values)
    pd_reload = pd.DataFrame(data=feature_reload_dataset7, columns=column_values)
    pd_logout = pd.DataFrame(data=feature_logout_dataset4, columns=column_values)

    joined_dataset = join_and_shuffle_dataset2(pd_shield, pd_reload, pd_logout, full_dataset)
    joined_dataset = joined_dataset.astype({'action': 'int32'})
    print("right dataaset: ", joined_dataset)

    print("idle count: ", joined_dataset['action'].value_counts()[NONE_LABEL])
    print("shield count: ", joined_dataset['action'].value_counts()[SHIELD_LABEL])
    print("grenade count: ", joined_dataset['action'].value_counts()[GRENADE_LABEL])
    print("reload count: ", joined_dataset['action'].value_counts()[RELOAD_LABEL])
    print("logout count: ", joined_dataset['action'].value_counts()[LOGOUT_LABEL])

    joined_dataset.to_csv(OUTPUT_FULL_DATASET_RIGHT)

def clean_left_glove_data():
    full_dataset = pd.read_csv(FULL_DATASET_LEFT, header=0, index_col=0)

    # read all datasets
    shield_dataset_l6 = pd.read_csv(SHIELD_DATASET_L6, header=0).drop(['Timestamp', 'Label'], axis=1)
    grenade_dataset_l4 = pd.read_csv(GRENADE_DATASET_L4, header=0).drop(['Timestamp', 'Label'], axis=1)
    reload_dataset_l5 = pd.read_csv(RELOAD_DATASET_L5, header=0).drop(['Timestamp', 'Label'], axis=1)
    logout_dataset_l4 = pd.read_csv(LOGOUT_DATASET_L4, header=0).drop(['Timestamp', 'Label'], axis=1)

    reload_dataset_l7 = pd.read_csv(RELOAD_DATASET_L7, header=0).drop(['Timestamp', 'Label'], axis=1)

    reload_dataset_l8 = pd.read_csv(RELOAD_DATASET_L8, header=0).drop(['Timestamp', 'Label'], axis=1)
    logout_dataset_l5 = pd.read_csv(LOGOUT_DATASET_L5, header=0).drop(['Timestamp', 'Label'], axis=1)

    reload_dataset_l9 = pd.read_csv(RELOAD_DATASET_L9, header=0).drop(['Timestamp', 'Label'], axis=1)

    # feature extraction of first dataset
    feature_shield_dataset_l6 = start_of_move_sliding(shield_dataset_l6)
    feature_grenade_dataset_l4 = start_of_move_sliding(grenade_dataset_l4)
    feature_reload_dataset_l5 = start_of_move_sliding(reload_dataset_l5)
    feature_logout_dataset_l4 = start_of_move_sliding(logout_dataset_l4)

    feature_reload_dataset_l7 = start_of_move_sliding(reload_dataset_l7)
    feature_reload_dataset_l7 = np.delete(feature_reload_dataset_l7, len(feature_reload_dataset_l7)-23,axis=0)

    feature_reload_dataset_l8 = start_of_move_sliding(reload_dataset_l8)
    feature_reload_dataset_l8 = np.delete(feature_reload_dataset_l8,[1, 3, 4, 8, 13, 14, 16, 17,19, 27, 28,36,38,42,45,48,50,55,58,61,62,65,68,69,70,73,74,81,82,83,84,85,87,91,93,95,96,99,102,103,104,107,108,109,112,113,114,116,117,118,119,120,121], axis=0)
    feature_logout_dataset_l5 = start_of_move_sliding(logout_dataset_l5)
    feature_logout_dataset_l5 = np.delete(feature_logout_dataset_l5, [1,2,3,6,7,8,10,11,13,14,15,16,17,18,19,21,22,24,28,29,34,37,40,42,44,47], axis=0)

    feature_reload_dataset_l9 = start_of_move_sliding(reload_dataset_l9)
    feature_reload_dataset_l9 = np.delete(feature_reload_dataset_l9, [6,8,14,16,17,28,29], axis=0)

    # join datasets together
    feature_reload_dataset_l5 = np.concatenate([feature_reload_dataset_l5, feature_reload_dataset_l7, feature_reload_dataset_l8, feature_reload_dataset_l9], axis=0)
    feature_logout_dataset_l4 = np.concatenate([feature_logout_dataset_l4, feature_logout_dataset_l5], axis=0)

    # add label column
    feature_shield_dataset_l6 = np.hstack((np.full((len(feature_shield_dataset_l6), 1), SHIELD_LABEL, dtype=int), feature_shield_dataset_l6))
    feature_grenade_dataset_l4 = np.hstack((np.full((len(feature_grenade_dataset_l4), 1), GRENADE_LABEL, dtype=int), feature_grenade_dataset_l4))
    feature_reload_dataset_l5 = np.hstack((np.full((len(feature_reload_dataset_l5), 1), RELOAD_LABEL, dtype=int), feature_reload_dataset_l5))
    feature_logout_dataset_l4 = np.hstack((np.full((len(feature_logout_dataset_l4), 1), LOGOUT_LABEL, dtype=int), feature_logout_dataset_l4))

    column_values = ['action', 'acc_x_mean', 'acc_x_std', 'acc_x_rms', 'acc_x_kurt', 'acc_x_skew', 'acc_x_iqr', 'acc_x_mad', 'acc_x_fmean', 'acc_x_frange', 'acc_x_fskew' ,
                     'acc_y_mean', 'acc_y_std', 'acc_y_rms', 'acc_y_kurt', 'acc_y_skew', 'acc_y_iqr', 'acc_y_mad', 'acc_y_fmean', 'acc_y_frange', 'acc_y_fskew',
                     'acc_z_mean', 'acc_z_std', 'acc_z_rms', 'acc_z_kurt', 'acc_z_skew', 'acc_z_iqr', 'acc_z_mad', 'acc_z_fmean', 'acc_z_frange', 'acc_z_fskew',
                     'gyro_x_mean', 'gyro_x_std', 'gyro_x_rms', 'gyro_x_kurt', 'gyro_x_skew', 'gyro_x_iqr', 'gyro_x_mad', 'gyro_x_fmean', 'gyro_x_frange', 'gyro_x_fskew',
                     'gyro_y_mean', 'gyro_y_std', 'gyro_y_rms', 'gyro_y_kurt', 'gyro_y_skew', 'gyro_y_iqr', 'gyro_y_mad',  'gyro_y_fmean', 'gyro_y_frange', 'gyro_y_fskew',
                     'gyro_z_mean', 'gyro_z_std', 'gyro_z_rms', 'gyro_z_kurt', 'gyro_z_skew', 'gyro_z_iqr', 'gyro_z_mad', 'gyro_z_fmean', 'gyro_z_frange', 'gyro_z_fskew']

    pd_shield = pd.DataFrame(data=feature_shield_dataset_l6, columns=column_values)
    pd_grenade = pd.DataFrame(data=feature_grenade_dataset_l4, columns=column_values)
    pd_reload = pd.DataFrame(data=feature_reload_dataset_l5, columns=column_values)
    pd_logout = pd.DataFrame(data=feature_logout_dataset_l4, columns=column_values)

    joined_dataset = join_and_shuffle_dataset(pd_shield, pd_grenade, pd_reload, pd_logout, full_dataset)
    joined_dataset = joined_dataset.astype({'action': 'int32'})
    print("left dataset: ", joined_dataset)

    print("idle count: ", joined_dataset['action'].value_counts()[NONE_LABEL])
    print("shield count: ", joined_dataset['action'].value_counts()[SHIELD_LABEL])
    print("grenade count: ", joined_dataset['action'].value_counts()[GRENADE_LABEL])
    print("reload count: ", joined_dataset['action'].value_counts()[RELOAD_LABEL])
    print("logout count: ", joined_dataset['action'].value_counts()[LOGOUT_LABEL])

    joined_dataset.to_csv(OUTPUT_FULL_DATASET_LEFT)

if __name__ == "__main__":
    clean_right_glove_data()

    clean_left_glove_data()