import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew, median_abs_deviation, zscore


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

def graph_data_energy(data, x_axis, data_start_move, energy_data):
    energy_np = np.array(energy_data)
    diff = np.append(energy_np[1:],0) - energy_np

    data_start_move = np.reshape(data_start_move, (len(data_start_move)))
    start_move_index = (data_start_move==2).nonzero()[0]

    graph, axis = plt.subplots(nrows=5,
           sharex='col')
    axis[0].plot(x_axis, 'Linear-X', data=data, color="#1f77b4")
    axis[0].plot(x_axis, data_start_move, color="#000000")

    for index, val in enumerate(start_move_index):
        axis[0].annotate(index, (val, ([2]*len(start_move_index))[index]))

    axis[1].plot(x_axis, 'Linear-Y', data=data, color="#6DD3CE")
    axis[1].plot(x_axis, data_start_move, color="#000000")
    axis[2].plot(x_axis, 'Linear-Z', data=data, color="#C8E9A0")
    axis[2].plot(x_axis, data_start_move, color="#000000")
    axis[3].plot(x_axis, diff, color="000000")
    axis[3].plot(x_axis, [THRESHOLD]*len(diff), color = "#C8E9A0")
    axis[4].plot(x_axis, energy_data, color="#EEC6CA")
    axis[4].plot(x_axis, data_start_move, color="#000000")
    axis[4].plot(x_axis, [1] * len(x_axis), color="#F44708")
    axis[4].plot(x_axis, [0.5] * len(x_axis), color="#FAA613")

    plt.show()


# start of move without segmenting move
def calculate_energy(raw_data):
    window_data = np.empty((0,NUMBER_OF_SENSOR_FEATURES))

    # energy
    energy_arr = [0] * 8

    for time, data in enumerate(raw_data.to_numpy()):
        data = np.reshape(data, (1,NUMBER_OF_SENSOR_FEATURES))

            
        # replace any NaNs at the start of data stream with 0
        if len(window_data) < WINDOW_SIZE:
            if np.isnan(data).any():
                data = np.nan_to_num(data)
            
        window_data = np.append(window_data, data, axis=0)

        if len(window_data) > WINDOW_SIZE:
            window_data = np.delete(window_data, 0, axis=0)

            # replace any NaNs with the median of the previous datapoints
            if np.isnan(data).any():
                window_data = replace_nan(window_data)
            
            # calculate energy of window
            rms_acc_curr_window = 0
            for idx, row in enumerate(window_data):
                rms_acc_curr_window = rms_acc_curr_window + rmsValue_np(window_data.T[0:3], idx)
                    
            energy_curr_window = rms_acc_curr_window / WINDOW_SIZE
            energy_arr = np.append(energy_arr, energy_curr_window)

    raw_data["energy"] = energy_arr
    return raw_data


# =============================================== start of move algo ======================================================
WINDOW_SIZE = 8
NUMBER_OF_SENSOR_FEATURES= 6
PREDICTION_WINDOW_SIZE = 30
NUMBER_OF_FEATURES = 60

def start_of_move_sliding_window(raw_data):
    window_data = np.empty((0,NUMBER_OF_SENSOR_FEATURES+1))
    action_feature_data = np.empty((0, NUMBER_OF_FEATURES))

    # for graph plotting of start of move
    start_of_move_data = np.zeros((len(raw_data), 1))

    # variables to be used when start of move is identified
    start_of_move_flag = 0
    action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES+1))
    start_of_move_index = 0

    for time, data in enumerate(raw_data.to_numpy()):
        data = np.reshape(data, (1,NUMBER_OF_SENSOR_FEATURES+1))
            
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

            if (energy_curr_window - energy_prev_window > THRESHOLD) & (start_of_move_flag != 1):
                start_of_move_data[time] = 2

                action_arr = np.append(action_arr, window_data, axis=0)
                start_of_move_flag = 1

        if start_of_move_flag == 1: 
            action_arr = np.append(action_arr, data, axis=0)
            if len(action_arr) == PREDICTION_WINDOW_SIZE:
                action_features = segment_move(action_arr)
                action_feature_data = np.append(action_feature_data, np.reshape(action_features, (1,NUMBER_OF_FEATURES)), axis=0)

                # reset flags and action window
                start_of_move_flag = 0
                action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES+1))
                window_data = np.empty((0,NUMBER_OF_SENSOR_FEATURES+1))

                start_of_move_index = start_of_move_index + 1

    graph_data_energy(raw_data, raw_data.index, start_of_move_data, np.reshape(raw_data.iloc[:,6], (len(raw_data))))
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

def replace_nan(arr):
    for idx, val in enumerate(arr[WINDOW_SIZE-1]):
        if np.isnan(val):
            arr[WINDOW_SIZE-1, idx] = np.nan_to_num(arr[WINDOW_SIZE-1, idx], np.median(arr[0:WINDOW_SIZE-2, idx]))
    return arr

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

column_values = ['action', 'acc_x_mean', 'acc_x_std', 'acc_x_rms', 'acc_x_kurt', 'acc_x_skew', 'acc_x_iqr', 'acc_x_mad', 'acc_x_fmean', 'acc_x_frange', 'acc_x_fskew' ,
                    'acc_y_mean', 'acc_y_std', 'acc_y_rms', 'acc_y_kurt', 'acc_y_skew', 'acc_y_iqr', 'acc_y_mad', 'acc_y_fmean', 'acc_y_frange', 'acc_y_fskew',
                    'acc_z_mean', 'acc_z_std', 'acc_z_rms', 'acc_z_kurt', 'acc_z_skew', 'acc_z_iqr', 'acc_z_mad', 'acc_z_fmean', 'acc_z_frange', 'acc_z_fskew',
                    'gyro_x_mean', 'gyro_x_std', 'gyro_x_rms', 'gyro_x_kurt', 'gyro_x_skew', 'gyro_x_iqr', 'gyro_x_mad', 'gyro_x_fmean', 'gyro_x_frange', 'gyro_x_fskew',
                    'gyro_y_mean', 'gyro_y_std', 'gyro_y_rms', 'gyro_y_kurt', 'gyro_y_skew', 'gyro_y_iqr', 'gyro_y_mad',  'gyro_y_fmean', 'gyro_y_frange', 'gyro_y_fskew',
                    'gyro_z_mean', 'gyro_z_std', 'gyro_z_rms', 'gyro_z_kurt', 'gyro_z_skew', 'gyro_z_iqr', 'gyro_z_mad', 'gyro_z_fmean', 'gyro_z_frange', 'gyro_z_fskew']

# data files
FOLDER = 'riza/'

SHIELD_DATASET = FOLDER + 'shield_right_riza_beetle2.csv'
GRENADE_DATASET = FOLDER + 'grenade_right_riza_beetle2.csv'
RELOAD_DATASET = FOLDER + 'reload_right_riza_beetle2.csv'
LOGOUT_DATASET = FOLDER + 'logout_right_riza_beetle2.csv'

# output data files
OUTPUT_FOLDER = 'output_datasets/'

OUTPUT_SHIELD_DATASET = OUTPUT_FOLDER + 'output_shield_right_6.csv'
OUTPUT_GRENADE_DATASET = OUTPUT_FOLDER + 'output_grenade_right_6.csv'
OUTPUT_RELOAD_DATASET = OUTPUT_FOLDER + 'output_reload_right_6.csv'
OUTPUT_LOGOUT_DATASET = OUTPUT_FOLDER + 'output_logout_right_6.csv'

# ======== shit to be edited =============

THRESHOLD = 0.08 # threshold of the start of move detector. higher threshold -> harder to detect start of move, lower threshold -> easier to detect start of move

# ========================================

if __name__ == "__main__":

    # ================================ shield ==================================
    # shield_dataset = pd.read_csv(SHIELD_DATASET, header=0)
    # shield_dataset = shield_dataset.drop(['Timestamp', 'Label'], axis=1)
    # energy_shield = calculate_energy(shield_dataset)
    # feature_shield_dataset = start_of_move_sliding_window(energy_shield)

    # feature_shield_dataset = np.delete(feature_shield_dataset, [], axis=0) # for deleting of actions

    # # comment this part out for finding bad moves
    # feature_shield_dataset = np.hstack((np.full((len(feature_shield_dataset), 1), SHIELD_LABEL, dtype=int), feature_shield_dataset))
    # pd_shield = pd.DataFrame(data=feature_shield_dataset, columns=column_values)
    # pd_shield.astype({'action': 'int32'}).to_csv(OUTPUT_SHIELD_DATASET)


    # =============================== grenade ====================================
    # grenade_dataset = pd.read_csv(GRENADE_DATASET, header=0)
    # grenade_dataset = grenade_dataset.drop([ 'Timestamp', 'Label'], axis=1)
    # energy_grenade = calculate_energy(grenade_dataset)
    # feature_grenade_dataset = start_of_move_sliding_window(energy_grenade)

    # feature_grenade_dataset = np.delete(feature_grenade_dataset, [], axis=0) # for deleting of actions

    # # comment this part out for finding bad moves
    # feature_grenade_dataset = np.hstack((np.full((len(feature_grenade_dataset), 1), GRENADE_LABEL, dtype=int), feature_grenade_dataset))
    # pd_grenade = pd.DataFrame(data=feature_grenade_dataset, columns=column_values)
    # pd_grenade.astype({'action': 'int32'}).to_csv(OUTPUT_GRENADE_DATASET)


    # =============================== reload =====================================
    # reload_dataset = pd.read_csv(RELOAD_DATASET, header=0)
    # reload_dataset = reload_dataset.drop([ 'Timestamp', 'Label'], axis=1)
    # energy_reload = calculate_energy(reload_dataset)
    # feature_reload_dataset = start_of_move_sliding_window(energy_reload)

    # feature_reload_dataset = np.delete(feature_reload_dataset, [], axis=0) # for deleting of actions

    # # comment this part out for finding bad moves
    # feature_reload_dataset = np.hstack((np.full((len(feature_reload_dataset), 1), RELOAD_LABEL, dtype=int), feature_reload_dataset))
    # pd_reload = pd.DataFrame(data=feature_reload_dataset, columns=column_values)
    # #pd_reload.astype({'action': 'int32'}).to_csv(OUTPUT_RELOAD_DATASET)


    # =============================== logout =====================================
    logout_dataset = pd.read_csv(LOGOUT_DATASET, header=0)
    logout_dataset = logout_dataset.drop([ 'Timestamp', 'Label'], axis=1)
    energy_logout = calculate_energy(logout_dataset)
    feature_logout_dataset = start_of_move_sliding_window(energy_logout)

    feature_logout_dataset = np.delete(feature_logout_dataset, [46,47,50,55,66], axis=0) # for deleting of actions

    # comment this part out for finding bad moves
    feature_logout_dataset = np.hstack((np.full((len(feature_logout_dataset), 1), LOGOUT_LABEL, dtype=int), feature_logout_dataset))
    pd_logout = pd.DataFrame(data=feature_logout_dataset, columns=column_values)
    pd_logout.astype({'action': 'int32'}).to_csv(OUTPUT_LOGOUT_DATASET)