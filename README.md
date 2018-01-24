

# Just a PC1D wrapper

This is just a quick wrapper around PC1D, meant for getting stuff into python or doing batch processes. PC1D is a popular, free one dimensional solver used in semiconductors modeling. It is particularly popular in photovoltaics.

This wrapper works on OSx, Linux, and Windows. It is compatible with both PVCD5 and PC1D6.


# Using it

As this is just a wrapper first go ahead an open the PC1D program and design your cell.
Try and make sure your that your .prm file runs before using this wrapper.

This script does not do magic, it is mostly only useful for pulling from the active graph. If your active graph isn't the correct one, you will get the wrong data.

To use it,

```python
  from PC1D import PC1D


  # provide an absolute path to your prm file.
  prm_file_path = path

  #initialize the wrapper
  pc1d = PC1D(PC1D_prm=prm_file_path)

  # set the standard silicon constants
  pc1d.StandardSiliconConstants

  # the run the prm. The values in the active graph will be saved in data
  data = a.run()

  #The returned data is a named numpy array. Check out its headers with
  print(data.dtype.names)

  #print its values:
  print(data)
```

# Common issues

PC1D does not play so nice in batch form. The main issue is finding the files it needs to do its calculations. This includes any-files, like absorption coefficients or time sweeps. The short answer is you need to make sure that they are absolutely referenced within PC1D. This can be more tricky than you would think, as it loves relative references. To help get around this there are two properties you can use to set some standard values. These include:

1. pc1d.StandardSiliconConstants. This sets the intrinsic n and k from Green in 2008, and
si300_green2008. Also the values in the provide si_updated.mat, which affects Permittivity, Band Structure, Material Recombination, Field-Enhanced Recombination, Bandgap Narrowing, Mobilities, Refractive Index, Optical Absorption Coefficients, Free-Carrier Absorption.
2. pc1d.setQSSPCFlash. This sets the spectrum and flash intensity to be that from a Sinton WCT. Here, we use a increasing flash intensity and assume a steady state flash. This limits the conditions that are possible (steady state) to simulate, but ensures that they simulations will converge.

Something that doesn't work is using external batch files. But never mind, you can change all the parameters prm directly using the pc1d.alterPRM function. You just need to pass the name of the vairable in the prm. This can be a bugger to find. You need to change a .prm to ascii, using the exe kindly provided by Halvard from version 6, and look through the list.  
