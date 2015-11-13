

import numpy as np
import matplotlib.pylab as plt
import subprocess
from StringIO import StringIO
import itertools
import scipy.integrate as inte


class PC1D():
    PC1D_File = "D:\PC1D\PC1D5\cmd-pc1d5-2.exe"

    def __init__(self, PC1D_prm, BatchFile=None):
        self.PC1D_prm = PC1D_prm
        self.BatchFile = BatchFile

    def PrepareBatchFile(self, header, values):
        # print values
        with open(self.BatchFile, 'w') as f:
        # f.write('\n')

            if len(header) == 1:
                f.write(header[0])

            else:
                f.write(header[0])
                for i in header[1:]:
                    f.write('\t' + i)

            f.write('\n')

            for i in values:
                # print i
                f.write(str(i) + '\t')
        

    def run_PC1D(self):
        process = subprocess.Popen(
            self.PC1D_File + ' ' + self.PC1D_prm, stdout=subprocess.PIPE)

        (output, err) = process.communicate()

        data_str = StringIO(output)
        process.kill()
        # print output, err
        # print output
        data = np.genfromtxt(data_str, delimiter='\t', names=True)

        return data

    def permute_values(self, values):

        return list(itertools.product(*values))


class CaculateFromPC1DOutput():

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
                print i + ' is a required PC1D output to perform this calculation'
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
            print 'The outputs received were:'
            print [i for i in values]

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

        #put it in cm
        

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
            print tau, '\t', average_carriers

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

        return tau, average_carriers/PC1D_output['Distance_from_Front'][-1]


if __name__ == "__main__":
    prm = 'D:\pc1d\pc1d5\StandardWafer_test.prm'
    batch = 'D:\pc1d\BatchFile.txt'
    pc1d = PC1D(prm, batch)
    CPC1D = CaculateFromPC1DOutput()
    print CPC1D.lifetime_from_PC1D(pc1d.run_PC1D(), carrier=None, Plot=True) * 1e6
    print 'ok'
    plt.show()
