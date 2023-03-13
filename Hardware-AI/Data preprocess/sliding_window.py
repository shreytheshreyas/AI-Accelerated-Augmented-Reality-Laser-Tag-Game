import numpy as np
import pandas as pd
import math

WINDOW_SIZE = 5
NUMBER_OF_FEATURES= 6
THRESHOLD = 2
THRESHOLD_NUMBER = 1

DATA_FILE = 'dataset1.csv'

def replace_nan(arr):
    for idx, val in enumerate(arr[WINDOW_SIZE-1]):
        if np.isnan(val):
            arr[WINDOW_SIZE-1, idx] = np.nan_to_num(arr[WINDOW_SIZE-1, idx], np.median(arr[0:WINDOW_SIZE-2, idx]))
    return arr


def sliding_window(raw_data):
    window_data = np.empty((0,NUMBER_OF_FEATURES))

    # variables to be used when start of move is identified
    start_of_move_flag = 0
    action_sample_count = 0
    action_arr = np.empty((0, NUMBER_OF_FEATURES))

    for data in raw_data:
        data = np.reshape(data, (1,NUMBER_OF_FEATURES))

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
            
                # if mean of current window > mean + k * std of prev window, identify as start of move
                data_above_threshold = 0
                for idx, col in enumerate(window_data.T):
                    mean_curr_window = np.mean(col)
                    mean_prev_window = np.mean(prev_window_data[:, idx])
                    std_curr_window = np.std(col)

                    if mean_curr_window > mean_prev_window + THRESHOLD * std_curr_window:
                        data_above_threshold = data_above_threshold + 1
                if data_above_threshold > THRESHOLD_NUMBER:
                    print("start of move at: ", window_data)
                    action_arr = np.append(action_arr, window_data, axis=0)
                    start_of_move_flag = 1
        else: 
            if action_sample_count == 15:
                print("action sample: ")
                segment_move(action_arr)

                # reset flags and action window
                start_of_move_flag = 0
                action_sample_count = 0
                action_arr = np.empty((0, NUMBER_OF_FEATURES))
            else:
                action_arr = np.append(action_arr, data, axis=0)
                action_sample_count = action_sample_count + 1

def segment_move(window):
    # find statistical features of window and feed it to model

    action = {
        "acc_x_mean":window[:, 0].mean(),
        "acc_x_std":window[:, 0].std(),
        "acc_x_rms":rmsValue(window, 0),
        "acc_x_min":window[:, 0].min(),
        "acc_x_max":window[:, 0].max(),

        "acc_y_mean":window[:, 1].mean(),
        "acc_y_std":window[:, 1].std(),
        "acc_y_rms":rmsValue(window, 1),
        "acc_y_min":window[:, 1].min(),
        "acc_y_max":window[:, 1].max(),

        "acc_z_mean":window[:, 2].mean(),
        "acc_z_std":window[:, 2].std(),
        "acc_z_rms":rmsValue(window, 2),
        "acc_z_min":window[:, 2].min(),
        "acc_z_max":window[:, 2].max(),

        "gyro_x_mean":window[:, 3].mean(),
        "gyro_x_std":window[:, 3].std(),
        "gyro_x_rms":rmsValue(window, 3),
        "gyro_x_min":window[:, 3].min(),
        "gyro_x_max":window[:, 3].max(),

        "gyro_y_mean":window[:, 4].mean(),
        "gyro_y_std":window[:, 4].std(),
        "gyro_y_rms":rmsValue(window, 4),
        "gyro_y_min":window[:, 4].min(),
        "gyro_y_max":window[:, 4].max(),

        "gyro_z_mean":window[:, 5].mean(),
        "gyro_z_std":window[:, 5].std(),
        "gyro_z_rms":rmsValue(window, 5),
        "gyro_z_min":window[:, 5].min(),
        "gyro_z_max":window[:, 5].max()
        }

    action_features = list(action.values())

    print(np.array(action_features))

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


if __name__ == "__main__":
    data_pandas = pd.read_csv(DATA_FILE, header=None)
    raw_data = data_pandas.drop([0,7], axis=1).drop(data_pandas.index[0]).to_numpy().astype(float)
    print(raw_data)
    sliding_window(raw_data)