import pandas as pd
from datetime import datetime, timedelta, time

DATA = pd.read_csv("datasets/dsa_data.csv")
CLB_OPENING = "09:00:00"
CLB_CLOSING = "20:59:00"
MAX_SECONDS_IN_LIBRARY = 86400 #24hours

def basic_cleaning(df: pd.DataFrame):
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Singapore').astype(str)
    df['Datetime'] = df['Datetime'].astype(str)
    df[['Date','Time']] = df.Datetime.str.split(" ", expand = True)
    df['Time'] = df['Time'].apply(lambda x: x.replace('+08:00','')) 

    df.dropna(subset = ['User Number'], inplace = True)
    df = df[-df['Broad Category'].isin(['Administrative Staff','Complimentary','Corporate Card',
                                        'External Members', 'External Members/Alumni', 'Non-Academic Staff',
                                        'Research Staff', 'Teaching Staff', 'Library Professional']) == True]
    return df

#---For specific data---
def get_outlier_records(df: pd.DataFrame):
    """
    Extracts entry and exit pairs that have mismatched dates and entry or exit records that dont have their corresponding pairs

    Args:
        Cleaned dataframe with all records
    Returns: 
        dataframe containing mismatched entry and exit pairs 
    """
    current_date = 0
    current_user = df.iloc[0]["User Number"]
    prev = 'Exit'
    outlier = pd.DataFrame()
    for index, row in df.iterrows():
        if row['User Number'] == current_user:
            if row['Direction'] != prev:
                if row['Direction'] == "Entry":
                    current_date = row["Date"]
                else:
                    if row['Date'] != current_date:
                        outlier = outlier.append(df.iloc[index-1])
                        outlier = outlier.append(df.iloc[index])
                prev = row['Direction']
            else:
                outlier = outlier.append(df.iloc[index])
        else:
            if row['Direction'] != "Entry":
                outlier = outlier.append(df.iloc[index])
                if prev == "Entry":
                    outlier = outlier.append(df.iloc[index-1])
            else:
                current_date = row["Date"]
                current_user = row['User Number']
                prev = "Entry"
    return outlier

def fix_outlier_records(outlier: pd.DataFrame):
    """
    Manually adds in tap in or tap out records for current entry and exit pairs with mismatched days
    Assumption: If records does not show tap in, assume user enters when library opens, vice versa.

    Args:  
        dfframe of mismatched entry and exit pairs

    Returns:
        dfframe with additional entry and exit records to fix mismatched pairs
    """
    outlier_solution = pd.DataFrame()
    for index, row in outlier.iterrows():
        if row["Direction"] == 'Entry':
            new_row = row.to_dict()
            new_row['Direction'] = 'Exit'
            new_row['Time'] = CLB_CLOSING
            outlier_solution = outlier_solution.append(new_row, ignore_index = True)
        else:
            new_row = row.to_dict()
            new_row['Direction'] = 'Entry'
            new_row['Time'] = CLB_OPENING
            outlier_solution = outlier_solution.append(new_row, ignore_index = True)
    return outlier_solution

#---For entry/exit labels---
def assign_entry_exit(data: pd.DataFrame):
    """
    Takes in entry/exit labelled records and labels them entry or exit based on each user(assume first is entry then alternate)
    
    Args:
        Dataframe of entry/exit labelled records
    
    Returns:
        Dataframe that is labelled with entry or exit labels
    """
    current_user = data.iloc[0]['User Number'] 
    is_entry = True
    solution = pd.DataFrame()
    for index, row in data.iterrows():
        if row["User Number"] == current_user:
            new_row = row.to_dict()   
            if is_entry == True:
                new_row['Direction'] = 'Entry'
                is_entry = False
            else:
                new_row['Direction'] = 'Exit'
                is_entry = True
            solution = solution.append(new_row, ignore_index = True)
        else:
            new_row = row.to_dict()
            new_row['Direction'] = 'Entry'
            solution = solution.append(new_row, ignore_index = True)
            is_entry = False
            current_user = new_row['User Number']
    return solution
        
def get_outlier_records_random(data: pd.DataFrame):
    """
    Extracts all outlier records from df_random i.e. entry records without exits / extry and exit pairs with time diff > 24hours

    Args:
        Dataframe of entry/exit that is fixed

    Returns:
        All outlier records from input df
    """
    before = 'exit'
    current_time = 0
    outlier = pd.DataFrame()
    for index, row in data.iterrows():
        if row['Direction'] == 'Entry':
            if before != 'exit':
                outlier = outlier.append(data.iloc[index-1])
            current_time = datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S') 
            before = 'entry'
        else:
            if (datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S') - current_time).total_seconds() > MAX_SECONDS_IN_LIBRARY:
                outlier = outlier.append(data.iloc[index-1])
                outlier = outlier.append(data.iloc[index])
            before = 'exit'
    if data.iloc[-1]['Direction'] == "Entry": #if last row is entry so must add in exit for it
        outlier = outlier.append(data.iloc[-1])
    return outlier

def fix_outlier_random(outlier: pd.DataFrame):
    """
    Manually adds in tap in or tap out records for current entry and exit pairs with mismatched days
    Assumption: If records does not show tap in, assume user enters when library opens, vice versa.

    Args:  
        dfframe of mismatched entry and exit pairs

    Returns:
        dfframe with additional entry and exit records to fix mismatched pairs
    """
    outlier_solution = pd.DataFrame()
    for index, row in outlier.iterrows():
        if row["Direction"] == 'Entry':
            new_row = row.to_dict()
            new_row['Direction'] = 'Exit'
            new_row['Datetime'] = datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S') + timedelta(hours=12)
            outlier_solution = outlier_solution.append(new_row, ignore_index = True)
        else:
            new_row = row.to_dict()
            new_row['Direction'] = 'Entry'
            new_row['Datetime'] = datetime.strptime(str(row['Datetime']), '%Y-%m-%d %H:%M:%S') - timedelta(hours=12)
            outlier_solution = outlier_solution.append(new_row, ignore_index = True)
    output = pd.concat([outlier, outlier_solution]).reset_index(drop=True)
    output['Datetime'] = output['Datetime'].astype(str)
    output[['Date','Time']] = output.Datetime.str.split(" ", expand = True)
    return output.drop_duplicates(subset=['User Number','Date','Time']).sort_values(by=['User Number', 'Date', 'Time']).reset_index(drop=True)

def final_clean(data: pd.DataFrame):
    """
    Final check to ensure that all entry and exits make sense. Catch outliers after combining the two clean dataframes 
    Assumptions: Due to uncertainty tap in/out, assume that timings recorded are correct and every record must alternate for each user

    Args:
        Merged dataframe of clean_specific and clean_random

    Returns:
        Cleaned dataframe
    """
    prev = 'exit'
    for index, row in data.iterrows():
        if row['Direction'] == 'Entry':
            if prev != 'exit':
                data.loc[index,'Direction'] = "Exit"
                prev = 'exit'
            else:
                prev = 'entry'
        else:
            if prev != 'entry':
                data.loc[index,'Direction'] = "Entry"
                prev = 'entry'
            else:
                prev = 'exit'
    return data

def main():
    #clean data for records that have specific "Entry" or "Exit" labels
    df = basic_cleaning(DATA)
    df_specific = df[df['Direction'].isin(['Entry','Exit']) == True]
    df_specific = df_specific.sort_values(by=['User Number','Datetime'])
    df_specific['Direction_lead'] = df_specific['Direction'].shift(-1)
    df_specific['Direction_lag'] = df_specific['Direction'].shift(1)
    df_specific = df_specific[((df_specific['Direction'] == 'Entry') & (df_specific['Direction_lead'] != 'Entry') == True) |
            ((df_specific['Direction'] == 'Exit') & (df_specific['Direction_lag'] != 'Exit') == True) ].reset_index(drop=True)

    outlier = get_outlier_records(df_specific).reset_index(drop = True)

    outlier_solution = fix_outlier_records(outlier)
    
    clean_specific = pd.concat([df_specific,outlier,outlier_solution]).drop(columns=['Direction_lead','Direction_lag']).sort_values(by = ['User Number', 'Date', 'Time']).drop_duplicates().reset_index(drop = True)
    


    #clean data for records that have ambiguous label "Entry/Exit"
    df2 = basic_cleaning(DATA)
    df_random = df2[df2['Direction'].isin(['Entry/Exit']) == True]
    df_random = df_random.sort_values(by=['User Number','Datetime']).reset_index()
    df_random['Datetime'] = df_random['Datetime'].apply(lambda x: x.replace('+08:00',''))


    df_random = assign_entry_exit(df_random).drop(columns=['index']).reset_index(drop=True)

    outlier_random = get_outlier_records_random(df_random)

    outlier_solution_random = fix_outlier_random(outlier_random)

    clean_random = pd.concat([df_random,outlier_solution_random])
    clean_random = clean_random.reset_index(drop=True).drop_duplicates(subset=['User Number','Date','Time']).sort_values(by = ['User Number', 'Date', 'Time']).reset_index(drop=True)
    
    #combine both types of records into a single dataframe and perform a final round of cleaning to ensure data is logical
    clean_df = pd.concat([clean_specific,clean_random]).sort_values(by = ['User Number', 'Date', 'Time']).reset_index(drop=True)
    clean_df = final_clean(clean_df).reset_index(drop=True)

    #split cleaned data into entry and exit records (seperate dataframes)
    clean_entry = clean_df.iloc[0::2].drop(columns=['Datetime',
                                                    'Broad Category',
                                                    'Library', 
                                                    'User Number',
                                                    'Method']).reset_index(drop=True) 
                                                                                                                                             
    clean_exit = clean_df.iloc[1::2].drop(columns=['Datetime',
                                                    'Broad Category',
                                                    'Library',                                                                                      
                                                    'User Number',                                                                                   
                                                    'Method']).reset_index(drop=True)
    
    #add a column for datetime to plot the graph and to calculate average occupancy
    clean_entry["Datetime"] = pd.to_datetime(clean_entry["Date"].astype(str) + " " +  clean_entry["Time"].astype(str))
    clean_exit["Datetime"] = pd.to_datetime(clean_exit["Date"].astype(str) + " " + clean_exit["Time"].astype(str))
    
    #concat entry and exit data to one dataframe with columns [Direction,Datetime,Date]
    clean_df = pd.concat([clean_entry,clean_exit],ignore_index=True)
    clean_df = clean_df.sort_values(by = "Datetime")
    clean_df = clean_df[["Direction", "Datetime","Date"]]
    clean_df["Date"] = pd.to_datetime(clean_df["Date"])
    clean_df.to_csv("datasets/clean_df.csv")

if __name__ == '__main__':
    main()