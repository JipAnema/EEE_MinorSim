# Name: auxfunctions.py
# Description: Extra functions to assist the simulation
# Usage: Use the functions as required
# Written by: Jip

def timeToSecond(day,hour,minute,second):
  return (day * 86400) + (hour * 3600) + (minute * 60) + second

def isValueGood(value, callName):
  if value < 0:
    print("Value not ok. Value: ", value, ". Friendly name: ", callName)
    return False
  return True

def limit(lowerlimit,value,upperlimit):
  if value < lowerlimit:
    return lowerlimit
  elif value > upperlimit:
    return upperlimit
  else:
    return value