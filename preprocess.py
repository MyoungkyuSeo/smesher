#!/usr/bin/env python3
import os
import h5py
import pandas as pd
import logging
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def export_dataset_to_csv(dataset, csv_filename):
    data = dataset[()]
    if data.ndim == 1:
        df = pd.DataFrame(data, columns=["Value"])
    elif data.ndim == 2:
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data.reshape(data.shape[0], -1))
    df.to_csv(csv_filename, index=False)
    logging.info("Exported dataset to %s", csv_filename)

def recursive_export(h5group, base_path, output_dir):
    for key in h5group:
        item = h5group[key]
        new_base = f"{base_path}/{key}" if base_path else key
        if isinstance(item, h5py.Group):
            recursive_export(item, new_base, output_dir)
        elif isinstance(item, h5py.Dataset):
            csv_filename = os.path.join(output_dir, new_base.replace("/", "__") + ".csv")
            export_dataset_to_csv(item, csv_filename)

def main():
    data_dir = os.path.join(os.getcwd(), "data")
    input_file = None
    for filename in os.listdir(data_dir):
        if ".dat." in filename and filename.endswith(".h5"):
            input_file = os.path.join(data_dir, filename)
            break
    if not input_file:
        logging.error("No .dat.h5 file found in the data directory.")
        return
    logging.info("Using file: %s", input_file)
    
    # Define and clear the output folder "exported_data"
    output_dir = os.path.join(os.getcwd(), "exported_data")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        logging.info("Cleared existing folder: %s", output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with h5py.File(input_file, 'r') as f:
            logging.info("Opened HDF5 file with top-level keys: %s", list(f.keys()))
            recursive_export(f, "", output_dir)
    except Exception as e:
        logging.exception("Error processing the HDF5 file: %s", e)
        return
    logging.info("Export complete. CSV files are in %s", output_dir)

if __name__ == '__main__':
    main()
