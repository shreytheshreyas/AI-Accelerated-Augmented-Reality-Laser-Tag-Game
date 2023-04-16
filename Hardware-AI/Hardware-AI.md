# Documentation for Hardware-AI
## Data preprocess
Data preprocess folder contains the code for processing raw data obtained from hardware sensors, and outputting a train and test dataset for training the software model. It also outputs the pickle files of the trained Standard Scaler and Principal Component Analysis (PCA).

`clean_imu_data.py` and `clean_imu_data_threshold.py` is the code to segment actions (of 60 features) for the 2-player evaluation. `clean_imu_data_threshold.py` is used to detect moves with a different threshold from `clean_imu_data.py`. While `clean_imu_data_collab.py` is the code to segment actions for the unseen player evaluation.

`feature_extraction.py` is the code to do dimensionality reduction on the actions obtained from the code above. It reduces the 60 action features into 16, and splits the dataset up into train and test data to be used to train the software model.

### Set up
* Copy the .csv files of the raw hardware sensor data into the same directory as `clean_imu_data.py`.
* In `clean_imu_data.py`, ensure that the file name to be read is specified correctly. The global variable to be changed is `<ACTION>_DATASET`.
* Run the code by calling `python clean_imu_data.py`. You may also choose to run it in an IDE. You will get an output of a .csv file containing the actions extracted (of 60 features).
* Alternatively, you can also use `clean_imu_data_threshold.py` or  `clean_imu_data_collab.py`. Repeat the same steps as above.
* After obtaining the dataset containing extracted actions (of 60 features), ensure that the dataset is in the same directory as `feature_extraction.py`.
* In `feature_extraction.py`, ensure that the file name to be read is specified correctly. The global variable to be changed is `FULL_DATASET_<SIDE>`.
* Run the code by calling `python feature_extraction.py`. You may also choose to run it in an IDE. You will get an output of 2 .csv files, which are train and test datasets containing actions of 16 features.

## Software implementation
Software implementation folder contains the code for training the software Multi-Layer Perceptron (MLP) model. It takes in the train and test datasets obtained from the data preprocessing stage, and outputs weights and biases of the trained model in a .txt file.

### Set up
* Copy the .csv files of the train and test dataset into the same directory as `mlp.py`.
* In `mlp.py`, ensure that the file name to be read is specified correctly. The global variable to be changed is `TRAIN_FILE_<SIDE>` and `TEST_FILE<SIDE>`.
* Run the code by calling `python mlp.py`. You may also choose to run it in an IDE. You will get an output of the balanced accuracy and ROC AUC score of the model, along with the weights and biases of the trained model as two .txt files.

## HLS code
HLS code folder contains the code for generating the HLS IP. `mlp_hls_sol.cpp` is the source code for the right glove model and `mlp_hls_sol_left.cpp` is the source code for the left glove model.

### Set up
* Open up Vivado HLS.
* Select `Create new project`. Ensure that the files in the folder are copied to the directory `\AppData\Roaming\Xilinx\Vivado`.
* When prompted to add C Source files and C Test bench files, select `mlp_hls_sol.cpp` and `test_mlp_hls_sol.cpp` respectively.
* Select the appropriate device part.
* Once done setting up the project, run the pipeline to generate HLS IP accordingly.

## FPGA implementation
FPGA implementation folder contains the files to be uploaded to the Ultra96. It contains the bitstream of the MLP design, the hardware handoff file, and the pickle files of the trained Standard Scaler and PCA.

### Set up
* SCP the files in this folder to the Ultra96 by running `scp <file name> xilinx@<address>:`. Enter the password to the Ultra96 accordingly.