
import PC1D
import matplotlib.pylab as plt

pc1d = PC1D.PC1D(PC1D_exe=r'D:\software\pc1d\PC1DV6.2\cmd-pc1d5.exe',
                 PC1D_prm=r'D:\software\pc1d\PC1DV6.2\test.prm',
                 BatchFile=r'D:\software\pc1d\PC1DV6.2\example batch file2.txt'
                 )

print (pc1d.PC1D_prm)
# print(data.dtype.names)

header = ['FrS(1)', 'RrS(1)']

Fsr = [1e7, 0]
Rsr = [1e7, 0]

for values in pc1d.permute_values([Fsr, Rsr]):
    pc1d.PrepareBatchFile(header, values)

    datas = pc1d.run()


    plt.plot(datas['Distance_from_Front']*1e6, datas['Electron_Density'], label=values)
    plt.plot(datas['Distance_from_Front']*1e6, datas['Hole_Density'],         label=values)

plt.legend()
plt.loglog()
plt.show()
