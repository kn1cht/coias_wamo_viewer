import numpy as np
import os
import pandas as pd
import requests

WAMO_URL = "https://data.minorplanetcenter.net/api/wamo"

def search_send_mpc(directory):
    print('gathering files...')
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt") and file.startswith("send_mpc"):
                file_list.append(os.path.join(root, file))
    print(f'found {len(file_list)}')
    return file_list

def extract_obs(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        start_index = next((index for index, line in enumerate(lines) if line == 'ACK Subaru/HSC\n'), None)
        if start_index is not None:
            return ''.join(lines[start_index+1:])
        else:
            return ''

count_uniques = lambda obs_arr: len(set(obs[:12] for obs in obs_arr))

def wamo_request_batch(obs_list, batch_size=100):
    found_results = []
    not_found_results = []
    for i in range(0, len(obs_list), batch_size):
        print(f'sending requests to WAMO: {i} to {min(i+batch_size-1, len(obs_list)-1)}')
        response = requests.get(WAMO_URL, json=list(obs_list)[i:i+batch_size])
        batch_results = response.json()
        found_results.extend(batch_results['found'])
        not_found_results.extend(batch_results['not_found'])

    print(f'WAMO request finished!\nfound {len(found_results)}\nnot found {len(not_found_results)}')
    return [list(dictionary.values())[0][0] for dictionary in found_results]

def count_asterisk_in_df(df):
  ret = {'True' : 0, 'False' : 0}
  value_counts = df['asterisk'].value_counts()
  if False in value_counts.keys(): ret['False'] = value_counts[False]
  if True in value_counts.keys(): ret['True'] = value_counts[True]
  return(ret)

def add_asterisk_column_to_result_df(df):
    df.loc[:,['asterisk']] = np.char.find(df['obs80'].to_numpy().astype(str), '*') >= 0
    return df

def add_designation_type_column_to_result_df(df):
    df['designation_type'] = np.nan
    df.loc[df['iau_desig'].str.contains('[A-Za-z]'), 'designation_type'] = 'provisional'
    df.loc[df['iau_desig'].str.isnumeric(), 'designation_type'] = 'numbered'
    return df
