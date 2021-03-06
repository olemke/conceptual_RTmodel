'''
This should be an easy one-layer extionction model with an source and an receiver
'''

import numpy as np
import matplotlib.pyplot as plt
import typhon as ty
from submodules import plotting_routines as pr


def main():
    ### Settings
    #model
    ds = 1 # m
    delta_angle = 10
    elevation_array = np.arange(-80,81,delta_angle)  # []
    reflection_type = 1         # 0= specular, 1= lambert

    # Source
    Solar_Intensity = 1000
    Sun_height = 1000
    Sun_angle = 0

    # Atmosphere and Boundary
    atm_height = 200 # km
    alpha = 1e-4 # 1/m
    ground_albedo = 0.7
    SIGMA = 1e-30           # absorption cross section  - scattering cross section(6.2403548416*10**(-32))

    # Receiver
    view_angle = 180
    receiv_height = 20 # km

    # MSIS
    PATH = '/Users/jonpetersen/data/data_BA/'
    MSIS_DATEI = 'MSIS/MSIS_18072300_new.txt'
    msis = open(PATH + MSIS_DATEI)      # 0 Height, km | 1 O, cm-3 | 2 N2, cm-3 | 3 O2, cm-3 | 4 Mass_density, g/cm-3 | 5 Ar, cm-3
    MSISdata = np.genfromtxt(msis, skip_header=11)
    MSISalt = MSISdata[:,0]        # Altitude
    MSISdens = (MSISdata[:,1] + MSISdata[:,2] + MSISdata[:,3] + MSISdata[:,4])*10**6    # Dichten von O, N2, O2 und Ar addieren für Gesamtdichte / cm^-3, nur jeder 5. Bin

    rad_array = np.zeros((2,len(elevation_array),int(atm_height*1000/ds))) # down and upward radiation array with an spacing of ds
    height_array = np.linspace(0,atm_height,int(atm_height*1000/ds))


    alpha_array = []#np.zeros((int(atm_height*1000/ds)))
    for height in height_array:
        dens = MSISdens[argclosest(height, MSISalt)]
        alpha_array.append(dens*SIGMA)


    '''
    Integration
    '''
    ### DOWNWARD
    rad_array[0,argclosest(Sun_angle,elevation_array)] = path_integartion_angle(Solar_Intensity, int(atm_height*1000/ds), alpha_array[::-1])

    ### GROUND INTERACTION
    for ang in range(len(elevation_array)):

        if reflection_type == 1:
            ground_value = rad_array[0,argclosest(Sun_angle,elevation_array),-1] * ground_albedo * np.cos(elevation_array[ang]*np.pi/180)


        ### UPWARD
        rad_array[1,ang] = path_integartion_angle(ground_value, int(atm_height*1000/ds), alpha_array, ang)



    ty.plots.styles.use(["typhon", 'typhon-dark'])
    fig, ax0 = plt.subplots(ncols=1)
    plot_height = 10
    labels = ['multilayer extinction',f"angle / $^\circ$",f"Height / km",r'Intensity / a.u.']
    print(height_array[0:argclosest(plot_height,height_array):1000])
    pr.plot_angle(rad_array[1,:,0:argclosest(plot_height,height_array):1000], elevation_array, height_array[0:argclosest(plot_height,height_array):1000], fig=fig, labels=labels, ax=ax0)
    fig.savefig('./../plots/angle_dependency')
    plt.show()



def argclosest(value, array):
    '''Returns the index in ``array`` which is closest to ``value``.'''
    return np.abs(array - value).argmin()


def path_integartion_angle(rad_init, size, alpha, angle = 0, ds = 1):
    rad_array = [rad_init]
    for id in range(1,size):
        rad_array.append(rad_array[-1] * np.exp(-alpha[id]*ds/np.cos(angle*np.pi/180)))
    return np.array(rad_array)


def plot_intensity(rad_array, height_array, ax=None):
    if ax is None:
        ax = plt.gca()

    ax.plot(rad_array[0][::-1], height_array, label = 'downward')
    ax.plot(rad_array[1], height_array, label = 'upward')
    ax.set_xlim(0,1000)
    #ax.set_ylim(0,10)
    ax.set_xlabel(f"Intensity / a.u.")
    ax.set_ylabel(f"Height / km")
    ax.set_title('multilayer extionction')
    ax.legend(loc='upper left')




if __name__ == "__main__":
    try:
        plt.close('all')
    except:
        pass
    main()
