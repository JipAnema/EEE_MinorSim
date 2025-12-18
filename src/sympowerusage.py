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
    def __init__(self, filepath, enableWrapping,enableInterpolate ,offset):
        self.filepath = filepath
        self.timeSeconds = 0
        self.index = 0
        self.colums = defaultdict(list)
        self.enableWrapping = enableWrapping
        self.enableInterpolate = enableInterpolate
        self.offset = offset

        # Open and write colums to list
        with open(self.filepath) as file:
            filereader = csv.DictReader(file,delimiter=';')
            for row in filereader:
                for (k,v) in row.items():
                    self.colums[k].append(v)
        
        # Read power accuracy (first input is used)
        self.accuracy = int(self.colums['accuracy(sec)'][0])
    
    # Set time in seconds
    def setTimeSeconds(self,seconds):
        self.timeSeconds = seconds
        self.index = int(self.timeSeconds / self.accuracy)

    def getPowerConsumption(self):
        # Check time step
        self.timeSeconds += 1
        if self.timeSeconds % self.accuracy == 0:
            self.index += 1

        # Check for out of bounds index
        if self.index > len(self.colums['power(kw)']) - 1 and not self.enableWrapping:
            return -1
        elif self.index > len(self.colums['power(kw)']) - 1 and self.enableWrapping:
            self.index = 0

        # Return correct power usage based on time
        if self.enableInterpolate:
            return self.__interpolateProduction(float(self.colums['power(kw)'][self.index].replace(",", "."))) + self.offset
        else:

            return float(self.colums['power(kw)'][self.index].replace(",", ".")) + self.offset

    # Interpolate 
    def __interpolateProduction(self, production):
        y0 = production
        x0 = self.accuracy * self.index
        
        if self.index >= len(self.colums['power(kw)']) - 1:
            return production
        else:
            index = self.index + 1

        y1 = float(self.colums['power(kw)'][index].replace(",", "."))
        x1 = self.accuracy * (index)
        return (y1 - y0) / (x1 - x0) * (self.timeSeconds % (self.accuracy)) + production