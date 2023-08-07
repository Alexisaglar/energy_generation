import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pvlib import pvsystem
from datetime import datetime
from parameters_pv import parameters

series_panel = 5
parallel_panel = 3 
#CFPV Data
PCE_ref_CFPV = 10
#y=mx+b
slope_2x_enhance = (-1/100)
constant_2x_enhance = 20
weather_file = "Newcastle_data_1_min_January"

with open(f'{weather_file}.csv', newline='') as weather_data:
    irradiance = pd.read_csv(weather_data, skiprows=42, delimiter=';')
    irradiance.rename(columns={irradiance.columns[0]: irradiance.columns[0].lstrip('#')}, inplace=True)


print(irradiance)

IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
    Jul_avg_GHI['GHI'],
    Jul_avg_GHI['Temperature'],
    alpha_sc=parameters['alpha_sc'],
    a_ref=parameters['a_ref'],
    I_L_ref=parameters['I_L_ref'],
    I_o_ref=parameters['I_o_ref'],
    R_sh_ref=parameters['R_sh_ref'],
    R_s=parameters['R_s'],
    EgRef=1.121,
    dEgdT=-0.0002677
)

# plug the parameters into the SDE and solve for IV curves:
curve_info = pvsystem.singlediode(
    photocurrent=IL,
    saturation_current=I0,
    resistance_series=Rs,
    resistance_shunt=Rsh,
    nNsVth=nNsVth,
    ivcurve_pnts=100,
    method='lambertw'
)

Cell_result = pd.DataFrame({
    'i_sc': curve_info['i_sc'],
    'v_oc': curve_info['v_oc'],
    'i_mp': curve_info['i_mp'],
    'v_mp': curve_info['v_mp'],
    'p_mp': curve_info['p_mp'],
}).set_index(Jul_avg_GHI.index)

Total_PV = pd.DataFrame({
    'Irradiance': Jul_avg_GHI['GHI'],
    'V': Cell_result['v_mp']*Series_panel,
    'I': Cell_result['i_mp']*Parallel_panel,
})

Total_PV['P'] = Total_PV['I']*Total_PV['V']
#calculating other technology performance
Total_PV['PCE@GHI'] = Slope_2x_enhance * Total_PV['Irradiance'] + Constant_2x_enhance  #y = mx+b
Total_PV['P_CFPV'] = Total_PV['P']*(Total_PV['PCE@GHI']/PCE_ref_CFPV) # P = P_silicon * (Enhanced_PCE @ Iradiance level / Silicon PCE efficiency) 
    
print(Total_PV)
plt.plot(Total_PV['Irradiance'])
plt.show()
plt.plot(np.arange(0,288,1), Total_PV[['P','P_CFPV']])
Total_PV[['P','P_CFPV']].to_csv(f'Profile_June.csv') 
plt.show()
