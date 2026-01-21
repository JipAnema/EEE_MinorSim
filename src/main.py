# Name: main.py
# Description: Main python file. Contains the simulation
# Usage: Enable/Disable stats and plotting, adjust settings and run the file.   

# Imports
import symFermentation as fw
import sympowerusage as pu
import symPowerSupply as ps
import calcEnergyPrice as price
import auxfunctions as aux
import matplotlib.pyplot as plt
from collections import defaultdict
import time
import csv

# ================================================================================== #
' Simulation settings  '

timesteps = aux.timeToSecond(16,0,0,0)    # Time to simulate (day,hour,minute,second)
offsetTime = aux.timeToSecond(90,0,0,0)    # Offset time in seconds for power profiles (day,hour,minute,second)
offsetTimeProd = aux.timeToSecond(0,0,0,0)# Offset fermentation proces relative to offsetTime (day,hour,minute,second)
transformerRating = 2000                  # kVA rating of transformer
pvFactor = [0,0],[1200,2823.529]          # Linear factor to convert j/m2 to kW for PV system
windFactor =  [0, 0],[3, 0],[3.5, 36],\
  [4, 76],[4.5, 134],[5, 192],[5.5, 269],\
  [6, 346],[6.5, 465],[7, 584],[7.5, 737],\
  [8, 890],[8.5, 1098],[9, 1306],[9.5, 1514],\
  [10, 1722],[10.5, 1942],[11, 2162],[11.5, 2352],\
  [12, 2542],[12.5, 2701],[13, 2860],[13.5, 2930],\
  [14, 2970],[14.5, 2983],[15, 2995],[15.5, 3000],\
  [25, 3000],[25.5, 0],[35, 0]          # 2D list to convert m/s to kW for Wind system
pvCO2factor = 13.2                      # g CO2 per kWh for PV production
windCO2factor = 10.93                   # g CO2 per kWh for Wind production
greyCO2factor = 445.25                  # g CO2 per kWh for grey energy consumption

# ================================================================================== #
' Simulation instances '

power1 = pu.symPowerUsage('CSV profiles/fermentationProfile.csv', True, True, 0)
otherTrafoLoad = pu.symPowerUsage('CSV profiles/otherLoad.csv', True, True, 0)
battery = pu.symPowerUsage('CSV profiles/battery.csv',True, False, -400)
costCalculator = price.calcEnergyPrice('CSV profiles/costOfEnergy.csv', True)
pvSystem = ps.symPowerSupply('CSV profiles/pvProfile.csv', 2000, 0, pvFactor,1, True,True)  # 2000 kW peak 1 'group' of panels
windSystem = ps.symPowerSupply('CSV profiles/windProfile.csv', 6000, 0, windFactor,2, True,True)  # 6000 kW peak 2 turbines

# ================================================================================== #
' Start stats '
# Changing the var 'startStat' will enable/disable start statistics.
startStat = False

if startStat:
  print("Transformer Rating:", transformerRating, "kVA")

# ================================================================================== #
' Simulation '
# Every step will count as 1 second. 
secondsPassed = 0
totalCO2Production = 0
powerUsage = defaultdict(list)
enableBattery = False
startTime = time.perf_counter() 

# Offset entire symulation in time
power1.setTimeSeconds(offsetTime)
power1.offsetOutputIndex(offsetTimeProd, True)
otherTrafoLoad.setTimeSeconds(offsetTime)
battery.setTimeSeconds(offsetTime)
pvSystem.setTimeSeconds(offsetTime)
windSystem.setTimeSeconds(offsetTime)
costCalculator.setTimeSeconds(offsetTime)

# Simulation (second based)
for t in range(timesteps):
  facilityPower = 0
  greenPowerProduction = 0
  powerBuffer = 0
  totalTrafoLoad = 0
  facilityGreenCO2Percentage = 0
  
  ' Consumers '
  # Power Sim 1
  powerBuffer = power1.getPowerConsumption()
  if not aux.isValueGood(powerBuffer,"Power sim 1"):
    exit()
  powerUsage['Power1'].append(powerBuffer)
  facilityPower += powerBuffer

  # Battery
  if enableBattery:
    powerBuffer = battery.getPowerConsumption()
    facilityPower += powerBuffer

  # Cost calculation
  costCalculator.PowerUsage(facilityPower)
  powerUsage['CurrentPcost'].append(costCalculator.getPowerCost(facilityPower) / 3600)
  powerUsage['time'].append(secondsPassed)

  # Other power users on same bus
  powerBuffer = otherTrafoLoad.getPowerConsumption()
  if not aux.isValueGood(powerBuffer,"Other power users on same bus"):
    exit()
  totalTrafoLoad = float(powerBuffer + facilityPower)
  powerUsage['TotalTrafoLoad'].append(totalTrafoLoad)

  facilityPowerShare = facilityPower / totalTrafoLoad

  ' Producers '
  # PV System
  powerBuffer = pvSystem.getPowerProduction()
  powerUsage['PVProduction'].append(float(powerBuffer))
  greenCO2Production = powerBuffer * pvCO2factor / 3600
  greenPowerProduction += powerBuffer

  # Wind System
  powerBuffer = windSystem.getPowerProduction()
  powerUsage['WindProduction'].append(float(powerBuffer))
  greenCO2Production += powerBuffer * windCO2factor / 3600
  greenPowerProduction += powerBuffer
  

  ' CO2 production '
  # Current CO2 production
  faciltyGreenCO2 = greenCO2Production * facilityPowerShare
  facilityGreyCO2 = (totalTrafoLoad - aux.limit(0,greenPowerProduction,totalTrafoLoad)) * greyCO2factor / 3600 * facilityPowerShare
  faciltyTotalCO2 = faciltyGreenCO2 + facilityGreyCO2

  facilityGreenCO2Percentage = aux.limit(0,greenPowerProduction,totalTrafoLoad) / totalTrafoLoad * 100

  powerUsage['FacilityGreenCO2'].append(faciltyGreenCO2)
  powerUsage['FacilityGreyCO2'].append(facilityGreyCO2)
  powerUsage['FacilityTotalCO2'].append(faciltyTotalCO2)
  powerUsage['FacilityGreenCO2Percentage'].append(facilityGreenCO2Percentage)

  # Cumulative CO2 production (integrating)
  totalCO2Production += faciltyTotalCO2 / 1000
  powerUsage['totalCO2Production'].append(totalCO2Production)

  # Keep last (End of sim)
  secondsPassed += 1

# ================================================================================== #
' Write outputs to CSV '
# Changing the var 'writeCSV' will enable/disable writing data to a csv file. 
writeCSV = True
csvPath = 'CSV profiles\SimulationOutput.csv'

if writeCSV:
  # Compact all the data (and structure to colums) powerUsage['Ferm1'],
  data = zip(powerUsage['time'],powerUsage['CurrentPcost'],powerUsage['Power1'], powerUsage['TotalTrafoLoad'],powerUsage['PVProduction'],powerUsage['WindProduction'],powerUsage['FacilityGreenCO2'], powerUsage['FacilityGreyCO2'], powerUsage['totalCO2Production'], powerUsage['FacilityGreenCO2Percentage'])

  # Write data to csv
  with open(csvPath,'w', newline= '') as simcsv:
    fieldnames = ['time','Current Power Cost (euro)','Power sim 1(kW)', 'Total Transformer Load(kW)', 'PV Production(kW)', 'Wind Production(kW)', 'Facility Green CO2(g CO2)', 'Facility Grey CO2(g CO2)', 'Facility Cumulative CO2(kg CO2)', 'Facility Green CO2 percentage (Current % green CO2 of total CO2)']
    writer = csv.writer(simcsv,delimiter=';') 
    writer.writerow(fieldnames)
    writer.writerows(data)
    simcsv.close()


# ================================================================================== #
' End stats '
# Changing the var 'endStat' will enable/disable end statistics.
endStat = True

if endStat:
  print("Minutes Passed:", secondsPassed / 60)
  print("Total Power Consumption:", round(costCalculator.getTotalPower(),4) , "kWh")
  print("Total Power Cost:", costCalculator.getTotalCost(), "Euro")
  print("Total Facility CO2 production:", round(totalCO2Production,4), "kG CO2")
  print("Simulation time (s):", round(time.perf_counter() - startTime,4))

# ================================================================================== #
' Plotting '
# Changing the var 'plot' will enable/disable plotting.
plot = False

if plot: 
  plt.plot(powerUsage['TotalTrafoLoad'])
  plt.plot(powerUsage['PVProduction'])
  plt.plot(powerUsage['WindProduction'])
  plt.ylabel('Power Production (kW)')
  plt.xlabel('Time (seconds)')
  plt.show()

# ================================================================================== #