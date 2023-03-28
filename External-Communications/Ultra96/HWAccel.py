import math
import pickle
import numpy as np
from scipy.stats import kurtosis, skew

import pynq
from Helper import Actions


INPUT_SIZE = 16
OUTPUT_SIZE = 5

NUMBER_OF_SENSOR_FEATURES = 6
NUMBER_OF_ACTION_FEATURES = 60
START_MOVE_WINDOW_SIZE = 8
PREDICTION_WINDOW_SIZE = 30
THRESHOLD = 0.12


class PlayerHWAccel:
    def __init__(
        self,
        in_queue,
        out_queue,
        dma,
        scaler_file,
        pca_file,
    ):
        self.prev = 0
        self.count = 0
        self.total = 0

        self.dma = dma

        self.in_queue = in_queue
        self.out_queue = out_queue

        with open(scaler_file, 'rb') as pickle_file:
            scaler = pickle.load(pickle_file)

        with open(pca_file, 'rb') as pickle_file:
            pca = pickle.load(pickle_file)

        self.scaler = scaler
        self.pca = pca

        self.in_buffer = pynq.allocate(shape=(INPUT_SIZE,), dtype=np.double)
        self.out_buffer = pynq.allocate(shape=(OUTPUT_SIZE,), dtype=np.double)
        self.window_data = np.empty((0, NUMBER_OF_SENSOR_FEATURES))

        # self.variables to be used when start of move is identified
        self.start_of_move_flag = 0
        self.action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES))

    def run(self):
        while True:
            data = self.in_queue.get()
            prediction = self.get_action(data)
            self.out_queue.put(prediction)

    def replace_nan(self, arr):
        for idx, val in enumerate(arr[START_MOVE_WINDOW_SIZE - 1]):
            if np.isnan(val):
                arr[START_MOVE_WINDOW_SIZE - 1, idx] = np.nan_to_num(
                    arr[START_MOVE_WINDOW_SIZE - 1, idx],
                    np.median(arr[0 : START_MOVE_WINDOW_SIZE - 2, idx]),
                )

    def get_action(self, data):
        data = np.reshape(data, (1, NUMBER_OF_SENSOR_FEATURES))

        if self.start_of_move_flag == 0:
            # replace any NaNs at the start of data stream with 0
            if len(self.window_data) < START_MOVE_WINDOW_SIZE:
                if np.isnan(data).any():
                    data = np.nan_to_num(data)

            prev_window_data = self.window_data
            self.window_data = np.append(self.window_data, data, axis=0)

            if len(self.window_data) > START_MOVE_WINDOW_SIZE:
                self.window_data = np.delete(self.window_data, 0, axis=0)

                # replace any NaNs with the median of the previous datapoints
                if np.isnan(data).any():
                    self.window_data = self.replace_nan(self.window_data)

                # calculate energy of window and prev window
                rms_acc_curr_window = 0
                rms_acc_prev_window = 0
                for idx, row in enumerate(self.window_data):
                    rms_acc_curr_window = rms_acc_curr_window + self.rmsValue(
                        self.window_data.T[0:3], idx
                    )
                    rms_acc_prev_window = rms_acc_prev_window + self.rmsValue(
                        prev_window_data.T[0:3], idx
                    )

                energy_curr_window = rms_acc_curr_window / len(self.window_data)
                energy_prev_window = rms_acc_prev_window / len(prev_window_data)

                # start of move identifier, find if increase in energy of the windows is > threshold
                if energy_curr_window - energy_prev_window > THRESHOLD:
                    self.action_arr = np.append(
                        self.action_arr, self.window_data, axis=0
                    )
                    self.start_of_move_flag = 1
        else:
            self.action_arr = np.append(self.action_arr, data, axis=0)
            if len(self.action_arr) == PREDICTION_WINDOW_SIZE:
                prediction = self.segment_move(self.action_arr)

                # reset flags and action window
                self.start_of_move_flag = 0
                self.action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES))

                return prediction

        return Actions.no

    def segment_move(self, action_window):
        # find statistical features of action and feed it to model
        window_fft = np.fft.fft(action_window, axis=0)

        action = {
        "acc_x_mean":action_window[:, 0].mean(),
        "acc_x_std":action_window[:, 0].std(),
        "acc_x_rms":self.rmsValue(action_window, 0),
        "acc_x_kurt":kurtosis(action_window[:, 0]),
        "acc_x_skew":skew(action_window[:, 0]),
        "acc_x_iqr":np.percentile(action_window[:, 0], 75) - np.percentile(action_window[:, 0], 25),
        "acc_x_mad":np.median(np.absolute(action_window[:,0] - np.median(action_window[:,0]))),
        "acc_x_fmean":window_fft[:, 0].mean().real,
        "acc_x_frange":(window_fft[:, 0].max() - window_fft[:,0].min()).real,
        "acc_x_fskew":skew(window_fft[:, 0]).real,

        "acc_y_mean":action_window[:, 1].mean(),
        "acc_y_std":action_window[:, 1].std(),
        "acc_y_rms":self.rmsValue(action_window, 1),
        "acc_y_kurt":kurtosis(action_window[:, 1]),
        "acc_y_skew":skew(action_window[:, 1]),
        "acc_y_iqr":np.percentile(action_window[:, 1], 75) - np.percentile(action_window[:, 1], 25),
        "acc_y_mad":np.median(np.absolute(action_window[:,1] - np.median(action_window[:,1]))),
        "acc_y_fmean":window_fft[:, 1].mean().real,
        "acc_y_frange":(window_fft[:, 1].max() - window_fft[:,1].min()).real,
        "acc_y_fskew":skew(window_fft[:, 1]).real,

        "acc_z_mean":action_window[:, 2].mean(),
        "acc_z_std":action_window[:, 2].std(),
        "acc_z_rms":self.rmsValue(action_window, 2),
        "acc_z_kurt":kurtosis(action_window[:, 2]),
        "acc_z_skew":skew(action_window[:, 2]),
        "acc_z_iqr":np.percentile(action_window[:, 2], 75) - np.percentile(action_window[:, 2], 25),
        "acc_z_mad":np.median(np.absolute(action_window[:,2] - np.median(action_window[:,2]))),
        "acc_z_fmean":window_fft[:, 2].mean().real,
        "acc_z_frange":(window_fft[:, 2].max() - window_fft[:,2].min()).real,
        "acc_z_fskew":skew(window_fft[:, 2]).real,

        "gyro_x_mean":action_window[:, 3].mean(),
        "gyro_x_std":action_window[:, 3].std(),
        "gyro_x_rms":self.rmsValue(action_window, 3),
        "gyro_x_kurt":kurtosis(action_window[:, 3]),
        "gyro_x_skew":skew(action_window[:, 3]),
        "gyro_x_iqr":np.percentile(action_window[:, 3], 75) - np.percentile(action_window[:, 3], 25),
        "gyro_x_mad":np.median(np.absolute(action_window[:,3] - np.median(action_window[:,3]))),
        "gyro_x_fmean":window_fft[:, 3].mean().real,
        "gyro_x_frange":(window_fft[:, 3].max() - window_fft[:,3].min()).real,
        "gyro_x_fskew":skew(window_fft[:, 3]).real,

        "gyro_y_mean":action_window[:, 4].mean(),
        "gyro_y_std":action_window[:, 4].std(),
        "gyro_y_rms":self.rmsValue(action_window, 4),
        "gyro_y_kurt":kurtosis(action_window[:, 4]),
        "gyro_y_skew":skew(action_window[:, 4]),
        "gyro_y_iqr":np.percentile(action_window[:, 4], 75) - np.percentile(action_window[:, 4], 25),
        "gyro_y_mad":np.median(np.absolute(action_window[:,4] - np.median(action_window[:,4]))),
        "gyro_y_fmean":window_fft[:, 4].mean().real,
        "gyro_y_frange":(window_fft[:, 4].max() - window_fft[:,4].min()).real,
        "gyro_y_fskew":skew(window_fft[:, 4]).real,

        "gyro_z_mean":action_window[:, 5].mean(),
        "gyro_z_std":action_window[:, 5].std(),
        "gyro_z_rms":self.rmsValue(action_window, 5),
        "gyro_z_kurt":kurtosis(action_window[:, 5]),
        "gyro_z_skew":skew(action_window[:, 5]),
        "gyro_z_iqr":np.percentile(action_window[:, 5], 75) - np.percentile(action_window[:, 5], 25),
        "gyro_z_mad":np.median(np.absolute(action_window[:,5] - np.median(action_window[:,5]))),
        "gyro_z_fmean":window_fft[:, 5].mean().real,
        "gyro_z_frange":(window_fft[:, 5].max() - window_fft[:,5].min()).real,
        "gyro_z_fskew":skew(window_fft[:, 5]).real
        }

        action_features = np.array(list(action.values()))

        # final model input is 16 features after dimensionality reduction
        model_input = self.feature_reduction(action_features)

        for i, value in enumerate(model_input):
            self.in_buffer[i] = value

        self.dma.sendchannel.transfer(self.in_buffer)
        self.dma.recvchannel.transfer(self.out_buffer)

        self.dma.sendchannel.wait()
        self.dma.recvchannel.wait()
        
        prediction = Actions.glove[np.argmax(self.out_buffer)]
        print("prediction:", prediction)
        return prediction

    def rmsValue(self, arr, col):
        square = 0
        mean = 0.0
        root = 0.0
        n = arr.shape[0]

        # Calculate square
        for column_value in arr[:, col]:
            square += pow(column_value, 2)

        # Calculate Mean
        mean = square / (float)(n)

        # Calculate Root
        root = math.sqrt(mean)

        return root
    
    def feature_reduction(self, action_features):
        # reduce 60 action features to 16 using PCA

        action_features = np.reshape(action_features, (1, NUMBER_OF_ACTION_FEATURES))

        pca_action_features = self.pca.transform(self.scaler.transform(action_features))

        return pca_action_features

class HWAccel:
    def __init__(
        self,
        in_queue_p1,
        in_queue_p2,
        out_queue_p1,
        out_queue_p2,
    ):
        self.in_queue_p1 = in_queue_p1
        self.in_queue_p2 = in_queue_p2
        self.out_queue_p1 = out_queue_p1
        self.out_queue_p2 = out_queue_p2

        self.overlay = pynq.Overlay("mlp_fpga_design.bit")

        self.dma_p1 = self.overlay.axi_dma_0
        self.dma_p2 = self.overlay.axi_dma_1

        self.scaler_p1 = 'scaler.pkl'
        self.scaler_p2 = 'scaler_left.pkl'

        self.pca_p1 = 'pca.pkl'
        self.pca_p2 = 'pca_left.pkl'

        self.p1 = PlayerHWAccel(self.in_queue_p1, self.out_queue_p1, self.dma_p1, self.scaler_p1, self.pca_p1)
        self.p2 = PlayerHWAccel(self.in_queue_p2, self.out_queue_p2, self.dma_p2, self.scaler_p2, self.pca_p2)
