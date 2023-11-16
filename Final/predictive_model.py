#!/usr/bin/env python3

import pandas as pd
import numpy as np
import math
import os
import pandas as pd
import sshtunnel
from sshtunnel import SSHTunnelForwarder
import mysql.connector

def connect_database_download_data():
  """
  Connect to the database and download cleaned data 
  """
  config_path = './config.sh'
  config_vars = {}

  with open(config_path, 'r') as file:
    for line in file:
      if line.startswith('#') or '=' not in line:
          continue
      key, value = line.split('=', 1)
      key = key.strip()
      value = value.strip().strip("'").strip('"')
      config_vars[key] = value

  ssh_host = config_vars['SSH_HOST']
  ssh_username = config_vars['SSH_USER']
  ssh_key_path = config_vars['SSH_KEY_PATH']
  mysql_host = config_vars['HOST']
  mysql_user = config_vars['USER']
  mysql_password = config_vars['PASSWORD']
  mysql_db = config_vars['DATABASE']
  local_bind_port = 5000
  mysql_port = 3306
  remote_bind_port = mysql_port
  try:
    tunnel = SSHTunnelForwarder(
      (ssh_host, 22),
      ssh_username=ssh_username,
      ssh_private_key=ssh_key_path,
      remote_bind_address=(mysql_host, remote_bind_port),
      local_bind_address=('127.0.0.1', local_bind_port)
    )
    tunnel.start()
  except Exception as e:
    exit(1)

  try:
    connection = mysql.connector.connect(
      user=mysql_user,
      password=mysql_password,
      host='127.0.0.1',
      port=local_bind_port, 
      database=mysql_db,
      use_pure=True
    )

    if connection.is_connected():
      cursor = connection.cursor()
      sample_query = "SELECT * FROM LibraryRecords;"
      cursor.execute(sample_query)
      result = cursor.fetchall()
      df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
      cursor.close()
  except mysql.connector.Error:
      pass
  finally:
      if 'connection' in locals() or 'connection' in globals() and connection.is_connected():
        connection.close()
      tunnel.stop()
  return df

#to see the no of ppl in library at a given hour
def add_occupancy(data):
  """
  Adds in number of people in the library at a given hour

  Args:
      the merged entry and exit data

  Returns:
      dataframe containing the direction,datetime,date and occupancy columns
  """
  data["Datetime"] = pd.to_datetime(data["Datetime"])
  data["Date"] = pd.to_datetime(data["Date"])
  data = data.copy()
  data = data.sort_values(by=["Datetime"],ignore_index = True)
  data["occupancy"] = list(np.zeros(len(data)))
  # here i add the occupancy column to see the number of ppl in the library at a certain hour 
  for i in range(len(data)):
    if i == 0: #first entry
      data.iloc[0,-1] = 1 
    elif (data.loc[i,"Direction"] == "Entry"): # if entry, occupancy +1
      data.iloc[i,-1] = data.iloc[i-1,-1] + 1
    elif (data.loc[i,"Direction"] == "Exit"): # if entry, occupancy -1
      data.iloc[i,-1] = data.iloc[i-1,-1] -1
  return data


def segregrate_data(data):
  """
  Segregrate the datas to their respective Academic years

  Args:
      the cleaned data 

  Returns:
      a dictionary , where the keys are the academic years(i.e for AY22/23 its 2022) and the values are the filtered data  
  """
  output={}
  #tfor different academic year we have different way of calculating the difference of the week and the starting date of the ay, read the function below(getRecessWeekData) to understand why its important
  for year,endingdate in AYendingdate.items():
    temp = data[(data["Date"] <= endingdate) & (AYstartingdate[year]<=data["Date"])]
    if not(temp.empty):
      output[year] = temp
  return output

def getRecessWeekData(data):
  """
  from the segregated data, further filter to only take those dates where it falls under Recess week, regardless of semester

  Args:
      the segregated data (a dictionary)

  Returns:
      a dataframe 
  """
  # to generalize the data for future input data..
  # the range here is pre-computed, i only consider the weeks where it is Recess week
  output = pd.DataFrame()
  for years,AYdata in data.items():
    #we are calculating the difference of weeks of that particular day and the starting date of the ay (since the starting week of the ay is always the first week of august, then from there we can tell what week this date is on)
    #the numbers here represent the difference of weeks between the starting/ending date of recess week and the first date of the ay (where i already pre-hand computed)
    #and since the two semester of the ay are 22 weeks apart, so we check if its either in sem1's recess week or in sem2's recess week and include it in
    temp = AYdata[((6.714285714285714 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < 8)) |
                  ((28.714285714285714 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < 30)) ]
    if not (temp.empty):
      output = pd.concat([output,temp],ignore_index = True)
  return output

# the same logic applies to all these below
def getNormalWeekData(data,week):
  """
  from the segregated data, further filter to only take those dates where it falls under normal week (i.e non recess/exam/reading), regardless of semester

  Args:
      the segregated data (a dictionary)

  Returns:
      a dataframe 
  """
  output = pd.DataFrame()
  for years,AYdata in data.items():
    temp = AYdata[((week <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < week + 0.7142857142857143)) |
                  ((week + 22 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < week + 22.7142857142857143)) ]
    if not (temp.empty):
      output = pd.concat([output,temp],ignore_index = True)
  # if we dont have data for that particular week, we will just use the baseline data.
  if output.empty:
    return BASELINE,True
  return output,False

def getReadingWeekData(data):
  """
  from the segregated data, further filter to only take those dates where it falls under reading week, regardless of semester

  Args:
      the segregated data (a dictionary)

  Returns:
      a dataframe
  """
  output = pd.DataFrame()
  for years, AYdata in data.items():
    temp = AYdata[((14.714285714285714 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < 15.714285714285714)) |
                  ((36.714285714285714 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < 37.714285714285714))]
    if not (temp.empty):
      output = pd.concat([output,temp],ignore_index = True)
  return output

def getExamWeekData(data):
  """
  from the segregated data, further filter to only take those dates where it falls under exam week, regardless of semester

  Args:
      the segregated data (a dictionary)

  Returns:
      a dataframe
  """
  output = pd.DataFrame()
  for years,AYdata in data.items():
    temp = AYdata[((15.714285714285714 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < 17.857142857142858))|
                  ((37.714285714285714 <= ((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AYstartingdate[years]) / np.timedelta64(1,'W')) < 39.857142857142858))]
    if not (temp.empty):
      output = pd.concat([output,temp],ignore_index = True)
  return output

#if we have no such data of the day of the week that we are interested in, the we will take the average of the whole week
def checkIfDataOfDayPresent(data,day):
  """
  from the further filtered data, filter to only take those dates where we are interested in. If we dont have data for such a day, select the whole week to take the average

  Args:
      the further filtered dataframe in their respective weeks data, the day that we are interested in (i.e. Monday)

  Returns:
      a dataframe 
  """
  data = data.copy()
  if data[data["Date"].dt.dayofweek == day - 1].empty:
    return data[data["Date"].dt.dayofweek <= 4]
  return data[data["Date"].dt.dayofweek == day - 1]

def create_category(data,max_occupancy):
  """
  from the levels/seat data gathered from the survey, in order to utilize the points system given, we need to split the occupancy into different categories to calculate the probability

  Args:
      data (either seats_survey or levels_survey) and the max occupancy for each level / whole library

  Returns:
      a dictionary consisting {level:{category:number of people}} 
      for example: {'3': {4: 54.75, 3: 109.5, 2: 164.25, 1: 219.0}, '4': {2: 153.0, 1: 306.0}, '5': {3: 161.0, 2: 322.0, 1: 483.0}, '6': {3: 127.66666666666667, 2: 255.33333333333334, 1: 383.0}, '6Chinese': {3: 53.333333333333336, 2: 106.66666666666667, 1: 160.0}}
  """
  #split the max capacity of library into 5 categories, 5. 0-200 people (very empty) | 4. 201-400 | 3. 401-600 | 2. 601-800 | 1. 801-1500 (library is full) (just an example)
  levels = data["level"].unique()
  preference = {}
  for level in levels:
    num_of_features = data[data["level"] == level]["preference"].max()
    cat = np.linspace(0,max_occupancy[level],num_of_features+1)[1:] # split the occupancy to different categories
    temp = {}
    for i in range(num_of_features,0,-1):
      temp[i] = cat[num_of_features - i]
    preference[level] = temp
  return preference

def calculate_occupancy_for_every_level(week,day,hour,occupancy,levels_survey_data):
  """
  for the given week, day, hour, we use the survey_data to calculate the distribution for each level and times a probability to it and
  getting the occupancy for every level

  Args:
    object,int,int,int,DataFrame
    levels_survey_data = cleaned data from the survey_data
    
  Returns:
    a dictionary {level:occupancy_for_that_level}
    for example: {'6Chinese': 160, '3': 214, '4': 286, '5': 269, '6': 273}
  """
  #so now lets assume at 5pm the library has a total of 357 people, it would fall into category 4 (from the function create_category). 
  # The level dist will be: lvl<x> = (v5[lvl<x>]+v4[lvl<x>])/sum(v5+v4) * no. of people
  #e.g lvl3 = (51+32)/[(51+46+53+48+37)+(32+77+45+62+30)] * 357 = 61 people on level 3
  output = {}
  levels_survey_data = levels_survey_data.copy()  
  preset_cat = create_category(levels_survey_data,MAX_OCCUPANCY_FOR_THE_LIBRARY)
  occupancy_category = {}
  for level,category_occupancy in preset_cat.items():
    for category,capacity in category_occupancy.items():
      if occupancy <= capacity:
        occupancy_category[level]= category
        break
  # to check if the timeframe interested in is within library opening hours. if it is only apply the probability thing, otherwise only level 6 is open, thus no meaning in calculating the probability
  if week in ["Reading","Exam"] :
    if 1<=day<=5: #weekday
      if hour > 21 or hour < 9: #library opens from 9am-9pm
        return {"6":occupancy}
    elif day == 6: #saturday
      if hour > 17 or hour < 10: #library opens from 10am-5pm
        return {"6":occupancy}
    elif day == 7: #library closes at sunday
      return {"6":occupancy}

  #everything below is to calculate the occupancy for each level
  occupancy_left = occupancy
  while len(output) != 5: #while we have not finished distributing the occupancy for every level
    temp={}
    maxUsed = False
    for level,max in MAX_OCCUPANCY_FOR_EACH_LEVEL.items():
      if level in output: # we have already added this in
        continue
      probability = levels_survey_data[(levels_survey_data["level"] == level) & (levels_survey_data["preference"] >= occupancy_category[level])]["value"].sum() / levels_survey_data[levels_survey_data["preference"] >= occupancy_category[level]]["value"].sum()
      current = math.ceil(occupancy_left*probability)
      if max <= current: #if the current occupancy is greater than the maximum capacity
        occupancy_left -= max
        output[level] = max #assign the maximum occupancy and assume that users will move to other levels
        levels_survey_data = levels_survey_data[levels_survey_data["level"] != level] #exclude that level's preference and calculate the distribution of the remaining levels all over again
        maxUsed = True
        break
      temp[level] = current #not over max capacity, can add into the final output
    if not maxUsed: #check if there is any violation
      output.update(temp)
  return output
     

def calculate_occupancy_for_each_seat_type(occupancy_for_each_level,seats_survey_data):
  """
  from the occupancy of every level, further distributed the occupancy for each seat_type

  Args:
    dictionary,dataframe
    seats_survey_data = cleaned data from the survey_data
    
  Returns:
    a dictionary {level:{seat_type:occupancy}}
    for example: 
    {'6Chinese': {'Windowed.Seats': 36, 'Diagonal.Seats': 72, 'Cubicle.seats': 52},
    '3': {'Discussion.Cubicles': 56, 'Soft.seats': 73, 'Moveable.seats': 70},
    '4': {'Sofa': 32, 'Soft.seats': 268},
    '5': {'Windowed.Seats': 97, 'X4.man.tables': 156, 'X8.man.tables': 112},
    '6': {'Diagonal.Seats': 91, 'Cubicle.seats': 87, 'Windowed.Seats': 93}}
  """
  #so now lets assume at 5pm the library has a total of 357 people at level 3, then 
  # The level dist will be: lvl<x> = (v5[lvl<x>]+v4[lvl<x>])/sum(v5+v4) * no. of people
  #e.g seat_type1 = (51+32)/[(51+46+53+48+37)+(32+77+45+62+30)] * 357 = 61 people on seat_type1, level 3
  output = {}
  seats_survey_data = seats_survey_data.copy()  
  preset_cat = create_category(seats_survey_data,MAX_OCCUPANCY_FOR_EACH_LEVEL)
  occupancy_category = {}
  for level, occupancy in occupancy_for_each_level.items():
    for category,capacity in preset_cat[level].items():
      if occupancy <= capacity:
        occupancy_category[level]= category
        break

  #essential the same method as calculate_occupancy_for_every_level()
  for level, occupancy in occupancy_for_each_level.items():
    output[level] = {}
    unique_seat_types = max_seat[max_seat["level"] == level]["seat_type"].unique()
    while len(output[level]) != len(unique_seat_types):
      temp = {}
      maxUsed = False
      occupancy_left = occupancy
      for seat_type in unique_seat_types:
        if seat_type in output[level]:
          continue
        probability = seats_survey_data[(seats_survey_data["level"] == level) & (seats_survey_data["seat_type"] == seat_type) & (seats_survey_data["preference"] >= occupancy_category[level])]["value"].sum() / seats_survey_data[(seats_survey_data["level"] == level) & (seats_survey_data["preference"] >= occupancy_category[level])]["value"].sum()
        current = math.ceil(occupancy_left*probability)
        max = max_seat[(max_seat["level"] == level) & (max_seat["seat_type"] == seat_type)]["count"].item()
        if (max <= current):
          occupancy_left -= max
          output[level][seat_type] = max
          seats_survey_data = seats_survey_data[(seats_survey_data["level"] != level) | (seats_survey_data["seat_type"] != seat_type)] # not (A and B) == not A or not B
          maxUsed = True
          break
        temp[seat_type] = current
      if not maxUsed:
        output[level].update(temp)
  return output

def predict_occupancy(week, day, hour, gates_data, levels_survey_data, seats_survey_data):
  """
  given the interested timeframe(week,day,hour) and level, we use the cleaned datas(gates_data,levels_survey_data,seats_survey_data) to calculate and output the all levels and types of seats average occupancy of the specific timeframe using historical data
  
  Args:
      object,int,int,DataFrame
        week = 1-13/Recess/Exam/Reading
        day = 1-5 for normal week(1-13)
              1-6 for Recess week
              1-7 for Exam/Reading week
        1:Monday ... 7:Sunday
        hour = 9-21 for normal week(1-13) and Recess week (weekday)
              10 - 17 for Recess week (weekend)
              1-24 for Exam/Reading week
        1: 0100hr 2: 0200hr ... 23: 2300hr 24: 0000hr
        level = 3/4/5/6/6Chinese
        levels_survey_data = cleaned floor data from survey
        seats_survey_data = cleaned seat_types data from survey
  Returns:
      an dictionary consisting the {level:{seat_type:occupancy}}
      for example:
      {'3': {'Discussion.Cubicles': 32, 'Soft.seats': 33, 'Moveable.seats': 20}, 
      '4': {'Sofa': 32, 'Soft.seats': 157}, 
      '5': {'Windowed.Seats': 85, 'X4.man.tables': 46, 'X8.man.tables': 29}, 
      '6': {'Diagonal.Seats': 48, 'Cubicle.seats': 49, 'Windowed.Seats': 45}, 
      '6Chinese': {'Diagonal.Seats': 34, 'Cubicle.seats': 35, 'Windowed.Seats': 32}}

  """
  gates_data = gates_data.copy()
  # since we have such limited data, i assume that the distribution of occupancy for the weeks are almost iid.. and as the weeks get closer to midterms/exam, the number of people in the library would increase
  # the factor here is to capture the reality that as it gets closer to exam/midterm, the total occupancy will increase
  factor = {1:0.95,2:0.97,3:1,4:1.03,5:1.05,6:1.1,7:1.1,8:1.05,9:1.06,10:1.06,11:1.18,12:1.2,13:1.3}
  temp = segregrate_data(gates_data)
  usedBaseline = False
  # here i split the weeks into different scenarios to access different weeks of data
  if week == "Recess": 
    gates_data = getRecessWeekData(temp)
  elif week == "Reading":
    gates_data = getReadingWeekData(temp)
  elif week == "Exam":
    gates_data = getExamWeekData(temp)
  elif 1<=week<=13:
    gates_data, usedBaseline = getNormalWeekData(temp,week)
  gates_data = checkIfDataOfDayPresent(gates_data,day)
  if usedBaseline: #baseline is used, then need to times a factor to consider the case when it gets closer to exam/midterm, the total occupancy will increase
    occupancy =  math.ceil(gates_data[gates_data["Datetime"].dt.hour == hour - 1].groupby(by=["Date"])["occupancy"].mean().mean() * factor[week])
  else:
    occupancy =  math.ceil(gates_data[gates_data["Datetime"].dt.hour == hour - 1].groupby(by=["Date"])["occupancy"].mean().mean())
  occupancy_for_each_level = calculate_occupancy_for_every_level(week,day,hour,occupancy,levels_survey_data)
  return calculate_occupancy_for_each_seat_type(occupancy_for_each_level,seats_survey_data)


def create_model_output(gates_data,levels_survey_data,seats_survey_data):
  """
  trying every possible combination of week,day,hour,level,seat_type in the predict_occupancy function as our model_output, where we will store this dataframe in mysql for fast access

  Args:
      the cleaned datas

  Returns:
      a dataframe 
  """
  seat_type_for_each_level ={}
  global levels
  for level in levels:
    seat_type_for_each_level[level] = max_seat[max_seat["level"] == level]["seat_type"].unique()
  model_output = {"week":[],"day" :[], "hour": [], "level":[], "seat_type":[],"occupancy" : []}
  #normal weeks
  for week in range(1,14): #week1-13
    for day in range(1,6): #monday to friday
      for hour in range(9,22): #9am to 9pm
        temp = predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)
        for level in levels:
          for seat_type in seat_type_for_each_level[level]:
            model_output["week"] = model_output["week"] + [week,]
            model_output["day"] = model_output["day"] + [day,]
            model_output["hour"] = model_output["hour"] + [hour,]
            model_output["level"] = model_output["level"] + [level,]
            model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
            model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]

  #recess week
  for week in ["Recess"]:
    for day in range(1,7): #monday to saturday
      if day ==6: 
        for hour in range(10,18): #10am to 5pm
          temp = predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)
          for level in levels:
            for seat_type in seat_type_for_each_level[level]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [hour,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
              model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]

      else:
        for hour in range(9,22): #9am to 9pm
          temp = predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)
          for level in levels:
            for seat_type in seat_type_for_each_level[level]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [hour,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
              model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]
  #reading/exam week
  for week in ["Reading","Exam"]:
    for day in range(1,8): #since the library 24/7, can allow the user to select monday to sunday
      if 1<=day<=5:
        for hour in range(1,25):
          temp = predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)
          if hour > 21 or hour < 9: #outside of library opening hours
            level = "6"
            for seat_type in seat_type_for_each_level[level]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [hour,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
              model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]
          else:
            for level in levels:
              for seat_type in seat_type_for_each_level[level]:
                model_output["week"] = model_output["week"] + [week,]
                model_output["day"] = model_output["day"] + [day,]
                model_output["hour"] = model_output["hour"] + [hour,]
                model_output["level"] = model_output["level"] + [level,]
                model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
                model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]
      elif day == 6:
        for hour in range(1,25): # 24 hours
          temp = predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)
          if hour > 17 or hour < 10: #outside of library opening hours
            level = "6"
            for seat_type in seat_type_for_each_level[level]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [hour,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
              model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]
          else:
            for level in levels:
              for seat_type in seat_type_for_each_level[level]:
                model_output["week"] = model_output["week"] + [week,]
                model_output["day"] = model_output["day"] + [day,]
                model_output["hour"] = model_output["hour"] + [hour,]
                model_output["level"] = model_output["level"] + [level,]
                model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
                model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]
      elif day == 7: #library closes on sunday
        for hour in range(1,25):
          temp = predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)
          level = "6"
          for seat_type in seat_type_for_each_level[level]:
            model_output["week"] = model_output["week"] + [week,]
            model_output["day"] = model_output["day"] + [day,]
            model_output["hour"] = model_output["hour"] + [hour,]
            model_output["level"] = model_output["level"] + [level,]
            model_output["seat_type"] = model_output["seat_type"] +[seat_type,]
            model_output["occupancy"] = model_output["occupancy"] + [temp[level][seat_type],]
  return pd.DataFrame(model_output)

#reading in all the data required
#input = pd.read_csv(datasets/clean_df.csv)
#before running this, make sure to change the pem file to your directory
input = connect_database_download_data()
levels_survey_data = pd.read_csv("datasets/floor.csv")
seats_survey_data = pd.read_csv("datasets/chair.csv")
max_seat = pd.read_csv("datasets/actual_seat_count.csv")

gates_data = add_occupancy(input) #add occupancy to the data

MAX_OCCUPANCY_FOR_THE_LIBRARY = {}
MAX_OCCUPANCY_FOR_EACH_LEVEL={}  
levels = ["3","4","5","6","6Chinese"]
for level in levels:
  MAX_OCCUPANCY_FOR_THE_LIBRARY[level] = max_seat["count"].sum()
  MAX_OCCUPANCY_FOR_EACH_LEVEL[level] = max_seat[max_seat["level"] == level]["count"].sum()

# the starting date of each AYstartingdate to check at any given date, which AY and week it belongs to (week1-13 or recess or reading/exam)
AYstartingdate = {2019:pd.Timestamp(2019,8,5),2020:pd.Timestamp(2020,8,3),2021:pd.Timestamp(2021,8,2),2022:pd.Timestamp(2022,8,1),2023:pd.Timestamp(2023,8,7),
    2024:pd.Timestamp(2024,8,5),2025:pd.Timestamp(2025,8,4),2026:pd.Timestamp(2026,8,3)}
# the ending date of each AY to check at any given date, which AY it belongs to
AYendingdate = {2019:pd.Timestamp(2020,5,9),2020:pd.Timestamp(2021,5,8),2021:pd.Timestamp(2022,5,7),2022:pd.Timestamp(2023,5,6),2023:pd.Timestamp(2024,5,11),
    2024:pd.Timestamp(2025,5,10),2025:pd.Timestamp(2026,5,9),2026:pd.Timestamp(2027,5,8)}
# i sorta hard-coded here and it doesnt work if they input data before ay19/20 and after ay26/27

# the baseline (given) data if we dont have data for that week
BASELINE =  gates_data[(gates_data["Date"].dt.year == 2023) & (gates_data["Date"].dt.month == 1) & (25 <= gates_data["Date"].dt.day) & (gates_data["Date"].dt.day <= 27)] 

#if u want test indiviudally
#week = "Reading"
#day = 2
#hour = 24

#print(predict_occupancy(week,day,hour,gates_data,levels_survey_data,seats_survey_data)) 

model_output = create_model_output(gates_data,levels_survey_data,seats_survey_data)
print(model_output) 
model_output.to_csv("datasets/model_output.csv",index=False)
os.system('./predDB.sh')