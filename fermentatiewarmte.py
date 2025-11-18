# Name: fermentatiewarmte.py
# Description: Class to calculate power consumption for fermentation heat control
# Usage:  Import the class and create an instance with the required parameters 
#         to manage fermentation temperature. Calling getPowerConsumption() will return
#         the current power consumption in kW based on the target temperature. Calling 
#         getPowerConsumption() counts as 1 second passed.   
# Presumptions: 
#   - No active cooling system is implemented; cooling occurs naturally.
#   - Heat loss is calculated based on a simple linear model.
#   - The class assumes a linear relationship between energy input and temperature change.     
# Written by: Jip  

class FermentatieWarmte:
  def __init__(self, mass_kg, soortelijke_warmte_jc_kg, max_power_kw, initial_temp_c, warmtegeleiding_coeff, area_m2, thickness_m, suround_temp_c):
    self.mass_kg = mass_kg
    self.soortelijke_warmte_jc_kg = soortelijke_warmte_jc_kg
    self.max_power_kw = max_power_kw
    self.temp = initial_temp_c
    self.stored_energy = mass_kg * soortelijke_warmte_jc_kg * self.__calc_celciustokelvin(initial_temp_c)

    self.heatcofficient = warmtegeleiding_coeff
    self.area_m2 = area_m2
    self.thickness_m = thickness_m
    self.suround_temp_c = suround_temp_c


  # Calculate the energy needed to reach a new temperature
  def __calc_energieneeded(self, nieuw_temp_c):
    Q = self.mass_kg * self.soortelijke_warmte_jc_kg * (nieuw_temp_c - self.temp)
    return Q
  
  # Calculate lossed energy by heat transfer
  def __calc_heatlossenergy(self):
    return (self.heatcofficient * self.area_m2 * (self.temp - self.suround_temp_c) / self.thickness_m)
  
  # Convert Celsius to Kelvin
  def __calc_celciustokelvin(self, temp_c):
    return temp_c + 273.15
  
  # Return the current temperature
  def get_temp(self):
    return self.temp
  
  # Get the stored energy based on current temperature
  def get_stored_energy(self):
    return self.stored_energy  
  
  # Set new target temperature
  def set_newtemperature(self, nieuw_temp_c):
    self.targettempp = nieuw_temp_c

  # Get current power consumption in kW
  def getPowerConsumption(self):
    # Calculate heat loss energy per second
    energie_loss_p = self.__calc_heatlossenergy()
    # Check if new temperature is set
    if self.temp != self.targettempp:
      # More energy required to reach target temperature
      energie_needed_j = self.__calc_energieneeded(self.targettempp)
      # Max power available in Joules per second
      max_power_j_per_s = self.max_power_kw * 1000
      # Remove heat loss from available power
      available_power_j_per_s = max_power_j_per_s - energie_loss_p
      # Add energy to stored energy
      if energie_needed_j > 0:
        # Heating up
        energie_to_add = min(energie_needed_j, available_power_j_per_s)
        self.stored_energy += energie_to_add
        self.temp += energie_to_add / (self.mass_kg * self.soortelijke_warmte_jc_kg)
        return (energie_to_add + energie_loss_p) / 1000  # in kW
      else:
        # Cooling down (No active cooling, so just let it cool naturally)
        self.stored_energy -= energie_loss_p
        self.temp -= energie_loss_p / (self.mass_kg * self.soortelijke_warmte_jc_kg)
        return 0
    else:
      # Maintain current temperature, only heat loss needs to be compesated
      return energie_loss_p / 1000  # in kW
