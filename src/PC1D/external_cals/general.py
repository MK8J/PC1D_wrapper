
import numpy as np
import matplotlib.pylab as plt
import scipy.integrate as inte
import scipy.optimize as opt
import scipy.constants as const
import semiconductor.electrical.resistivity as semel
from semiconductor.general_functions.carrierfunctions import get_carriers
'''
This is a moduel used for determinaing values from
PC1D outputs, that are not provided directly as an
output. One limitations is the correct things must be plotted
in the active graph.
'''


def _check_fields(must_have, one_required, values):
    '''
    Checks it the required first and one required fieds are there
    if not returns None,
    Else returns the list of fields
    '''

    # check must have fields are there
    for i in must_have:

        if i in values:
            pass
        else:
            print(i + ' is a required PC1D output to perform this calculation')
            must_have = None

    # check is one of fields exist
    is_one_in = True
    if one_required != [] and must_have is not None:
        is_one_in = False
        for i in one_required:
            if i in values:
                must_have.append(i)
                is_one_in = True
                break

    if not is_one_in or must_have is None:
        must_have = None
        print('The outputs received were:')
        print([i for i in values])

    return must_have


def lifetime(PC1D_output, Plot=False, Print=False, carrier=None):
    """
    takes any PC1D image as input.
    Requires the active image to have the an excess carrier density and
    the generation rate
        carrier: electron|hole|None*, choose which carrier lifetime to
                 calculate, If None, chooses the first on provided
        Plot: True|False*, will plot the lifetime_n
        Print: True|False*, will print the lifetime
        Return: True|False*, will return the lifetime
    returns lifetime in s
    """

    required_fields = ['Distance_from_Front', 'Generation_Rate']
    optional_fields = ['Excess_Electron_Density', 'Excess_Hole_Density']

    # put it in cm

    if carrier is not None:
        # print'gothere'

        new_field = [field
                     for field in optional_fields
                     if carrier.lower() in field.lower()]

        required_fields.append(new_field[0])
        optional_fields = []

    List_of_Values = _check_fields(required_fields,
                                   optional_fields,
                                   PC1D_output.dtype.names)

    if List_of_Values is not None:
        # print List_of_Values[-1]
        average_carriers = inte.simps(
            PC1D_output[List_of_Values[-1]],
            PC1D_output['Distance_from_Front'],
        )

        # print '{0:.2e}'.format(average_carriers)

        generation = inte.simps(
            PC1D_output['Generation_Rate'],
            PC1D_output['Distance_from_Front']
        )

        tau = average_carriers / generation

    else:

        tau = None

    if Print:
        print(tau, '\t', average_carriers)

    if Plot:

        plt.plot(
            PC1D_output['Distance_from_Front'],
            PC1D_output['Generation_Rate'],
        )

        plt.plot(
            PC1D_output['Distance_from_Front'],
            PC1D_output[List_of_Values[-1]],
        )
        plt.loglog()

    return tau, average_carriers / PC1D_output['Distance_from_Front'][-1]


def iVoc_conductance(PC1D_output, Na=1e16, Nd=0):
    """
    takes any PC1D image as input.
    provide PC1D output data, and calculates the iVoc from the conductance
        PC1D_output: (ndarray)
                    the PC1D output
    Currently does not work as have to get a mobility model working.
    """

    ni = 1e10
    T = 300.

    required_fields = ['Distance_from_Front',
                       'Cumulative_Excess_Conductivity']
    optional_fields = []

    List_of_Values = _check_fields(required_fields,
                                   optional_fields,
                                   PC1D_output.dtype.names)

    res = semel.Resistivity(material='Si', Na=Na, Nd=Nd, nxc=1e10)
    # print(res.cal_dts)
    # print ()

    if List_of_Values is not None:
        total_ex_conductance = PC1D_output[
            'Cumulative_Excess_Conductivity'][-1]
        width = PC1D_output['Distance_from_Front'][-1] * 100

        def conductance_min(nxc):

            cond = res._conductivity(nxc=nxc)[0] * width
            dark_cond = res._conductivity(nxc=1)[0] * width

            return cond - total_ex_conductance - dark_cond

        nxc = opt.newton(conductance_min, x0=1e15)

        ne, nh = get_carriers(Na, Nd, nxc, T, 'Si', ni=1e10)
        Vt = const.k * T / const.e

        iVoc = Vt * \
            np.log((ne * nh / ni**2))

        # print('Not finished yet', result)
    else:
        iVoc = None

    return iVoc


def PL_simple(PC1D_output):
    """
    Calculates the PL intensity as the product of the excess carrier densities.

    inputs
        PC1D_output: (ndarray)
                    the PC1D output
    output:
        PL intensity: (float)
    """

    required_fields = ['Distance_from_Front',
                       'Electron_Density',
                       'Hole_Density']

    optional_fields = []

    List_of_Values = _check_fields(required_fields,
                                   optional_fields,
                                   PC1D_output.dtype.names)

    if List_of_Values is not None:
        # print List_of_Values[-1]
        pl = inte.simps(
            PC1D_output['Electron_Density'] *
            PC1D_output['Hole_Density'] - 1e20,
            PC1D_output['Distance_from_Front'],
        )
        # print (PC1D_output['Electron_Density'] *
        #     PC1D_output['Hole_Density'] - 1e20)

    else:
        pl = None

    return pl
