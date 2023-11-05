import numpy as np
import os
import pandas as pd

from wamo_util import *

pd.set_option('display.unicode.east_asian_width', True)

file_array = search_send_mpc(os.getcwd())
combined_obs = ''
for file_path in file_array:
    combined_obs += extract_obs(file_path)

combined_obs = combined_obs.replace('\n\n', '\n')
personal_obs = [line for line in combined_obs.split('\n') if len(line) >= 6 and line[5] == 'H']
sorted_personal_obs = sorted(personal_obs, key=lambda x: (x[:12], x[14:]))
provisional_obs = [line for line in combined_obs.split('\n') if len(line) >= 6 and line[5] != 'H' and line[5] != ' ']
sorted_provisional_obs = sorted(provisional_obs, key=lambda x: (x[:12], x[14:]))
numbered_obs = [line for line in combined_obs.split('\n') if len(line) >= 5 and line[0] != ' ']
sorted_numbered_obs = sorted(numbered_obs, key=lambda x: (x[:5], x[14:]))

sorted_personal_obs_arr = np.array(sorted_personal_obs)
sorted_personal_obs_solos = sorted_personal_obs_arr[np.char.find(sorted_personal_obs_arr, '*') >= 0]

unique_set = set()
sorted_personal_obs_solos_unique = []
for obs in sorted_personal_obs_solos:
    if obs[:12] not in unique_set:
        unique_set.add(obs[:12])
        sorted_personal_obs_solos_unique.append(obs)

candidate_df = pd.DataFrame(wamo_request_batch(sorted_personal_obs_solos_unique))

candidate_df['original_desig'] = [ob[5:13] for ob in sorted_personal_obs_solos_unique]
candidate_P_df = candidate_df[candidate_df.status == 'P'].sort_values('iau_desig').copy()
candidate_P_df = add_asterisk_column_to_result_df(candidate_P_df)
candidate_P_df = add_designation_type_column_to_result_df(candidate_P_df)
candidate_P_provisional_df = candidate_P_df[candidate_P_df['designation_type'] == 'provisional']
candidate_P_numbered_df = candidate_P_df[candidate_P_df['designation_type'] == 'numbered']

candidate_p_df = candidate_df[candidate_df.status == 'p'].sort_values('iau_desig').copy()
candidate_p_df = add_asterisk_column_to_result_df(candidate_p_df)
candidate_p_df = add_designation_type_column_to_result_df(candidate_p_df)
candidate_p_provisional_df = candidate_p_df[candidate_p_df['designation_type'] == 'provisional']
candidate_p_numbered_df = candidate_p_df[candidate_p_df['designation_type'] == 'numbered']

candidate_I_df = candidate_df[candidate_df.status == 'I'].copy()

obs_by_types_arr = np.array([sorted_personal_obs, sorted_provisional_obs, sorted_numbered_obs], dtype=object)
print('')
print('【全体統計】')
print(pd.DataFrame({
    'カテゴリ': ['新天体候補', '仮符号天体', '確定番号天体'],
    '観測数': np.vectorize(len)(obs_by_types_arr),
    '天体数': np.vectorize(count_uniques)(obs_by_types_arr),
}))

candidate_categories = [
  'Isolated Tracklet File (ITF)',
  '仮符号（アスタリスク付）',
  '仮符号（アスタリスクなし）',
  '確定番号（アスタリスク付）',
  '確定番号（アスタリスクなし）'
]
unpublished_results_count = [
  len(candidate_I_df),
  count_asterisk_in_df(candidate_p_provisional_df)['True'],
  count_asterisk_in_df(candidate_p_provisional_df)['False'],
  count_asterisk_in_df(candidate_p_numbered_df)['True'],
  count_asterisk_in_df(candidate_p_numbered_df)['False']
]
published_results_count = [
  0,
  count_asterisk_in_df(candidate_P_provisional_df)['True'],
  count_asterisk_in_df(candidate_P_provisional_df)['False'],
  count_asterisk_in_df(candidate_P_numbered_df)['True'],
  count_asterisk_in_df(candidate_P_numbered_df)['False']
]

print('')
print('【新天体候補の統計】')
print(pd.DataFrame({
    'カテゴリ': candidate_categories,
    '公開前': unpublished_results_count,
    '公開済': published_results_count,
}))


if len(candidate_P_df[candidate_P_df['asterisk']]):
    print('')
    print('【アスタリスク付天体の詳細（公開済）】')
    print(candidate_P_df[candidate_P_df['asterisk']][['original_desig', 'iau_desig', 'ref', 'submission_id']])


if len(candidate_p_df[candidate_p_df['asterisk']]):
    print('')
    print('【アスタリスク付天体の詳細（公開前）】')
    print(candidate_p_df[candidate_p_df['asterisk']][['original_desig', 'iau_desig', 'ref', 'submission_id']])
