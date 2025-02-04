#!/usr/bin/env python3
"""
Automatically export each dataset from the HDF5 file containing ".dat." in its name 
(from the ./data folder) into separate CSV files. All CSV files will be saved inside 
a folder named "exported_data" in the project root.

No command-line input is required.
"""

import os
import h5py
import pandas as pd
import logging

# Set up production-grade logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def export_dataset_to_csv(dataset, csv_filename):
    """
    Exports a single HDF5 dataset to a CSV file.
    
    Parameters:
      dataset: The h5py.Dataset object.
      csv_filename: The output CSV filename.
    """
    data = dataset[()]
    # Handle different dimensionalities:
    if data.ndim == 1:
        # One-dimensional data becomes a single column.
        df = pd.DataFrame(data, columns=["Value"])
    elif data.ndim == 2:
        # Two-dimensional data: assume each row is an observation.
        df = pd.DataFrame(data)
    else:
        # For higher dimensions, flatten the dataset into 2D.
        df = pd.DataFrame(data.reshape(data.shape[0], -1))
    
    df.to_csv(csv_filename, index=False)
    logging.info("Exported dataset to %s", csv_filename)

def recursive_export(h5group, base_path, output_dir):
    """
    Recursively iterates through an HDF5 group and exports each dataset found.
    
    Parameters:
      h5group: The current h5py.Group object.
      base_path: The current group path as a string.
      output_dir: Directory where CSV files are saved.
    """
    for key in h5group:
        item = h5group[key]
        new_base = f"{base_path}/{key}" if base_path else key
        if isinstance(item, h5py.Group):
            recursive_export(item, new_base, output_dir)
        elif isinstance(item, h5py.Dataset):
            # Replace "/" with "__" to create a safe filename.
            csv_filename = os.path.join(output_dir, new_base.replace("/", "__") + ".csv")
            export_dataset_to_csv(item, csv_filename)

def main():
    # Define the data directory.
    data_dir = os.path.join(os.getcwd(), "data")
    
    # Automatically search for a file with ".dat." in its name ending with .h5.
    input_file = None
    for filename in os.listdir(data_dir):
        if ".dat." in filename and filename.endswith(".h5"):
            input_file = os.path.join(data_dir, filename)
            break

    if not input_file:
        logging.error("No .dat.h5 file found in the data directory.")
        return

    logging.info("Using file: %s", input_file)
    
    # Create an output folder named "exported_data" in the project root.
    output_dir = os.path.join(os.getcwd(), "exported_data")
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
