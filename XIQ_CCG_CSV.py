#!/usr/bin/env python3
import logging
import os
import json
import inspect
import pandas as pd
from pprint import pprint as pp
from app.logger import logger
from app.xiq_api import XIQ
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
logger = logging.getLogger('Serial-CCG.Main')

XIQ_API_token = ''

pageSize = 100

PATH = current_dir

csv_df = pd.DataFrame(columns = ['serialNumbers', 'cloudConfigGroup','device_ids'])
for filename in os.listdir(PATH+'/csv'):
    temp_df = pd.read_csv(PATH+'/csv/'+filename,dtype=str)
    csv_df = pd.concat([csv_df, temp_df], ignore_index=True)

print(f"Found {len(csv_df.index)} Serial numbers in CSV")
x = XIQ(token=XIQ_API_token)

device_data = x.collectDevices(pageSize)

device_df = pd.DataFrame(device_data)
device_df.set_index('id',inplace=True)

device_list = []
for serial in csv_df['serialNumbers']:
    device_id = device_df.index[device_df['serial_number'] == serial].tolist()
    if device_id:
        if len(device_id) > 1:
            logger.warning(f"multiple devices found with {serial}")
        elif len(device_id) == 0:
            logger.warning(f"No devices found with {serial}")
        else:
            device_list.append(device_id[0])
            filt = csv_df['serialNumbers'] == serial
            csv_df.loc[filt,'device_ids'] = device_id[0]
    else:
        logger.warning(f"No devices found with {serial}")

print(f"Found {len(device_list)} device IDs that match the CSV serial numbers.")

csv_ccgs = csv_df['cloudConfigGroup'].unique().tolist()

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
    filt = csv_df['cloudConfigGroup'] == ccg_name
    csv_device_list = csv_df.loc[filt,'device_ids'].dropna().tolist()
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
