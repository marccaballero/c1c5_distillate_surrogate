import os, glob, json
import pandas as pd
import pickle
from csv import writer
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

json_dir = './Simulation_Files/test_data'
json_pattern = os.path.join(json_dir, 'disc_sims_*.json')
file_list = glob.glob(json_pattern)
csv_data_path = './Simulation_Files/train_files/classif_data.csv'

lstart = 0
lend = 65
# Very manual way to do it. If info is added or removed from the column object, this won't work. ToDo: automate it in a robust way

def join_json_to_csv():
    print("Joining Json data into single .CSV file. Please wait...")
    if not os.path.isfile(csv_data_path):
        # Write headers
        with open(csv_data_path, 'a', newline='') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(['', "N_trays", "Feed_tray", "RR", "D:F", "F_t", "F_F1", "F_F2", "F_F3","F_F4", "F_F5", "F_F6", "F_F7", "F_F8", "Conv"])
            f_object.close()
        # Open all the jsons and write into a single csv file
        pbar = tqdm(total=len(file_list))
        for json_file in file_list:
            with open(json_file, 'r') as f:
                raw_data = f.readlines()

            # Write each line
            for i in range(len(raw_data)//lend):
                col_dict = json.loads(''.join(raw_data[lend*i:lend*i+lend]).replace('\n', ''))

                l_data = [col_dict["col_id"], col_dict["number_trays"], col_dict["feed_tray"], col_dict["reflux_ratio"], col_dict["df_ratio"], col_dict["feed"]["temperature"]] + col_dict["feed"]["mass_flows"] + [col_dict["convergence"]]


                with open(csv_data_path, 'a', newline='') as f_object:
                    writer_object = writer(f_object)
                    writer_object.writerow(l_data)
                    f_object.close()
            pbar.update()
    print("Json to .CSV complete")
    
def pre_processing():

    print("Pre-processing data, please wait...")
    # Import input/output data
    dt = pd.read_csv(csv_data_path, index_col=0)

    #Train, test, dev splitting
    train_size = dt.shape[0]*8//10
    dev_size = dt.shape[0]*1//10

    # Normalize the dataset
    nrm = StandardScaler()
    nrm.fit(dt.iloc[:,:])
    dt.iloc[:,:] = pd.DataFrame(nrm.transform(dt.iloc[:,:]), columns=dt.columns[:], index=dt.index)
    # Shuffle the dataset
    dt = dt.sample(frac=1)

    # Split the data into train/dev/test
    data_train = dt.iloc[:train_size,:]
    data_dev = dt.iloc[train_size:train_size+dev_size, :]
    data_test = dt.iloc[train_size+dev_size:, :]

    # Write individual files for each split
    data_train.to_csv('./Simulation_Files/train_files/classif_train.csv')
    data_test.to_csv('./Simulation_Files/train_files/classif_test.csv')
    data_dev.to_csv('./Simulation_Files/train_files/classif_dev.csv')


    with open('./Simulation_Files/train_files/norm_vars.pickle', 'wb') as f:
        pickle.dump(nrm,f)

    print("Data preprocessing complete")

if __name__ == '__main__':
    join_json_to_csv()
    pre_processing()
