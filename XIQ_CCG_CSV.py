#!/usr/bin/env python3
import logging
import argparse
import sys
import os
import json
import inspect
import getpass
import pandas as pd
import numpy as np
from pprint import pprint as pp
from app.logger import logger
from app.xiq_api import XIQ
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
logger = logging.getLogger('Serial-CCG.Main')

XIQ_API_token = ''

pageSize = 100

parser = argparse.ArgumentParser()
parser.add_argument('--external',action="store_true", help="Optional - adds External Account selection, to use an external VIQ")
args = parser.parse_args()

PATH = current_dir

if XIQ_API_token:
    x = XIQ(token=XIQ_API_token)
else:
    print("Enter your XIQ login credentials")
    username = input("Email: ")
    password = getpass.getpass("Password: ")
    x = XIQ(user_name=username,password = password)

#OPTIONAL - use externally managed XIQ account
if args.external:
    accounts, viqName = x.selectManagedAccount()
    if accounts == 1:
        validResponse = False
        while validResponse != True:
            response = input("No External accounts found. Would you like to import data to your network?")
            if response == 'y':
                validResponse = True
            elif response =='n':
                print("script is exiting....\n")
                raise SystemExit
    elif accounts:
        validResponse = False
        while validResponse != True:
            print("\nWhich VIQ would you like to import the floor plan and APs too?")
            accounts_df = pd.DataFrame(accounts)
            count = 0
            for df_id, viq_info in accounts_df.iterrows():
                print(f"   {df_id}. {viq_info['name']}")
                count = df_id
            print(f"   {count+1}. {viqName} (This is Your main account)\n")
            selection = input(f"Please enter 0 - {count+1}: ")
            try:
                selection = int(selection)
            except:
                print("Please enter a valid response!!")
                continue
            if 0 <= selection <= count+1:
                validResponse = True
                if selection != count+1:
                    newViqID = (accounts_df.loc[int(selection),'id'])
                    newViqName = (accounts_df.loc[int(selection),'name'])
                    x.switchAccount(newViqID, newViqName)

default_filename = "device_list.csv"
filename = input(f'Please enter csv filename including "CSV" extension [default: {default_filename} <- press enter]: ').strip()
if not filename:
    filename = default_filename

else:
    filename = filename.replace("\\ ", " ")
    filename = filename.replace("'", "")  
    if os.path.isabs(filename):
        file_path = os.path.dirname(filename)  # e.g., '/path/to' from '/path/to/myfile.csv'
        base_filename = os.path.basename(filename)  # e.g., 'myfile.csv' from '/path/to/myfile.csv'
        print(f"Detected full path: {filename}")
    else:
        base_filename = filename  # Use as-is if relative/no path

try:
    csv_df = pd.read_csv(filename,dtype=str).fillna({'Serial Number': np.nan})
except FileNotFoundError:
    print(f"file {filename} was not found.")
    print("Script is exiting....")
    raise SystemExit      
 
print(f"Found {len(csv_df.index)} Serial numbers in CSV")
device_data = x.collectDevices(pageSize)

device_df = pd.DataFrame(device_data)
device_df.set_index('id',inplace=True)

device_list = []
for serial in csv_df['Serial Numbers']:
    device_id = device_df.index[device_df['serial_number'] == serial].tolist()
    if device_id:
        if len(device_id) > 1:
            logger.warning(f"multiple devices found with {serial}")
        elif len(device_id) == 0:
            logger.warning(f"No devices found with {serial}")
        else:
            device_list.append(device_id[0])
            filt = csv_df['Serial Numbers'] == serial
            csv_df.loc[filt,'Device Id'] = device_id[0]
    else:
        logger.warning(f"No devices found with {serial}")

print(f"Found {len(device_list)} device IDs that match the CSV serial numbers.")

# Clean the column in-place (modifies the original DataFrame)
csv_df['Cloud Config Group'] = csv_df['Cloud Config Group'].astype(str).str.strip()
# Extract the unique values
csv_ccgs = csv_df['Cloud Config Group'].unique().tolist()

ccg_data = x.collectCCG(pageSize)

ccg_df = pd.DataFrame(ccg_data)
ccg_df.set_index('id',inplace=True)

for ccg_name in csv_ccgs:
    if ccg_name not in ccg_df['name'].tolist():
        logger.warning(f"CCG {ccg_name} was not found in XIQ!")
        logger.info("Skipping CCG")
        continue
    filt = ccg_df['name'] == ccg_name
    ccg_device_list = ccg_df.loc[filt,'device_ids'].values[0]
    ccg_id = ccg_df.loc[filt].index.values[0]
    filt = csv_df['Cloud Config Group'] == ccg_name
    csv_device_list = csv_df.loc[filt,'Device Id'].dropna().tolist()
    update_device_list = list(set(ccg_device_list + csv_device_list))

    payload = {
        "name": ccg_df.loc[ccg_id,'name'],
        "description": ccg_df.loc[ccg_id,'description'],
        "device_ids": update_device_list
    }

    #print(payload)
    response = x.updateCCG(str(ccg_id), payload)
    if response.status_code != 200:
        log_msg = (f"Failed to set {ccg_name}\n  ")
        logger.error(log_msg)
        logger.error(response.text)
    else:
        logger.info(f"Successfully set CCG {ccg_name}")
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Unable to parse json data - HTTP Status Code: {str(response.status_code)}")
            raise ValueError("Unable to parse the data from json, script cannot proceed")
        logger.info(data)
