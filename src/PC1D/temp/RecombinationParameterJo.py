
from PC1D import PC1D as PC1Da
import matplotlib.pylab as plt
import numpy as np
import scipy.constants as const
import sys
import os

sys.path.append('C:\Users\mattias\Dropbox\CommonCode\SintonExtraction')

import ExtractFromSinton as ES
import scipy.optimize as sopt

import time

prm_loc = 'RecombinationParameterJo.prm'
exe_loc = 'D:\pc1d\PC1Dmod6-1\cmd-pc1d6-2.exe'
bat_loc = 'RecombiationParameterJo.txt'
PC1D = PC1Da(prm_loc, BatchFile=bat_loc, PC1D_exe=exe_loc)


def calc_PC_from_voltage(inf_dic, data):

    conductance = np.copy(data['Photovoltage'])
    # conductance -= inf_dic['C']
    conductance = inf_dic['A'] * \
        np.power(conductance, 2) + inf_dic['B'] * conductance
    return conductance


def plot_exp_data(fname, ax):
    A = 0.00027
    B = 0.02984
    C = 0.00211

    data = np.genfromtxt(
        fname, delimiter='\t',
        names=['time', 'pc'],
        usecols=(0, 1))

    data['pc'] -= C
    data['pc'] = A * \
        np.power(data['pc'], 2) + B * data['pc']
    ax.plot(data['time'], data['pc'], 'k.', label='measured data')
    ax.set_ylim(top=np.amax(data['pc']) * 1.2)


def gen_file(fname,
             optical_constant=1.03,
             ref_cell=0.0103765809454623,
             PC1D_conv=0.310322849):
    '''
    fname:
        a data file with everything
    optical_cosntant:
        the sinton optical constant
    ref_cell:
        the sinton ref_cell calibration
    PC1D_conv:
        the intensity value that makes the
        simulation have a Isc of 38 mA
    '''
    data = np.genfromtxt(
        fname, delimiter='\t',
        names=['time', 'ref'],
        usecols=(0, 2))

    # ref voltage into sun

    data['ref'] /= ref_cell
    print np.amax(data['ref']) * 38 * optical_constant
    data['ref'] *= optical_constant

    data['ref'] *= PC1D_conv
    # let the first point be the SS one
    # data['ref'][0] = PC1D_conv
    # data['time'][0] = 0

    np.savetxt('exp.lgt', data)

    return data


def determine_PC1D_optical_constant(inf_dic):
    '''
    this file finds the value that is to be sent to PC1D
    such that the simulated cell outputs 38 mA/cm^-2
    '''
    header = [
        'FrS(1)', 'RrS(1)', 'BulkTau(1)', 'BkgndDop(1)',
        'Thickness(1)', 'FrCharge(1)',
        'BaseResTR(1)']

    values = [0, 0, 1e6, inf_dic['Doping'],
              inf_dic['Thickness'] * 1e4, 1e13,
              0.1, 0, .175]

    PC1D.PrepareBatchFile(header, values)

    lt_int = np.genfromtxt('exp.lgt', names=['time', 'intensity'])

    data = PC1D.run_PC1D()
    data['Base_Current'] = abs(data['Base_Current'])

    current = np.interp(
        lt_int['time'], data['Elapsed_Time'], data['Base_Current'], right=0)
    # print current
    ratio = current / 0.038 / lt_int['intensity']
    ratio = 1. / ratio[current > 0]

    print ratio
    print np.median(ratio)
    print lt_int['intensity'][current < 0.038][0]

    # print ratio, current
    # print ratio, np.log10(1./ratio)
    # plt.figure('things')
    # plt.plot(lt_int['time'], current, 'bo')
    # plt.plot(data['Elapsed_Time'], data['Base_Current'], 'go')
    # plt.plot(lt_int['time'], lt_int['intensity'], '.')

    # plt.semilogy()
    # plt.show()
    # print data.dtype.names
    # print data['Base_Current']
    return np.median(ratio)


def create_gen_file(time, ref_V,
                    optical_constant=1.03,
                    ref_cell=0.0103765809454623,
                    PC1D_conv=0.0310322849):
    '''
    fname:
        a data file with everything
    optical_cosntant:
        the sinton optical constant
    ref_cell:
        the sinton ref_cell calibration V/sun
    PC1D_conv:
        the intensity value that makes the
        simulation have a Isc of 38 mA
    '''

    # ref voltage into sun
    ref_V /= ref_cell
    # print np.amax(data['ref']) * 38 * optical_constant
    ref_V *= optical_constant

    ref_V *= PC1D_conv
    # let the first point be the SS one
    # data['ref'][0] = PC1D_conv
    # data['time'][0] = 0
    time = np.append(time, time[-1] + 1e-6)
    ref_V = np.append(ref_V, [0])
    # ref_V /= ref_V/.1
    data = np.vstack((time.T, ref_V.T)).T
    np.savetxt('exp.lgt', data)

    return data


def cal_j0_froms(s, doping):
    j0 = const.e * s / doping * 9.65e9 * 9.65e9
    return j0


def _plot(time, conductance, ax):
    data = PC1D.run_PC1D()

    ax.plot(data['Elapsed_Time'], data[
            'Cumulative_Excess_Conductivity'], label='Simulated data')
    ax.plot(time, conductance, 'k.', label='measured data')
    ax.legend(loc=0)
    plt.show()


def run_PC1D(guess, inf_dic):

    # PC1D = PC1Da(prm_loc, BatchFile=bat_loc, PC1D_exe=exe_loc)

    header = [
        'FrS(1)', 'RrS(1)', 'BulkTau(1)', 'BkgndDop(1)', 'Thickness(1)']
    values = [10**guess[1], 10**guess[1], guess[0],
              inf_dic['Doping'], inf_dic['Thickness'] * 1e4]

    PC1D.PrepareBatchFile(header, values)

    data = PC1D.run_PC1D()

    # plt.figure('fitting')
    # plt.plot(data['Cumulative_Excess_Conductivity'])

    return data


def Fit_J0(guess, inf_dic, measured_data):
    srv = abs(guess)
    # PC1D = PC1Da(prm_loc, BatchFile=bat_loc, PC1D_exe=exe_loc)
    # print srv,
    header = [
        'FrS(1)', 'RrS(1)', 'BulkTau(1)', 'BkgndDop(1)', 'Thickness(1)']
    values = [srv, srv, 10000,
              inf_dic['Doping'], inf_dic['Thickness'] * 1e4]

    PC1D.PrepareBatchFile(header, values)

    data = PC1D.run_PC1D()

    # print data['Elapsed_Time'].shape
    # print measured_data['Time in s'].flatten().shape
    # print measured_data['Conductivity increase'].flatten().shape
    # print
    conductance = np.interp(
        data['Elapsed_Time'],
        measured_data['Time in s'].flatten(),
        measured_data['Conductivity increase'].flatten(),
        right=0)

    plt.figure('fitting')
    plt.plot(data['Elapsed_Time'], data['Cumulative_Excess_Conductivity'], '.')
    plt.plot(data['Elapsed_Time'], conductance, 'ko')
    # plt.show()
    plt.figure('Error')
    index = conductance != 0
    error = abs(conductance[
                index] - data['Cumulative_Excess_Conductivity'][index]) / conductance[index]
    err = np.sum(error)
    plt.plot(srv, err, '.')
    # plt.loglog()

    # print err
    # print guess, err
    return err


def Auto_fit_J0(fname):

    inf_dic = ES.Sinton2015_ExtractUserData(fname, os.getcwd())
    file_path = os.path.join(os.getcwd(), fname)
    data = ES.Sinton2015_ExtractRawData(file_path)

    create_gen_file(
        data['Time in s'],
        data['Reference Voltage'],
        inf_dic['OpticalConstant'],
        inf_dic['RefCell'])

    PC1D_optical_constant = determine_PC1D_optical_constant(
        inf_dic)

    print 'PC1D optical cosntant', 'ref cell', 'cell\'s optica cosntant'
    print PC1D_optical_constant, inf_dic['RefCell'], inf_dic['OpticalConstant']

    create_gen_file(
        data['Time in s'],
        data['Reference Voltage'],
        inf_dic['OpticalConstant'],
        inf_dic['RefCell'],
        PC1D_optical_constant)

    # print 'The optical contant is', PC1D_optical_constant
    # print data.dtype.names

    # tau and SRV
    # x0 = 0
    # res = []
    # ss = np.logspace(2, 3, 2)
    # for s in ss:
    #     x0 = s
    #     res.append(Fit_J0(np.log10(x0), inf_dic, data))

    # plt.figure('err')
    # plt.plot(ss, res)

    # run_PC1D(x0, inf_dic)
    for i in range(5):
        start = time.clock()
        answer = sopt.minimize_scalar(
            Fit_J0,
            # np.log10(x0),
            args=(inf_dic, data),
            method='brent')
        fin = time.clock()
        print 'Brent: It took', start - fin, 's for  the result:', answer['x']

    # for i in range(5):
    #     start = time.clock()
    #     answer = sopt.minimize_scalar(
    #         Fit_J0,
    #         # np.log10(x0),
    #         args=(inf_dic, data),
    #         method='bounded')
    #     fin = time.clock()
    #     print 'bounded: It took', start - fin, 's for  the result:', answer['x']

    for i in range(5):
        start = time.clock()
        answer = sopt.minimize_scalar(
            Fit_J0,
            # np.log10(x0),
            args=(inf_dic, data),
            method='golden')
        fin = time.clock()
        print 'golden: It took', start - fin, 's for  the result:', answer['x']

    fig, ax = plt.subplots()
    _plot(data['Time in s'], data['Conductivity increase'], ax)

    print answer['x']
    print cal_j0_froms(answer['x'], inf_dic['Doping']), '1.01e-12 is what excel says'
    print

    plt.show()


def Manual_fit_J0(inf_dic, tau=1e6, SRV=100):
    '''

inpits:
    inf_dic: (dictionary)
        A diction with sample info. It must contain doping, and thickness.
    tau: (float, optional)
        The inital value used in PC1D for fitting
    SRV: (float, optiona)
        The inital value used in PC1D for fitting
'''

    gen_file('exp_data.dat')

    # tau = 1e6 / 2  # us

    fig, ax = plt.subplots(1)
    # for SRV in [330]:

    header = [
        'FrS(1)', 'RrS(1)', 'BulkTau(1)', 'BkgndDop(1)', 'Thickness(1)']
    values = [SRV, SRV, tau, inf_dic['Doping'], inf_dic['Thickness'] * 1e4]
    PC1D.PrepareBatchFile(header, values)

    data = PC1D.run_PC1D()

    ax.plot(data['Elapsed_Time'], data['Cumulative_Excess_Conductivity'], '--',
            label=str(cal_j0_froms(SRV, inf_dic['Doping'])) + ' A/cm^2')
    # print data['Cumulative_Excess_Conductivity']
    # print data[data.dtype.names[-1]][-1]

    plot_exp_data('exp_data.dat', ax)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Conductance (s)')
    ax.legend(loc=0)
    # ax.semilogx()
    plt.show()

    # inf_dic =  ES.Sinton2015_ExtractUserData('80-35D-1.xlsm', os.getcwd())
    #{'SampleType': 'p-type', 'xlBook': <COMObject Open>, 'Thickness': 0.023, 'xlApp': <COMObject Excel.Application>, 'xlSheet': <COMObject <unknown>>, 'Resisitivity': 1.0, 'File': '80-35D-1.xlsm', 'OpticalConstant': 0.85, 'WaferName': '80-35D', 'File_path': 'C:\\Users\\mattias\\Dropbox\\CommonCode\\PC1D_wrapper\\80-35D-1.xlsm', 'Dir': 'C:\\Users\\mattias\\Dropbox\\CommonCode\\PC1D_wrapper', 'AnalysisMode': 'Generalized (1/1)'}
    # test1(inf_dic)
Auto_fit_J0('80-35D-1.xlsm')
