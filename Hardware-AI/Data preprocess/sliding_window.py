from cmath import e
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

WINDOW_SIZE = 8
NUMBER_OF_FEATURES= 6
THRESHOLD = 0.12

DATA_FILE = 'shield.csv'


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

def graph_data_window(x_axis, y_axis):
    
    plt.plot(x_axis, y_axis)

    plt.show()


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

    # to graph out energy
    energy_arr = []
    time_arr = []

    for time, data in enumerate(raw_data):
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
            
                # calculate energy of window and prev window
                rms_acc_curr_window = 0
                rms_acc_prev_window = 0
                for idx, row in enumerate(window_data):
                    rms_acc_curr_window = rms_acc_curr_window + rmsValue(window_data.T[0:3], idx)
                    rms_acc_prev_window = rms_acc_prev_window + rmsValue(prev_window_data.T[0:3], idx)
                    
                energy_curr_window = rms_acc_curr_window / WINDOW_SIZE
                energy_prev_window = rms_acc_prev_window / len(prev_window_data)

                #print("time: ", time, "energy curr: ", energy_curr_window)

                # to graph out energy
                energy_arr.append(energy_curr_window)
                time_arr.append(time)

                if energy_curr_window - energy_prev_window > THRESHOLD:
                    print("start of move at: ", time)
                    action_arr = np.append(action_arr, window_data, axis=0)
                    start_of_move_flag = 1
        else: 
            action_arr = np.append(action_arr, data, axis=0)
            action_sample_count = action_sample_count + 1
            if action_sample_count == 22:
                segment_move(action_arr)

                # reset flags and action window
                start_of_move_flag = 0
                action_sample_count = 0
                action_arr = np.empty((0, NUMBER_OF_FEATURES))

    #graph_data_window(time_arr, energy_arr)

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
    for column_value in arr[:,col]:
        square += (pow(column_value,2))
     
    #Calculate Mean
    mean = (square / (float)(n))
     
    #Calculate Root
    root = math.sqrt(mean)
     
    return root


if __name__ == "__main__":
    data_pandas = pd.read_csv(DATA_FILE, header=None)
    raw_data = data_pandas.drop([0,7], axis=1).drop(data_pandas.index[0]).to_numpy().astype(float)
    sliding_window(raw_data)

    grenade_data = pd.read_csv(DATA_FILE, header=0)
    #graph_data(grenade_data, grenade_data.index)