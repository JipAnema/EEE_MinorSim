# Name: sympowerusage.py
# Description: Class to read a csv file that has a power usage of a (group of) machine(s)
# Usage:  Import the class and create an instance with the csv file path as parameter. 
#         The class will read the power accuracy. Calling getPowerConsumption() will return
#         the current power consumption in kW based on the time (second). Calling 
#         getPowerConsumption() counts as 1 second passed.   
# Written by: Jip

import csv 
from collections import defaultdict

class symPowerUsage:
    def __init__(self, filepath):
        self.filepath = filepath
        self.timeSeconds = 0
        self.index = 0
        self.colums = defaultdict(list)

        # Open and write colums to list
        with open(self.filepath) as file:
            filereader = csv.DictReader(file,delimiter=';')
            for row in filereader:
                for (k,v) in row.items():
                    self.colums[k].append(v)
        
        # Read power accuracy (first input is used)
        self.accuracy = int(self.colums['accuracy(sec)'][0])

    def getPowerConsumption(self):
        # Check time step
        if self.timeSeconds % self.accuracy == 0:
            self.index += 1
        self.timeSeconds += 1

        # Check for out of bounds index
        if self.index > len(self.colums['power(kw)']) - 1:
            return -1
        
        # Return correct power usage based on time
        return float(self.colums['power(kw)'][self.index].replace(",", "."))