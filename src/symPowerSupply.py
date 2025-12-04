# Name: sympowersupply.py
# Description: Class to read a csv file that has a production profile of an unspecified unit, and uses a linear factor to return power production.
# Usage:  Import the class and create an instance with the csv file path, upperlimit, lowerlimit, and factor as parameters. 
#         The class will read the power accuracy. Calling getPowerProduction() will return
#         the current power consumption in kW based on the time (second). Calling 
#         getPowerProduction() counts as 1 second passed.   
# Written by: Jip

import csv 
import bisect
from collections import defaultdict

class symPowerSupply:
    def __init__(self, filepath, upperLimit, lowerLimit, factor, count):
        self.filepath = filepath
        self.timeSeconds = 0
        self.index = 0
        self.upperLimit = upperLimit
        self.lowerLimit = lowerLimit
        self.factor = factor
        self.count = count
        self.previusProduction = 0
        self.previusScaledPower = 0
        self.colums = defaultdict(list)

        # Open and write colums to list
        with open(self.filepath) as file:
            filereader = csv.DictReader(file,delimiter=';')
            for row in filereader:
                for (k,v) in row.items():
                    self.colums[k].append(v)
        
        # Read power accuracy (first input is used)
        self.accuracy = int(self.colums['accuracy(sec)'][0])

    def getPowerProduction(self):
        # Check time step
        self.timeSeconds += 1
        if self.timeSeconds % self.accuracy == 0:
            self.index += 1

        # Check for out of bounds index
        if self.index > len(self.colums['production']) - 1:
            return -1
        
        production = float(self.colums['production'][self.index].replace(",", "."))

        # Return correct power usage based on time
        return self.__limit(self.lowerLimit, self.__getScaledPower(production), self.upperLimit)
    
    def __getScaledPower(self,production):
        # Check for previus value
        if production == self.previusProduction:
            return self.previusScaledPower
        
        # Find index for interpolation
        for i in range(len(self.factor)):
            if production < self.factor[i][0]:
                index = i
                break

        # Linear interpolation
        x1 = float(self.factor[index][0])
        x0 = float(self.factor[index - 1][0])
        y1 = float(self.factor[index][1])
        y0 = float(self.factor[index - 1][1])

        scaledPower = ((y1 - y0) / (x1 - x0) * (production - x0) + y0) * self.count

        # Store previous values
        self.previusProduction = production
        self.previusScaledPower = scaledPower

        return scaledPower 

    def __limit(self,lowerlimit,value,upperlimit):
        if value <= lowerlimit:
            return lowerlimit
        elif value >= upperlimit:
            return upperlimit
        else:
            return value
