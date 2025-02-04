#!/usr/bin/env python3
"""
Export all datasets from an HDF5 file to CSV files.

This script opens an HDF5 file (assumed here to be "preprocess.h5" in the "data" folder)
and recursively iterates through all groups and datasets. Each dataset is exported as a CSV file
into the specified output directory. The CSV filenames are derived from the full HDF5 path.

Usage:
    python preprocess.py --input data/preprocess.h5 --output_dir exported_csv

Dependencies:
    - h5py
    - pandas
"""

import os
import argparse
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
    # Retrieve the data from the dataset.
    data = dataset[()]
    
    # Handle different dimensionalities:
    if data.ndim == 1:
        # One-dimensional data becomes a single column.
        df = pd.DataFrame(data, columns=["Value"])
    elif data.ndim == 2:
        # Two-dimensional data: assume each row is an observation.
        df = pd.DataFrame(data)
    else:
        # For higher dimensions, we flatten the dataset into 2D.
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
        # Construct a new base path for this item.
        new_base = f"{base_path}/{key}" if base_path else key
        if isinstance(item, h5py.Group):
            recursive_export(item, new_base, output_dir)
        elif isinstance(item, h5py.Dataset):
            # Replace "/" with "__" to create a safe filename.
            csv_filename = os.path.join(output_dir, new_base.replace("/", "__") + ".csv")
            export_dataset_to_csv(item, csv_filename)

def main(input_h5, output_dir):
    """
    Main function to open the HDF5 file and export all datasets to CSV files.
    """
    if not os.path.exists(input_h5):
        logging.error("Input file not found: %s", input_h5)
        return

    os.makedirs(output_dir, exist_ok=True)
    with h5py.File(input_h5, 'r') as f:
        logging.info("Opened HDF5 file with keys: %s", list(f.keys()))
        recursive_export(f, "", output_dir)
    logging.info("Export complete. CSV files are in %s", output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Export all datasets from an HDF5 file to CSV files"
    )
    parser.add_argument("--input", type=str, required=True, help="Path to input HDF5 file")
    parser.add_argument("--output_dir", type=str, default="exported2_csv", help="Directory to store CSV files")
    args = parser.parse_args()

    main(args.input, args.output_dir)
