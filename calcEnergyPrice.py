# Name: calcEnergyPrice.py
# Description: Class to read a csv file that has the price per kW, and return the cost for the given power
# Usage:  Import the class and create an instance with the csv file path as parameter. 
#         The class will read the price per kW. Calling PowerUsage() will return
#         the current cost of the given energy in euro's based on the time (second). Calling 
#         PowerUsage() counts as 1 second passed.   
# Written by: Jip

import csv 
from collections import defaultdict

class calcEnergyPrice:
    def __init__(self, filepath):
        self.filepath = filepath
        self.timeSeconds = 0
        self.index = 0
        self.totalCost = 0
        self.totalPower = 0
        self.colums = defaultdict(list)

        # Open and write colums to list
        with open(self.filepath) as file:
            filereader = csv.DictReader(file,delimiter=';')
            for row in filereader:
                for (k,v) in row.items():
                    self.colums[k].append(v)
        
        # Read cost accuracy (first input is used)
        self.accuracy = int(self.colums['accuracy(min)'][0]) * 60

    # Return current price based on time from PowerUsage()
    def getCurrentPrice(self):
        return float(self.colums['price(euro)'][self.index].replace(",", "."))
    
    # Increment time unit, calculate total power and cost
    def PowerUsage(self, currentPower):
        # Check time step
        if self.timeSeconds % self.accuracy == 0:
            self.index += 1
        self.timeSeconds += 1

        # Check for out of bounds index
        if self.index > len(self.colums['price(euro)']) - 1:
            return -1
    
        self.totalCost += self.getPowerCost(currentPower / 3600 )
        self.totalPower += (currentPower / 3600)

    # Return price of current power based on time
    def getPowerCost(self, currentPower):
        return self.getCurrentPrice() * currentPower
    
    # Return total power
    def getTotalPower(self):
        return float(self.totalPower)
    
    # Return total cost
    def getTotalCost(self):
        return "%.2f" % round(self.totalCost,2)
