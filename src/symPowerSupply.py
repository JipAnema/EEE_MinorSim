# Name: sympowersupply.py
# Description: Class to read a csv file that has a production profile of an unspecified unit, and uses linear interpolation to return power production.
# Usage:  Import the class and create an instance with the csv file path, upperlimit, lowerlimit, and factor as parameters. 
#         The class will read the power accuracy. Calling getPowerProduction() will return
#         the current power consumption in kW based on the time (second). Calling 
#         getPowerProduction() counts as 1 second passed.   
# Written by: Jip

import csv 
import bisect
from collections import defaultdict

class symPowerSupply:
    def __init__(self, filepath, upperLimit, lowerLimit, factor, count, enableInterpolation, enableWrapping):
        self.filepath = filepath
        self.timeSeconds = 0
        self.index = 0
        self.upperLimit = upperLimit
        self.lowerLimit = lowerLimit
        self.factor = factor
        self.count = count
        self.previusProduction = 0
        self.previusScaledPower = 0
        self.enableInterpolation = enableInterpolation
        self.enableWrapping = enableWrapping
        self.colums = defaultdict(list)

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
        self.index = int((self.timeSeconds / self.accuracy) % len(self.colums['production']))

    # Return scaled and interpolated power production
    def getPowerProduction(self):
        # Check time step
        self.timeSeconds += 1
        if self.timeSeconds % self.accuracy == 0:
            self.index += 1

        # Check for out of bounds index
        if self.index > len(self.colums['production']) - 1 and not self.enableWrapping:
            return -1
        elif self.index > len(self.colums['production']) - 1 and self.enableWrapping:
            self.index = 0

        production = float(self.colums['production'][self.index].replace(",", "."))

        if self.enableInterpolation:
            production = self.__interpolateProduction(production)

        # Return correct power usage based on time
        return self.__limit(self.lowerLimit, self.__getScaledPower(production), self.upperLimit)
    
    # Interpolate 
    def __interpolateProduction(self, production):
        y0 = production
        x0 = self.accuracy * self.index
        
        if self.index >= len(self.colums['production']) - 1:
            return production
            index = len(self.colums['production']) - 1
        else:
            index = self.index + 1

        y1 = float(self.colums['production'][index].replace(",", "."))
        x1 = self.accuracy * (index)
        return (y1 - y0) / (x1 - x0) * (self.timeSeconds % (self.accuracy)) + production

    # 
    def __getScaledPower(self,production):
        # Check for previus value
        if production == self.previusProduction:
            return self.previusScaledPower
        
        # O(log n) Binary search
        length = len(self.factor)
        upperFind = length
        lowerFind = 0
        tryindex = int(upperFind / 2)

        if production >= self.factor[upperFind - 1][0]:
            upperFind -= 1
            lowerFind = upperFind - 1
        elif production <= self.factor[lowerFind][0]:
            upperFind = 1
        else:
            while upperFind - lowerFind != 1:
                tryval = self.factor[tryindex][0]
                if production > tryval:
                    lowerFind = tryindex
                    tryindex += int((upperFind - lowerFind) / 2)
                elif production < tryval:
                    upperFind = tryindex
                    tryindex -= int((upperFind - lowerFind) / 2)
                else:
                    upperFind = tryindex + 1
                    lowerFind = tryindex
        
        # Linear interpolation
        x1 = float(self.factor[upperFind][0])
        x0 = float(self.factor[lowerFind][0])
        y1 = float(self.factor[upperFind][1])
        y0 = float(self.factor[lowerFind][1])

        scaledPower = ((y1 - y0) / (x1 - x0) * (production - x0) + y0) * self.count

        # Store previous values
        self.previusProduction = production
        self.previusScaledPower = scaledPower

        return scaledPower 

    # Limit value
    def __limit(self,lowerlimit,value,upperlimit):
        if value <= lowerlimit:
            return lowerlimit
        elif value >= upperlimit:
            return upperlimit
        else:
            return value
