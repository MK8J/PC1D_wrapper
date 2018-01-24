

import numpy as np
import matplotlib.pylab as plt
import subprocess
import itertools
import scipy.integrate as inte

import sys
import os

import re

from io import StringIO, BytesIO


class PC1D():
    '''
    A class that enables sending of batch files to PC1D
    '''
    # PC1D_exe = r"D:\ownCloud1\UNSW\Software\pc1d\pc1d5\cmd-pc1d5-2.exe"
    dir_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'Files')
    PC1D_exe = os.path.join(dir_path, 'cmd-PC1D6-2.exe')
    asc2prm = os.path.join(dir_path, 'convert_ascii_to_prm.exe')
    prm2asc = os.path.join(dir_path, 'convert_prm_to_ascii.exe')

    __temp1 = os.path.join(dir_path, 'temp1.txt')
    __temp2 = os.path.join(dir_path, 'temp.txt')

    def __init__(self, PC1D_prm, BatchFile=None):
        '''
        initalises the PC1D class

        inputs:
            PC1D_prm: (str)
                location of the prm file to use
            BatchFile: (optional) (str)
                location of the batch input file to use
            PC1D_exe: (optional) (str)
                location of the PC1D exe file
        '''
        self.PC1D_prm = PC1D_prm
        self.BatchFile = BatchFile

        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
            if BatchFile is not None:
                print(
                    'Warning batch files don\'t work on linux or mac, the batch file has been removed')
                self.BatchFile = None

        # print(self.dir_path)

    @property
    def setQSSPCFlash(self):
        '''
        Sets the light source to be the QSSPC x5dflash

        This is done by setting the following values in the prm file:
            1. m_SpectrumFile as x5dflash.spc
            2. m_IntensityFile intensity as m_IntensityFile
        '''
        params = {
            'CLight::m_SpectrumFile': 'x5dflash.spc',
            'CLight::m_IntensityFile': 'qsspc_pulse_long_increasing.lgt'
        }
        lab, val = [], []
        for k, v in params.items():
            lab.append(k)
            val.append(os.path.join(self.dir_path, v))
            if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
                val[-1] = 'z:' + val[-1]
            # else:
            #     print('sys.platform', sys.platform)
            #     print(val[-1])

        self.alterPRM(lab, val)

    @property
    def StandardSiliconConstants(self):
        '''
        Sets ni as si_green2008,
        absorption coefficient and k as green2008
        si_updated is used for
        Using Jo not S
        '''
        params = {
            'CMaterial::m_IndexFilename': 'si_green2008.inr',
            'CMaterial::m_Filename': 'si_updated.mat',
            'CMaterial::m_AbsFilename': 'si300_green2008.abs',
        }
        lab, val = [], []
        for k, v in params.items():
            lab.append(k)
            val.append(os.path.join(self.dir_path, v))
            if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
                val[-1] = 'z:' + val[-1]

        self.alterPRM(lab, val)

    def J0orSeff(self, state):
        '''
        provide J0 or Seff.
        True/1 is J0
        False/0 is seff
        '''
        params = {'m_FrontJo': int(state),
                  'm_RearJo': int(state),
                  }
        lab, val = [], []
        for k, v in params.items():
            lab.append(k)
            val.append(v)

        self.alterPRM(lab, val)

    def alterPRM(self, param, value):
        '''
        Adjusts the PRM file to have the selected paramters.

        param is a list of parameters as found in the ascii version of the prm file. The value is the corresponding value it is to be set as.
        '''
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
            process = subprocess.run(
                ['wine', self.prm2asc, self.PC1D_prm, self.__temp1], stdout=subprocess.PIPE)

        elif sys.platform == "win32":

            process = subprocess.run(
                [self.prm2asc, self.PC1D_prm, self.__temp1], stdout=subprocess.PIPE)

        # process.kill()
        with open(self.__temp1, 'r') as f:
            s = f.read()
        f.closed

        for num, val in enumerate(param):
            s = re.sub('{0}=(.?)*'.format(val),
                       '{1}={0}'.format(value[num], val), s)

        with open(self.__temp2, 'w') as f:
            f.write(s)
        f.closed

        if sys.platform == "linux" or sys.platform == "linux2"or sys.platform == 'darwin':
            process = subprocess.run(
                ['wine', self.asc2prm,  self.__temp2, self.PC1D_prm], stdout=subprocess.PIPE)

        elif sys.platform == "win32":
            process = subprocess.run(
                [self.asc2prm,  self.__temp2, self.PC1D_prm], stdout=subprocess.PIPE)

    # def PrepareBatchFile(self, parName, values):
    #     '''
    #     A function that overwrites the batch file that is used for batch mode in PC1D.
    #     It only writes a single line to the batch file.
    #
    #     This assumes that .prm file has had the batch file set internally.
    #     The batch file path is set in this class, during the class initalisation.
    #
    #     inputs:
    #         header: (list of str, length m)
    #             The parameter names, taken from PC1D's help files. These form the header for the
    #             batch file.
    #         values: (list of values, length m)
    #             A list of values to be written to be batch file
    #             one value per parameter name.
    #
    #     '''
    #     with open(self.BatchFile, 'w') as f:
    #         # f.write('\n')
    #
    #         if len(parName) == 1:
    #             f.write(parName[0])
    #
    #         else:
    #             f.write(parName[0])
    #             for i in parName[1:]:
    #                 f.write('\t' + i)
    #
    #         f.write('\n')
    #
    #         for i in values:
    #             f.write(str(i) + '\t')

    def run(self):
        '''
        runs PC1D

        output:
            the data stored in the active plot
        '''
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
            process = subprocess.Popen(
                ['wine', self.PC1D_exe, self.PC1D_prm], stdout=subprocess.PIPE)

        elif sys.platform == "win32":
            process = subprocess.Popen(
                [self.PC1D_exe, self.PC1D_prm], stdout=subprocess.PIPE)

        (output, err) = process.communicate()

        if sys.version_info >= (3, 0):
            data_str = BytesIO(output)
        else:
            data_str = StringIO(output)

        process.kill()
        # print(str(data_str.getvalue(), 'utf-8'))

        if data_str is not None:

            try:
                data = np.genfromtxt(data_str, delimiter='\t', names=True)
            except:
                print(BytesIO(output).read())
                data = None
        else:
            print('nothing read')

        return data

    def permute_values(self, values):
        '''
        creates all the permiations of a range of values.
        This is usedful when coupled with the PrepareBatchFile function.
        This can be usedful for a batch input of PC1D

        inputs:
            values: (list)
                a list of values to be peremutated.
        '''
        return list(itertools.product(*values))


class CaculateFromPC1DOutput():
    '''
    This is a class used for determinaing values from
    PC1D outputs, that are not provided directly as an
    output. One limitations is the correct things must be plotted
    in the active graph.
    '''

    def _check_fields(self, must_have, one_required, values):
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

    def lifetime_from_PC1D(self, PC1D_output, Plot=False, Print=False, carrier=None):
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

        List_of_Values = self._check_fields(required_fields,
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


if __name__ == "__main__":
    # a short example of how to measure the effective lifetime
    prm = 'D:\pc1d\pc1d5\StandardWafer_test.prm'
    batch = 'D:\pc1d\BatchFile.txt'
    pc1d = PC1D(prm, batch)
    CPC1D = CaculateFromPC1DOutput()
    print(CPC1D.lifetime_from_PC1D(pc1d.run_PC1D(), carrier=None, Plot=True) * 1e6)
    plt.show()
