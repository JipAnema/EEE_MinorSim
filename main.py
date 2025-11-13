import fermentatiewarmte as fw
import matplotlib.pyplot as plt
import numpy as np
import csv

with open('energieprijs.csv', mode='r') as energieprijs_file:
    reader = csv.reader(energieprijs_file)
    energieprijs_data = {rows[0]:float(rows[1]) for rows in reader}
  
timesteps = 240 * 3600  # seconds to simulate
total_power = 0 
a = []

fermentatie1 = fw.FermentatieWarmte(100000, 4186, 20, 20.0, 0.1, 20, 0.05, 10.0 )  # 1000 kg, water, 20 kW heater, initial temp 20C, warmtegeleiding_coeff 0.1, oppervlakte 20m2, dikte 0.05m, omgeving temp 10C
setpoint = 40.0  # Target temperature in Celsius
secondspassed = 0
print("Initial Temperature:", fermentatie1.get_temp(), "°C")
fermentatie1.set_newtemperature(setpoint)  # Set target temperature to 25C
for t in range(timesteps):
  power_consumption = fermentatie1.getPowerConsumption()
  secondspassed += 1
  total_power += power_consumption
  if np.mod(t, 900) == 0:  # Every 15 minutes update price
    current_minute = t // 60
    hour = (current_minute // 60) % 24
    minute = current_minute % 60
    time_key = f"{hour:02d}:{minute:02d}"
    if time_key in energieprijs_data:
      current_price = energieprijs_data[time_key]
    else:
      current_price = 0.20  # Default price if time not found
     
  if np.mod (t, 6) == 0:  # Print every 10 minutes
    a.extend([power_consumption])
print("Minutes Passed:", secondspassed / 60)
print("Final Temperature:", fermentatie1.get_temp(), "°C")
print("Total Power Consumption:", total_power / 3600, "kWh")
  
plt.plot(a)
plt.ylabel('Power Consumption (kW)')
plt.xlabel('Time (minutes)')
plt.show()
