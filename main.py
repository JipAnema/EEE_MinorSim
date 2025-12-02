# Name: main.py
# Description: Main python file. Contains the simulation
# Usage: Enable/Disable stats and plotting, adjust settins and run the file.   
# Written by: Jip

# Imports
import symFermentation as fw
import sympowerusage as p
import calcEnergyPrice as price
import auxfunctions as aux
import matplotlib.pyplot as plt
from collections import defaultdict
import csv

# ================================================================================== #
' Simulation settings  '

timesteps = aux.timeToSecond(0,12,0,0)  # Time to simulate (day,hour,minute,second)
setpoint = 40.0                         # Target temperature in Celsius
transformerRating = 1000                # kVA rating of transformer
cosPhi = 0.85                           # Power factor of all loads

# ================================================================================== #
' Simulation instances '

power1 = p.symPowerUsage('test.csv')
otherTrafoLoad = p.symPowerUsage('otherLoad.csv')
fermentatie1 = fw.symFermentation(100000, 4186, 200, 20.0, 0.1, 20, 0.05, 10.0 )  # 1000 kg, water, 200 kW heater, initial temp 20C, warmtegeleiding_coeff 0.1, oppervlakte 20m2, dikte 0.05m, omgeving temp 10C
costCalculator = price.calcEnergyPrice('costOfEnergy.csv')

# ================================================================================== #
' Start stats '
# Changing the var 'startStat' will enable/disable start statistics.
startStat = False

if startStat:
  print("Initial Temperature:", fermentatie1.getTemperature(), "°C")
  print("Transformer Rating:", transformerRating, "kVA")

# ================================================================================== #
' Simulation '
# Every step will count as 1 second. 
secondsPassed = 0
powerUsage = defaultdict(list)
powerBuffer = 0

fermentatie1.setNewTemperature(setpoint)  # Set target temperature to 25C
for t in range(timesteps):
  totalPower = 0
  # Fermentatie 1
  powerBuffer = fermentatie1.getPowerConsumption()
  powerUsage['Ferm1'].append(powerBuffer)
  totalPower += powerBuffer

  # Power Sim 1
  powerBuffer = power1.getPowerConsumption()
  if not aux.isValueGood(powerBuffer,"Power sim 1"):
    exit()
  powerUsage['Power1'].append(powerBuffer)
  totalPower += powerBuffer

  costCalculator.PowerUsage(totalPower)
  powerUsage['CurrentPcost'].append(costCalculator.getPowerCost(totalPower) / 3600)
  powerUsage['time'].append(secondsPassed)

  # Other power users on same bus
  powerBuffer = otherTrafoLoad.getPowerConsumption()
  if not aux.isValueGood(powerBuffer,"Other power users on same bus"):
    exit()
  powerUsage['TotalTrafoLoad'].append(powerBuffer + totalPower)

  # Keep last (End of sim)
  secondsPassed += 1

# ================================================================================== #
' End stats '
# Changing the var 'endStat' will enable/disable end statistics.
endStat = True

if endStat:
  print("Minutes Passed:", secondsPassed / 60)
  #print("Final Temperature:", fermentatie1.get_temp(), "°C")
  print("Total Power Consumption:", round(costCalculator.getTotalPower(),4) , "kWh")
  print("Total Power Cost:", costCalculator.getTotalCost(), "Euro")

# ================================================================================== #
' Write outputs to CSV '
# Changing the var 'writeCSV' will enable/disable writing data to a csv file. 
writeCSV = True
csvPath = 'SimulationOutput.csv'

if writeCSV:
  # Compact all the data (and structure to colums)
  data = zip(powerUsage['time'],powerUsage['CurrentPcost'],powerUsage['Ferm1'],powerUsage['Power1'], powerUsage['TotalTrafoLoad'])

  # Write data to csv
  with open(csvPath,'w', newline= '') as simcsv:
    fieldnames = ['time','Current Power Cost','Fermentation 1','Power sim 1', 'Total Transformer Load']
    writer = csv.writer(simcsv,delimiter=';') 
    writer.writerow(fieldnames)
    writer.writerows(data)
    simcsv.close()
  

# ================================================================================== #
' Plotting '
# Changing the var 'plot' will enable/disable plotting.
plot = False

if plot: 
  plt.plot(powerUsage['Power1'])
  plt.plot(powerUsage['Ferm1'])
  plt.ylabel('Power Consumption (kW)')
  plt.xlabel('Time (seconds)')
  plt.show()

# ================================================================================== #