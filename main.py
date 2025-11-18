# Name: main.py
# Description: Main python file. Contains the simulation
# Usage: Enable/Disable stats and plotting, adjust settins and run the file.   
# Written by: Jip

# Imports
import fermentatiewarmte as fw
import sympowerusage as p
import calcEnergyPrice as price
import auxfunctions as aux
import matplotlib.pyplot as plt
from collections import defaultdict

# ================================================================================== #
' Simulation settings  '

timesteps = aux.timeToSecond(3,1,30,0)  # Time to simulate (day,hour,minute,second)
setpoint = 40.0  # Target temperature in Celsius

# ================================================================================== #
' Simulation instances '

power1 = p.symPowerUsage('test.csv')
fermentatie1 = fw.FermentatieWarmte(100000, 4186, 200, 20.0, 0.1, 20, 0.05, 10.0 )  # 1000 kg, water, 200 kW heater, initial temp 20C, warmtegeleiding_coeff 0.1, oppervlakte 20m2, dikte 0.05m, omgeving temp 10C
costCalculator = price.calcEnergyPrice('costOfEnergy.csv')

# ================================================================================== #
' Start stats '
# Changing the var 'startStat' will enable/disable end statistics.
startStat = True

if startStat:
  print("Initial Temperature:", fermentatie1.get_temp(), "°C")

# ================================================================================== #
' Simulation '
# Every step will count as 1 second. 
secondsPassed = 0
powerUsage = defaultdict(list)
powerBuffer = 0

fermentatie1.set_newtemperature(setpoint)  # Set target temperature to 25C
for t in range(timesteps):
  totalPower = 0
  # Fermentatie 1
  powerBuffer = fermentatie1.getPowerConsumption()
  powerUsage['Ferm1'].append(powerBuffer)
  totalPower += powerBuffer

  # Power Sim 1
  powerBuffer = power1.getPowerConsumption()
  powerUsage['Power1'].append(powerBuffer)
  totalPower += powerBuffer

  costCalculator.PowerUsage(totalPower)
  # Keep last (End of sim)
  secondsPassed += 1

# ================================================================================== #
' End stats '
# Changing the var 'endStat' will enable/disable end statistics.
endStat = True

if endStat:
  print("Minutes Passed:", secondsPassed / 60)
  #print("Final Temperature:", fermentatie1.get_temp(), "°C")
  print("Total Power Consumption:", costCalculator.getTotalPower(), "kWh")
  print("Total Power Cost:", costCalculator.getTotalCost(), "Euro")
  
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