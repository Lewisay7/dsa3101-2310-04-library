import pandas as pd
import numpy as np
import math

def select_columns(input):
  
  """
  select the columns that are relevant in our model

  Args:
      the input data

  Returns:
      dataframe containing the direction,datetime,date columns
  """
  entry = input[["EntryDate","EntryTime","EntryDirection"]]
  exit = input[["ExitDate","ExitTime","ExitDirection"]]

  #add a column for datetime to plot the graph and to calculate average occupancy
  entry["Datetime"] = pd.to_datetime(entry["EntryDate"].astype(str) + " " +  entry["EntryTime"].astype(str))
  exit["Datetime"] = pd.to_datetime(exit["ExitDate"].astype(str) + " " + exit["ExitTime"].astype(str))

  #rename the columns for concatanation
  exit = exit.rename(columns={"ExitDate": "Date","ExitDirection":"Direction","ExitTime":"Time"})
  entry = entry.rename(columns={"EntryDate": "Date","EntryDirection":"Direction","EntryTime":"Time"})

  #concat entry and exit data to one dataframe with columns [Direction,Datetime,Date]
  data = pd.concat([entry,exit],ignore_index=True)
  data = data.sort_values(by = "Datetime")
  data = data[["Direction", "Datetime","Date"]]
  data["Date"] = pd.to_datetime(data["Date"])
  return data


#to see the no of ppl in library at a given time
def add_occupancy(data):
  """
  Adds in number of people in the library at a given time

  Args:
      the merged entry and exit data

  Returns:
      dataframe containing the direction,datetime,date and occupancy columns
  """
  data = data.copy()
  data["occupancy"] = list(np.zeros(len(data)))
  # here i add the occupancy column to see the number of ppl in the library at a certain time 
  for i in range(len(data)):
    if i == 0: #first entry
      data.iloc[0,-1] = 1 
    elif (data.iloc[i,0] == "Entry"): # if entry, occupancy +1
      data.iloc[i,-1] = data.iloc[i-1,-1] + 1
    elif (data.iloc[i,0] == "Exit"): # if entry, occupancy -1
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
    return baseline,True
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


def predict_occupancy(week, day, time,data):
  """
  given the interested timeframe(week,day,time) we use the cleaned data(data) to calculate and output the average occupancy of that specific timeframe using historical data

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
  data = data.copy()
  # since we have such limited data, i assume that the distribution of occupancy for the weeks are almost iid.. and as the weeks get closer to midterms/exam, the number of people in the library would increase
  # the factor here is to
  factor = {1:0.95,2:0.97,3:1,4:1.03,5:1.05,6:1.1,7:1.1,8:1.05,9:1.06,10:1.06,11:1.18,12:1.2,13:1.3}
  temp = segregrate_data(data)
  usedBaseline = False
  # here i split the weeks into different scenarios to access different weeks of data
  if week == "Recess": 
    data = getRecessWeekData(temp)
  elif week == "Reading":
    data = getReadingWeekData(temp)
  elif week == "Exam":
    data = getExamWeekData(temp)
  elif 1<=week<=13:
    data, usedBaseline = getNormalWeekData(temp,week)
  data = checkIfDataOfDayPresent(data,day)
  if usedBaseline:
    return math.ceil(data[data["Datetime"].dt.hour == time - 1].groupby(by=["Date"])["occupancy"].mean().mean() * factor[week])
  return math.ceil(data[data["Datetime"].dt.hour == time - 1].groupby(by=["Date"])["occupancy"].mean().mean())


def create_model_output(data):
  """
  trying every possible combination of week,day,hour in the predict_occupancy function as our model_output, where we will store this dataframe in mysql for fast access

  Args:
      the cleaned data

  Returns:
      a dataframe 
  """
  model_output = {"week":[],"day" :[], "hour": [], "occupancy" : []}
  #normal weeks
  for i in range(1,14): #week1-13
    for j in range(1,6): #monday to friday
      for z in range(9,22): #9am to 9pm
        model_output["week"] = model_output["week"] + [i,]
        model_output["day"] = model_output["day"] + [j,]
        model_output["hour"] = model_output["hour"] + [z,]
        model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(i,j,z,data),]

  #recess week
  for i in ["Recess"]:
    for j in range(1,7): #monday to saturday
      if j ==6: 
        for z in range(10,18): #10am to 5pm
          model_output["week"] = model_output["week"] + [i,]
          model_output["day"] = model_output["day"] + [j,]
          model_output["hour"] = model_output["hour"] + [z,]
          model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(i,j,z,data),]
      else:
        for z in range(9,22): #9am to 9pm
            model_output["week"] = model_output["week"] + [i,]
            model_output["day"] = model_output["day"] + [j,]
            model_output["hour"] = model_output["hour"] + [z,]
            model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(i,j,z,data),]

  #reading/exam week
  for i in ["Reading","Exam"]:
    for j in range(1,8): #since the library 24/7, can allow the user to select monday to sunday
      for z in range(1,25): # 24 hours
        model_output["week"] = model_output["week"] + [i,]
        model_output["day"] = model_output["day"] + [j,]
        model_output["hour"] = model_output["hour"] + [z,]
        model_output["occupancy"] = model_output["occupancy"] + [predict_occupancy(i,j,z,data),]
  return pd.DataFrame(model_output)


input = pd.read_csv("datasets/clean_df.csv")
data = select_columns(input)
data = add_occupancy(data)
# the code above take quite long to run...
# the starting week of each AY to check at any given date, which week it is (week1-13 or recess or reading/exam)
# i sorta hard-coded here and it doesnt work if they input data before ay20/21 and after ay26/27
AY = {2020:pd.Timestamp(2020,8,3),2021:pd.Timestamp(2021,8,2),2022:pd.Timestamp(2022,8,1),2023:pd.Timestamp(2023,8,7),
    2024:pd.Timestamp(2024,8,5),2025:pd.Timestamp(2025,8,4),2026:pd.Timestamp(2026,8,3)}
# the baseline (given) data if we dont have data for that week
baseline =  data[(data["Date"].dt.month == 1) & (25 <= data["Date"].dt.day) & (data["Date"].dt.day <= 27)] 

# if u want test indiviudally
# week = "Reading"
# day = 2
# hour = 17
# print(predict_occupancy(week,day,hour,data)) 

model_output = create_model_output(data)
print(model_output) 






