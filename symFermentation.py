# Name: fermentatiewarmte.py
# Description: Class to calculate power consumption for fermentation heat control
# Usage:  Import the class and create an instance with the required parameters 
#         to manage fermentation temperatureerature. Calling getPowerConsumption() will return
#         the current power consumption in kW based on the target temperatureerature. Calling 
#         getPowerConsumption() counts as 1 second passed.   
# Presumptions: 
#   - No active cooling system is implemented; cooling occurs naturally.
#   - Heat loss is calculated based on a simple linear model.
#   - The class assumes a linear relationship between energy input and temperatureerature change.     
# Written by: Jip  

class symFermentation:
  def __init__(self, mass, specificHeat, maxPower, initial_temperature_c, warmtegeleiding_coeff, area, thickness, surroundingTemperature):
    self.mass = mass
    self.specificHeat = specificHeat
    self.maxPower = maxPower
    self.temperature = initial_temperature_c
    self.storedEnergy = mass * specificHeat * self.__calcCelciusToKelvin(initial_temperature_c)

    self.heatCofficient = warmtegeleiding_coeff
    self.area = area
    self.thickness = thickness
    self.surroundingTemperature = surroundingTemperature


  # Calculate the energy needed to reach a new temperatureerature
  def __calcEnergyNeeded(self, newTemperature):
    Q = self.mass * self.specificHeat * (newTemperature - self.temperature)
    return Q
  
  # Calculate lossed energy by heat transfer
  def __calcHeatLossEnergy(self):
    return (self.heatCofficient * self.area * (self.temperature - self.surroundingTemperature) / self.thickness)
  
  # Convert Celsius to Kelvin
  def __calcCelciusToKelvin(self, temperature_c):
    return temperature_c + 273.15
  
  # Return the current temperatureerature
  def getTemperature(self):
    return self.temperature
  
  # Get the stored energy based on current temperatureerature
  def getStoredEnergy(self):
    return self.storedEnergy  
  
  # Set new target temperatureerature
  def setNewTemperature(self, newTemperature):
    self.targetTemperature = newTemperature

  # Get current power consumption in kW
  def getPowerConsumption(self):
    # Calculate heat loss energy per second
    energyLoss = self.__calcHeatLossEnergy()
    # Check if new temperatureerature is set
    if self.temperature != self.targetTemperature:
      # More energy required to reach target temperatureerature
      energyNeeded = self.__calcEnergyNeeded(self.targetTemperature)
      # Max power available in Joules per second
      maxPowerS = self.maxPower * 1000
      # Remove heat loss from available power
      availablePowerS = maxPowerS - energyLoss
      # Add energy to stored energy
      if energyNeeded > 0:
        # Heating up
        energyToAdd = min(energyNeeded, availablePowerS)
        self.storedEnergy += energyToAdd
        self.temperature += energyToAdd / (self.mass * self.specificHeat)
        return (energyToAdd + energyLoss) / 1000  # in kW
      else:
        # Cooling down (No active cooling, so just let it cool naturally)
        self.storedEnergy -= energyLoss
        self.temperature -= energyLoss / (self.mass * self.specificHeat)
        return 0
    else:
      # Maintain current temperatureerature, only heat loss needs to be compesated
      return energyLoss / 1000  # in kW
