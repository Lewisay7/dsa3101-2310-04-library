import pandas as pd
import numpy as np
import math

#to see the no of ppl in library at a given time
def add_occupancy(data):
  """
  Adds in number of people in the library at a given time

  Args:
      the merged entry and exit data

  Returns:
      dataframe containing the direction,datetime,date and occupancy columns
  """
  data["Datetime"] = pd.to_datetime(data["Datetime"])
  data["Date"] = pd.to_datetime(data["Date"])
  data = data.copy()
  data["occupancy"] = list(np.zeros(len(data)))
  # here i add the occupancy column to see the number of ppl in the library at a certain time 
  for i in range(len(data)):
    if i == 0: #first entry
      data.iloc[0,-1] = 1 
    elif (data.loc[i,"Direction"] == "Entry"): # if entry, occupancy +1
      data.iloc[i,-1] = data.iloc[i-1,-1] + 1
    elif (data.loc[i,"Direction"] == "Exit"): # if entry, occupancy -1
      data.iloc[i,-1] = data.iloc[i-1,-1] -1
  print(data)
  return data


def segregrate_data(data):
  """
  Segregrate the datas to their respective Academic years

  Args:
      the cleaned data 

  Returns:
      a dictionary , where the keys are the academic years(i.e for AY22/23 its 2022) and the values are the filtered data  
  """
  unique_years = list(data["Date"].dt.year.unique())
  output={}
  for years in unique_years:
    #here we check which AY is it in
    #for example we have 2023-12-01, then unique_years = 2023, so there are two possibilites, either it is in AY22/23 or AY23/24
    #then for different academic year we have different way of calculating the difference of the week and the starting date of the ay, read the function below(getRecessWeekData) to understand why its important
    temp1 = data[(AY[years-1]<= data["Date"]) & (data["Date"] < AY[years])] #22/23
    temp2 = data[(AY[years]<= data["Date"]) & (data["Date"] < AY[years + 1])] #23/24
    if not (temp1.empty):
      output[years - 1] = temp1
    if not(temp2.empty):
      output[years] = temp2
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
    temp = AYdata[((6.714285714285714 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < 8)) |
                  ((28.714285714285714 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < 30)) ]
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
    temp = AYdata[((week <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < week + 0.7142857142857143)) |
                  ((week + 22 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < week + 22.7142857142857143)) ]
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
    temp = AYdata[((14.714285714285714 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < 15.714285714285714)) |
                  ((36.714285714285714 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < 37.714285714285714))]
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
    temp = AYdata[((15.714285714285714 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < 17.857142857142858))|
                  ((37.714285714285714 <= ((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W'))) & (((AYdata["Date"] - AY[years]) / np.timedelta64(1,'W')) < 39.857142857142858))]
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

#split the max capacity of library into 5 categories, 5. 0-200 people (very empty) | 4. 201-400 | 3. 401-600 | 2. 601-800 | 1. 801-1500 (library is full)
PRESET_CATEGORY = {5:200,4:400,3:600,2:800,1:1500} # on the assumption that the max library capacity is 1.5k at any given time...
def calculate_occupancy_for_level(week,day,time,level,occupancy,levels_survey_data):
  """
  for the given week, day, time, we will get the occupancy of the whole building, then from here we use the survey_data to calculate the distribution for each level and times a probability to it

  Args:
    object,int,int,object,int,DataFrame
    level = 3/4/5/6/6Chinese (for chinese library)
    levels_survey_data = cleaned data from the survey_data
    
  Returns:
    an integer
  """
  #so now lets assume at 5pm the library has a total of 357 people, it would fall into category 4. The level dist will be:
  #lvl<x> = (v5[lvl<x>]+v4[lvl<x>])/sum(v5+v4) * no. of people
  #e.g lvl3 = (51+32)/[(51+46+53+48+37)+(32+77+45+62+30)] * 357 = 61 people on level 3
  global PRESET_CATEGORY # on the assumption that the max library capacity is 1.5k at any given time...
  for category,capacity in PRESET_CATEGORY.items():
    if occupancy <= capacity:
      occupancy_category = category
      break
  # to check if the timeframe interested in is within library opening hours. if it is only apply the probability thing, otherwise only level 6 is open, thus no meaning in calculating the probability
  if week in ["Reading","Exam"] :
    if 1<=day<=5: #weekday
      if time > 21 or time < 9: #library opens from 9am-9pm
        return occupancy
    elif day == 6: #saturday
      if time > 17 or time < 10: #library opens from 10am-5pm
        return occupancy
    elif day == 7: #library closes at sunday
      return occupancy

  probability = levels_survey_data[(levels_survey_data["level"] == level) & (levels_survey_data["preference"] >= occupancy_category)]["value"].sum() / levels_survey_data[levels_survey_data["preference"] >= occupancy_category]["value"].sum()
  return math.ceil(occupancy * probability)

def predict_occupancy(week, day, time, level, gates_data, levels_survey_data, seats_survey_data):
  """
  given the interested timeframe(week,day,time) and level, we use the cleaned data(data) to calculate and output the average occupancy of that specific timeframe using historical data
  
  Args:
      object,int,int,DataFrame
        week = 1-13/Recess/Exam/Reading
        day = 1-5 for normal week(1-13)
              1-6 for Recess week
              1-7 for Exam/Reading week
        1:Monday ... 7:Sunday
        time = 9-21 for normal week(1-13) and Recess week (weekday)
              10 - 17 for Recess week (weekend)
              1-24 for Exam/Reading week
        1: 0100hr 2: 0200hr ... 23: 2300hr 24: 0000hr
  Returns:
      an integer 
  """
  gates_data = gates_data.copy()
  # since we have such limited data, i assume that the distribution of occupancy for the weeks are almost iid.. and as the weeks get closer to midterms/exam, the number of people in the library would increase
  # the factor here is to
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
  if usedBaseline:
    occupancy =  math.ceil(gates_data[gates_data["Datetime"].dt.hour == time - 1].groupby(by=["Date"])["occupancy"].mean().mean() * factor[week])
  else:
    occupancy =  math.ceil(gates_data[gates_data["Datetime"].dt.hour == time - 1].groupby(by=["Date"])["occupancy"].mean().mean())
  return calculate_occupancy_for_level(week,day,time,level,occupancy,levels_survey_data)


def create_model_output(gates_data,levels_survey_data,seats_survey_data):
  """
  trying every possible combination of week,day,hour in the predict_occupancy function as our model_output, where we will store this dataframe in mysql for fast access

  Args:
      the cleaned data

  Returns:
      a dataframe 
  """
  model_output = {"week":[],"day" :[], "hour": [], "level":[], "occupancy" : []}
  #normal weeks
  for week in range(1,14): #week1-13
    for day in range(1,6): #monday to friday
      for time in range(9,22): #9am to 9pm
        for level in ["3","4","5","6","6Chinese"]:
          model_output["week"] = model_output["week"] + [week,]
          model_output["day"] = model_output["day"] + [day,]
          model_output["hour"] = model_output["hour"] + [time,]
          model_output["level"] = model_output["level"] + [level,]
          model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]

  #recess week
  for week in ["Recess"]:
    for day in range(1,7): #monday to saturday
      if day ==6: 
        for time in range(10,18): #10am to 5pm
            for level in ["3","4","5","6","6Chinese"]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [time,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
      else:
        for time in range(9,22): #9am to 9pm
            for level in ["3","4","5","6","6Chinese"]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [time,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
  #reading/exam week
  for week in ["Reading","Exam"]:
    for day in range(1,8): #since the library 24/7, can allow the user to select monday to sunday
      if 1<=day<=5:
        for time in range(1,25):
          if time > 21 or time < 9: #outside of library opening hours
            level = "6"
            model_output["week"] = model_output["week"] + [week,]
            model_output["day"] = model_output["day"] + [day,]
            model_output["hour"] = model_output["hour"] + [time,]
            model_output["level"] = model_output["level"] + [level,]
            model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
          else:
            for level in ["3","4","5","6","6Chinese"]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [time,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
      elif day == 6:
        for time in range(1,25): # 24 hours
          if time > 17 or time < 10: #outside of library opening hours
            level = "6"
            model_output["week"] = model_output["week"] + [week,]
            model_output["day"] = model_output["day"] + [day,]
            model_output["hour"] = model_output["hour"] + [time,]
            model_output["level"] = model_output["level"] + [level,]
            model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
          else:
            for level in ["3","4","5","6","6Chinese"]:
              model_output["week"] = model_output["week"] + [week,]
              model_output["day"] = model_output["day"] + [day,]
              model_output["hour"] = model_output["hour"] + [time,]
              model_output["level"] = model_output["level"] + [level,]
              model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
      elif day == 7: #library closes on sunday
        for time in range(1,25):
          level = "6"
          model_output["week"] = model_output["week"] + [week,]
          model_output["day"] = model_output["day"] + [day,]
          model_output["hour"] = model_output["hour"] + [time,]
          model_output["level"] = model_output["level"] + [level,]
          model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(week,day,time,level,gates_data,levels_survey_data,seats_survey_data),]
  return pd.DataFrame(model_output)


input = pd.read_csv("datasets/clean_df.csv")
levels_survey_data = pd.read_csv("datasets/floor.csv")
seats_survey_data = pd.read_csv("datasets/chair.csv")

gates_data = add_occupancy(input)

# the starting week of each AY to check at any given date, which week it is (week1-13 or recess or reading/exam)
# i sorta hard-coded here and it doesnt work if they input data before ay20/21 and after ay26/27
AY = {2020:pd.Timestamp(2020,8,3),2021:pd.Timestamp(2021,8,2),2022:pd.Timestamp(2022,8,1),2023:pd.Timestamp(2023,8,7),
    2024:pd.Timestamp(2024,8,5),2025:pd.Timestamp(2025,8,4),2026:pd.Timestamp(2026,8,3)}

# the baseline (given) data if we dont have data for that week
BASELINE =  gates_data[(gates_data["Date"].dt.month == 1) & (25 <= gates_data["Date"].dt.day) & (gates_data["Date"].dt.day <= 27)] 

#split the max capacity of library into 5 categories, 5. 0-200 people (very empty) | 4. 201-400 | 3. 401-600 | 2. 601-800 | 1. 801-1500 (library is full)
PRESET_CATEGORY = {5:200,4:400,3:600,2:800,1:1500} # on the assumption that the max library capacity is 1.5k at any given time...

#if u want test indiviudally
#week = "Reading"
#day = 2
#hour = 24
#level = "6" #(level must be a string here)
#print(predict_occupancy(week,day,hour,level,gates_data,levels_survey_data,seats_survey_data)) 

model_output = create_model_output(gates_data,levels_survey_data,seats_survey_data)
print(model_output) 
model_output.to_csv("datasets/model_output.csv",index=False)
