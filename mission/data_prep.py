import traceback
from os import listdir
from os.path import join
from datetime import datetime, timedelta
from shutil import copyfile
import pandas as pd


def gen_execute_sheets(data_dir, out_dir, state_code_list, prev_res_dir=None, percent=20, max_num=250):
    """
    Generate execution plan (batch data sheets) per state

    Args:
        data_dir (str): Path to data sheets (CSV formatted Tableau sheets)

        out_dir (str): Path to store batched CSV files

        state_code_list (list[str]): State codes that needs processing

        prev_res_dir (str): Path to previously processed school lists

        percent (int, default=20): How many records you want to process in percentage

        max_num (int, default=250): How many records in each batch
    """
    for state in state_code_list:  # iterate states of interest
        prev_res_csv = None
        if prev_res_dir is not None:
            # import previously processed schools
            prev_res_csv = pd.read_csv(join(prev_res_dir, state+'_mission_result.csv'))
            print('{} State, {} Schools processed already'.format(state, len(prev_res_csv)))
        # use Tableau sheets (NCES sheets are larger and unnecessary)
        sch_csv = pd.read_csv(join(data_dir, state+'_Schools_Tableau.csv'))
        print('{} State, Total {} Schools'.format(state, len(sch_csv)))

        sch_name_url = sch_csv[['SCH_NAME', 'WEBSITE']]  # extract school names & homepage URLs
        sch_name_flt = sch_name_url.copy()
        if prev_res_dir is not None and prev_res_csv is not None:
            for row in prev_res_csv.itertuples():
                try:
                    # find matching record between the current row in
                    # previously processed school dataframe versus to-be-processed dataframe
                    # and retrieve indexes so that it could be dropped
                    index_matches = sch_name_flt[(sch_name_flt['SCH_NAME'] == row.SCH_NAME) &
                                                 (sch_name_flt['WEBSITE'] == row.WEBSITE)].index
                except IndexError:  # no match found
                    continue  # continue to next row
                sch_name_flt.drop(index_matches, inplace=True)

        # calculate required number of record based on percentage
        req_num = round(len(sch_name_flt) * percent / 100)
        print('{} State, {} Schools needs processing, and {} Required'.format(state, len(sch_name_flt), req_num))
        # generate batch sheets based on req_num and max_num
        if req_num <= max_num:
            sch_name_flt[:req_num+1].to_csv(join(out_dir, state+'_list.csv'), index=False)
        else:
            for i in range((req_num//max_num)+1):
                if req_num >= max_num*(i+1):
                    temp_df = sch_name_flt[max_num*i:max_num*(i+1)]
                else:
                    temp_df = sch_name_flt[max_num*i:req_num+1]
                temp_df.to_csv(join(out_dir, state + '_list_' + str(i) + '.csv'), index=False)


def gen_final_results(data_dir, out_dir):
    """
    Combine split results into one single file for each state

    Args:
        data_dir (str): Path to data sheets (CSV formatted mission result sheets)

        out_dir (str): Path to store result file for each state
    """
    result_files_dic = {}
    for filename in listdir(data_dir):
        if ('Result' not in filename) or (not filename.endswith('.csv')):
            continue
        if filename[:2] in result_files_dic:
            result_files_dic[filename[:2]].append(filename)
        else:
            result_files_dic[filename[:2]] = [filename]

    for state, result_files in result_files_dic.items():
        if len(result_files) == 1:
            copyfile(join(data_dir, result_files[0]), join(out_dir, result_files[0][:2]+'_mission_result.csv'))
        else:
            try:
                state_combined_result = \
                    pd.concat([pd.read_csv(join(data_dir, f)) for f in result_files], ignore_index=True)
                print('{} - Total schools: {}'.format(state, len(state_combined_result)))
                state_combined_result.to_csv(join(out_dir, state + '_mission_result.csv'), index=False)
            except ValueError:
                print("ERROR: Check the result files list: {}".format(result_files))
                traceback.print_exc()


def gen_final_etas(log_dir):
    """
    Process runtime log files to capture elapsed time

    Args:
        log_dir (str): Path to runtime logs
    """
    log_files_dic = {}
    for filename in listdir(log_dir):
        if (not filename.startswith('run_')) or (not filename.endswith('.log')):
            continue
        if filename[4:6] in log_files_dic:
            log_files_dic[filename[4:6]].append(filename)
        else:
            log_files_dic[filename[4:6]] = [filename]

    for state, log_files in log_files_dic.items():
        elapsed_time_list = []
        for log_file in log_files:
            with open(join(log_dir, log_file), 'r') as rf:
                for line in rf:
                    if 'Elapsed Time:' in line:
                        rec_list = line.strip('\n').split(' ')
                        rec_time = None
                        for idx in range(len(rec_list)):
                            try:
                                rec_time = datetime.strptime(rec_list[len(rec_list)-1-idx], '%H:%M:%S.%f')
                                break
                            except ValueError:
                                continue
                        if rec_time is None:
                            continue
                        day_idx = None
                        for idx in range(len(rec_list)):
                            if 'day' in rec_list[idx]:
                                day_idx = idx
                        if day_idx is not None:
                            day_num = int(rec_list[day_idx-1])
                            rec_time = rec_time + timedelta(hours=24*day_num)
                        # print('{} line - {}'.format(line.strip('\n'), rec_time))
                        # elapsed_time_list.append(rec_time.strftime('%H:%M:%S.%f'))
                        elapsed_time_list.append(rec_time)
        elapsed_time_list.sort(reverse=True)
        # print('{} state - {}'.format(state, elapsed_time_list))

        with open(join(log_dir, 'elapsed_time_log.csv'), 'a') as wf:
            wf.write(state + ',' + elapsed_time_list[0].strftime('%d:%H:%M:%S.%f') + '\n')


def add_mission_stmt_tableau(mission_dir, tableau_dir, tableau_file='US_Schools_Tableau.csv'):
    """
    Add mission statement result data to existing tableau sheet

    Args:
        mission_dir (str): Path to mission statement CSV sheets

        tableau_dir (str): Path to tableau CSV sheet

        tableau_file (str, default='US_Schools_Tableau.csv'): US level tableau CSV sheet
    """
    # import mission data
    mission_csv_df_list = []
    for mission_file in listdir(mission_dir):  # iterate per-state mission statement results
        if not mission_file.endswith('.csv'):
            continue

        mission_csv_df = pd.read_csv(join(mission_dir, mission_file))
        state_abbr_list = [mission_file[:2] for i in range(len(mission_csv_df))]
        mission_csv_df['LSTATE'] = state_abbr_list  # add state code column to prep for combining all results

        mission_csv_df_list.append(mission_csv_df)
    total_mission_csv_df = pd.concat(mission_csv_df_list, ignore_index=True)  # combine all states into one dataframe

    # import existing US level tableau data
    tableau_csv_df = pd.read_csv(join(tableau_dir, tableau_file))
    mission_list = ['' for i in range(len(tableau_csv_df))]
    tableau_csv_df['MISSION'] = mission_list  # create empty 'MISSION' column for tableau data
    for row in tableau_csv_df.itertuples():
        try:
            # find matching record between the current row in
            # tableau sheet versus combined mission statement result sheet
            # and get index of the row in combined mission statement result sheet
            mission_idx = total_mission_csv_df[(total_mission_csv_df['SCH_NAME'] == row.SCH_NAME) &
                                               (total_mission_csv_df['LSTATE'] == row.LSTATE) &
                                               (total_mission_csv_df['WEBSITE'] == row.WEBSITE)].index[0]
        except IndexError:  # no match found
            # traceback.print_exc()
            # print("row info: {}".format(row.SCH_NAME, row.LSTATE, row.WEBSITE))
            # print("match slice: {}".format(total_mission_csv_df[(total_mission_csv_df['SCH_NAME'] == row.SCH_NAME) &
            #                                                     (total_mission_csv_df['LSTATE'] == row.LSTATE) &
            #                                                     (total_mission_csv_df['WEBSITE'] == row.WEBSITE)]))
            continue  # continue to next row in tableau sheet
        try:
            # replace empty 'MISSION' column value of the current row in tableau sheet with
            # mission statement from the matched record in mission statement result sheet
            tableau_csv_df.at[row.Index, 'MISSION'] = total_mission_csv_df.at[mission_idx, 'MISSION']
            # print("mission stmt: {}".format(total_mission_csv_df.iloc[mission_idx]))
            # print("tableau record: {}".format(tableau_csv_df.iloc[row.Index]))
        except KeyError:
            traceback.print_exc()
            print("mission stmt: {}".format(total_mission_csv_df.iloc[mission_idx]))
            print("tableau record: {}".format(tableau_csv_df.iloc[row.Index]))
            exit(-1)
        except ValueError:
            traceback.print_exc()
            tableau_csv_df['MISSION'] = tableau_csv_df['MISSION'].astype(str)
            tableau_csv_df.at[row.Index, 'MISSION'] = total_mission_csv_df[mission_idx, 'MISSION']

    tableau_csv_df.to_csv(join(tableau_dir, tableau_file[:-4]+'_w_Mission.csv'), index=False)  # write to file


if __name__ == '__main__':
    # uncomment desired function call and replace parameter(s)
    # according to each function's description
    # each function may be called from outside
    # state_codes = [
    #     'AK', 'AL', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS',
    #     'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NM', 'NV',
    #     'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    state_codes = ['TX']
    gen_execute_sheets('/Users/jhp/Projects/MSU/schooltext/data/Final',
                       '/Users/jhp/Projects/MSU/schooltext/mission/school_list', state_codes,
                       prev_res_dir='/Users/jhp/Projects/MSU/schooltext/mission/result/final', percent=100)
    # gen_final_results('/Users/jhp/Projects/MSU/schooltext/mission/result',
    #                   '/Users/jhp/Projects/MSU/schooltext/mission/result/final')
    # gen_final_etas('/Users/jhp/Projects/MSU/schooltext/mission/result/logs')
    # add_mission_stmt_tableau('/Users/jhp/Projects/MSU/schooltext/mission/result/final',
    #                          '/Users/jhp/Projects/MSU/schooltext/data/Final')
