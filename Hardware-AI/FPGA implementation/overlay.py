from pynq import Overlay
import pynq
import numpy as np
import math

INPUT_SIZE = 30
OUTPUT_SIZE = 3

NUMBER_OF_SENSOR_FEATURES = 6
WINDOW_SIZE = 5
THRESHOLD = 2
THRESHOLD_NUMBER = 1

def test_input():
    stream = np.array([[0.3050025203548387,0.4475195293879845,0.5355742933800642,-1.1953125,0.96484375,-0.9778855847741936,0.7852111311764203,1.2461652448273612,-2.0,1.1484375,-0.059475806451612906,0.4977829006761008,0.4932869675930172,-1.047851563,0.912109375,-39.875504032258064,131.01913473818806,134.91600021123415,-220.734375,232.3203125,49.366431451612904,148.65692425640162,154.3472013041854,-228.4375,252.65625,91.27923387096774,137.9288067558928,163.5315424453612,-219.5390625,248.1328125],
                       [0.3169417843870968,0.4084586209243899,0.5117701186813375,-0.467773438,1.34375,-0.8568233367741936,0.8948316197908217,1.2284299181369258,-2.0,0.543945313,-0.09359249003225807,0.33352758132733495,0.3411917257385264,-1.076171875,0.71484375,-67.34122983870968,127.793012907188,142.61517165353547,-233.625,236.671875,66.59047379032258,172.70383566973325,182.47947059427344,-239.5859375,252.65625,84.46925403225806,141.50623043705326,162.8285362517868,-191.6640625,211.9453125],
                       [0.15439138106451614,0.8877503649687362,0.8868566995205867,-2.0,1.74609375,-0.9129599295161291,1.1415777467428188,1.4472929499889284,-2.0,1.33203125,0.04277973796774194,0.9347346037042363,0.9205292423429268,-1.372070313,1.999023438,18.95967741935484,100.93790777895842,101.09040782915818,-154.0234375,230.421875,-58.64969758064516,147.71209947546095,156.69976714876466,-252.4453125,214.2734375,-155.87399193548387,151.9035059804686,215.93293433854979,-249.90625,194.2578125],
                       [-0.32242313519354837,0.6787079913568423,0.741445692164287,-2.0,1.943359375,-0.5710055443548386,0.9702599748730227,1.11224271903476,-2.0,0.645507813,0.3726373488387097,1.1137707879895404,1.1572935258137227,-1.259765625,1.999023438,-79.29233870967742,175.1815326912453,189.69947422862944,-249.859375,250.3984375,-26.375252016129032,104.37999057281955,106.0159367882506,-221.578125,251.8203125,-27.748991935483872,147.03865405637507,147.28523750103363,-249.0,251.2578125],
                       [0.09926285296774194,0.7731717172087295,0.7670488410681348,-2.0,1.791015625,-0.8021988408064517,1.1236014777665517,1.3657518408117717,-2.0,1.111328125,-0.12427545370967742,0.5828807513400464,0.5867151627636273,-0.928710938,1.864257813,22.617691532258064,141.75615769183565,141.273311680024,-206.0546875,252.5546875,-34.64415322580645,151.78047538093705,153.27880133932467,-252.6796875,232.046875,-95.41154233870968,148.7758034860163,174.71002942592963,-235.359375,239.140625],
                       [-0.30276587725806453,0.3387097831356468,0.4502118492422212,-0.833984375,0.701171875,-0.8042149698709679,0.7574283161898684,1.0963361692427807,-2.0,0.294921875,-0.1682837702903226,0.43214940360948406,0.45721793557085433,-1.924804688,0.51953125,17.819808467741936,130.55094620957502,129.6584097113416,-254.6484375,245.6171875,-7.902721774193548,166.9619185266905,164.43691902564544,-249.6640625,250.59375,0.3528225806451613,157.41581001934372,154.85643469067847,-253.171875,247.0859375],
                       [-0.2807144658387097,0.47477504285852173,0.5449225807960367,-1.6484375,0.92578125,-1.0569556453548388,0.7643346753536477,1.297118856967369,-2.0,0.404296875,-0.1651020665483871,0.5650098930370298,0.5798249135237199,-2.0,1.138671875,39.040826612903224,137.5630601832346,140.84510323120458,-194.5078125,245.6171875,-9.60710685483871,158.17987531312352,155.90395928966387,-249.6640625,250.59375,24.602318548387096,173.6227617000435,172.56222793691896,-253.171875,247.0859375],
                       [-0.17578125006451614,0.856245708435185,0.8604682123894154,-2.0,1.999023438,-1.071005544483871,0.986115552930799,1.4450288051346092,-2.0,0.958984375,-0.5073399698709677,0.5761563642882648,0.7606850452310916,-1.362304688,0.772460938,-6.212953629032258,148.79492124644554,146.5071265731961,-211.9453125,196.015625,-40.379788306451616,135.0771173340183,138.88045163445938,-251.328125,231.2890625,-102.69934475806451,149.94298278692494,179.73535746695632,-248.6640625,173.3984375],
                       [-0.5366368448387098,0.5127395115719681,0.7364782457905306,-1.271484375,1.227539063,-0.8979964719677418,0.729027151866202,1.149231794166339,-2.0,0.36328125,0.3761340726129032,1.0904113123837145,1.1367140952312964,-1.494140625,1.876953125,-110.92338709677419,174.9479783101961,204.75223307304782,-235.6484375,243.3046875,-33.23991935483871,75.32407447455965,81.2132090924019,-173.0390625,242.953125,10.662802419354838,154.68553593419534,152.54327855863508,-249.25,251.0078125],
                       [-0.41885080667741936,0.4291139310551179,0.5946720137117432,-1.192382813,0.37890625,-0.9826738912903227,0.8060580227211184,1.2627028531395041,-2.0,0.26953125,-0.2615297380322581,0.5680058020980563,0.6169448570706472,-1.752929688,0.859375,32.46648185483871,129.92806062071406,131.8742404185122,-199.7578125,245.6171875,-16.007056451612904,179.61911985076108,177.4218454039158,-249.6640625,250.59375,-25.854334677419356,174.75120515113957,173.84284303629903,-253.171875,247.0859375]
    ])


    for index, data_point in enumerate(stream):

        for i, value in enumerate(data_point):
            in_buffer[i] = value

        dma.sendchannel.transfer(in_buffer)
        dma.recvchannel.transfer(out_buffer)

        dma.sendchannel.wait()
        dma.recvchannel.wait()

        print(index, ": ")

        for x in out_buffer:
            print(x)

        prediction = np.argmax(out_buffer)
        print('prediction: ', prediction, '\n')


# ============================== start of move identification code ================================
def replace_nan(arr):
    for idx, val in enumerate(arr[WINDOW_SIZE-1]):
        if np.isnan(val):
            arr[WINDOW_SIZE-1, idx] = np.nan_to_num(arr[WINDOW_SIZE-1, idx], np.median(arr[0:WINDOW_SIZE-2, idx]))
    return arr

def sliding_window(data):
    window_data = np.empty((0,NUMBER_OF_SENSOR_FEATURES))

    # variables to be used when start of move is identified
    start_of_move_flag = 0
    action_sample_count = 0
    action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES))

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
            segment_move(action_arr)

            # reset flags and action window
            start_of_move_flag = 0
            action_sample_count = 0
            action_arr = np.empty((0, NUMBER_OF_SENSOR_FEATURES))
        else:
            action_arr = np.append(action_arr, data, axis=0)
            action_sample_count = action_sample_count + 1
            # continue to send window result = none

def segment_move(action_window):
    # find statistical features of action and feed it to model

    action = {
        "acc_x_mean":action_window[:, 0].mean(),
        "acc_x_std":action_window[:, 0].std(),
        "acc_x_rms":rmsValue(action_window, 0),
        "acc_x_min":action_window[:, 0].min(),
        "acc_x_max":action_window[:, 0].max(),

        "acc_y_mean":action_window[:, 1].mean(),
        "acc_y_std":action_window[:, 1].std(),
        "acc_y_rms":rmsValue(action_window, 1),
        "acc_y_min":action_window[:, 1].min(),
        "acc_y_max":action_window[:, 1].max(),

        "acc_z_mean":action_window[:, 2].mean(),
        "acc_z_std":action_window[:, 2].std(),
        "acc_z_rms":rmsValue(action_window, 2),
        "acc_z_min":action_window[:, 2].min(),
        "acc_z_max":action_window[:, 2].max(),

        "gyro_x_mean":action_window[:, 3].mean(),
        "gyro_x_std":action_window[:, 3].std(),
        "gyro_x_rms":rmsValue(action_window, 3),
        "gyro_x_min":action_window[:, 3].min(),
        "gyro_x_max":action_window[:, 3].max(),

        "gyro_y_mean":action_window[:, 4].mean(),
        "gyro_y_std":action_window[:, 4].std(),
        "gyro_y_rms":rmsValue(action_window, 4),
        "gyro_y_min":action_window[:, 4].min(),
        "gyro_y_max":action_window[:, 4].max(),

        "gyro_z_mean":action_window[:, 5].mean(),
        "gyro_z_std":action_window[:, 5].std(),
        "gyro_z_rms":rmsValue(action_window, 5),
        "gyro_z_min":action_window[:, 5].min(),
        "gyro_z_max":action_window[:, 5].max()
        }

    action_features = np.array(list(action.values()))

    for i, value in enumerate(action_features):
            in_buffer[i] = value

    dma.sendchannel.transfer(in_buffer)
    dma.recvchannel.transfer(out_buffer)

    dma.sendchannel.wait()
    dma.recvchannel.wait()

    for x in out_buffer:
        print(x)

    prediction = np.argmax(out_buffer)
    print('prediction: ', prediction, '\n')


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
    overlay = Overlay('mlp_fpga_design.bit')

    dma = overlay.axi_dma_0

    in_buffer = pynq.allocate(shape=(INPUT_SIZE,), dtype=np.double)
    out_buffer = pynq.allocate(shape=(OUTPUT_SIZE,), dtype=np.double)

    test_input()