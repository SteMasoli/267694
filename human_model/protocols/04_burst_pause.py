from Purkinje_morpho_1 import Purkinje_Morpho_1
from neuron import h,gui
import multiprocessing
import random as rnd
from Purkinje_morpho_1_number import number_ind_1
import numpy as np
import matplotlib.pyplot as plt

#per disabilitare tutti i generatori random
seed = 123456
rnd.seed(seed)
h.use_mcell_ran4(1)
h.mcell_ran4_init(seed)

Hines = h.CVode()
Hines.active(0)


spines_on = 0 # switch between 0 (no spines) and 1 (spines)


h.nrncontrolmenu()

stimdata = dict()
stimdata['timeglobal'] =  5000


#this is a default setup
synapsesdata = dict()
synapsesdata['npf'] = 50
synapsesdata['naa'] = 0

synapsesdata['pfstl'] = 25


#parallel fiber
synapsesdata['syninterval'] = 10 
synapsesdata['synnumber'] = 5 
synapsesdata['synstart'] = 2000
synapsesdata['synnoise'] = 0

#ascending axon
synapsesdata['synaainterval'] = 10
synapsesdata['synaanumber'] = 5
synapsesdata['synaastart'] = 2000
synapsesdata['synaanoise'] = 0

#INHIBITION
#Stellate on parallel fiber
synapsesdata['synpfstlinterval'] = 7
synapsesdata['synpfstlnumber'] = 3
synapsesdata['synpfstlstart'] = 2000
synapsesdata['synpfstlnoise'] = 0

#new delay factor
synapsesdata['synpfdelay'] = 0
synapsesdata['synpfstldelay'] = 4

cell = Purkinje_Morpho_1(spines_on)


cpu = multiprocessing.cpu_count()
h.load_file("parcom.hoc")
p = h.ParallelComputeTool()
if spines_on == 0:
    p.change_nthread(cpu,1)
    print('spines_off')
else:    
    p.change_nthread(32,1)
    print('spines_on')
p.multisplit(1)
print(cpu)


cell.createsyn(int(synapsesdata['npf']), int(synapsesdata['naa']), int(synapsesdata['pfstl']))

#PF syn
spk_stim_pf = []
totalstim = int(stimdata['timeglobal']/  synapsesdata['synstart'])

for j in range(int(totalstim)):
    spk_stim = h.NetStim()
    spk_stim.interval=synapsesdata['syninterval']
    spk_stim.number=synapsesdata['synnumber']
    spk_stim.noise=synapsesdata['synnoise']
    spk_stim.start=(synapsesdata['synstart'] * (totalstim - j)) + synapsesdata['synpfdelay']
    
    spk_stim_pf.append(spk_stim)
    spk_nc_pfsyn = []
    j = j-1

print('len pf', len(cell.PF_L))

for m in range(int(totalstim)):	
    spk_nc_pfsyn.append([h.NetCon(spk_stim_pf[m],pf.input,0,0.1,1) for pf in cell.PF_L])

#AA syn
spk_stim_aa = []
totalstim = int(stimdata['timeglobal']/  synapsesdata['synaastart'])

for j in range(int(totalstim)):
    spk_stim_AA = h.NetStim()
    spk_stim_AA.interval=synapsesdata['synaainterval']
    spk_stim_AA.number=synapsesdata['synaanumber']
    spk_stim_AA.noise=synapsesdata['synaanoise']
    spk_stim_AA.start=(synapsesdata['synaastart'] * (totalstim - j)) + synapsesdata['synpfdelay']
    
    spk_stim_aa.append(spk_stim_AA)
    spk_nc_aasyn = []
    j = j-1

print('len aa', len(cell.AA_L))

for m in range(int(totalstim)):	
    spk_nc_aasyn.append([h.NetCon(spk_stim_aa[m],aa.input,0,0.1,1) for aa in cell.AA_L])


#SC
spk_stim_SC_complete = []
totalstim_SC = int(stimdata['timeglobal']/  synapsesdata['synpfstlstart'])

for j in range(int(totalstim_SC)):
    spk_stim_SC = h.NetStim()
    spk_stim_SC.interval=synapsesdata['synpfstlinterval']
    spk_stim_SC.number=synapsesdata['synpfstlnumber']
    spk_stim_SC.noise=synapsesdata['synpfstlnoise']
    spk_stim_SC.start=(synapsesdata['synpfstlstart'] * (totalstim_SC - j)) + synapsesdata['synpfstldelay']
    
    spk_stim_SC_complete.append(spk_stim_SC)
    j = j-1

print('len SC', len(cell.SC_L))
spk_nc_SCsyn = []
for m in range(int(totalstim_SC)):	
    spk_nc_SCsyn.append([h.NetCon(spk_stim_SC_complete[m],stl.input,0,0.1,1) for stl in cell.SC_L])

      
h.dt = 0.025
h.celsius = 32
h.tstop = stimdata['timeglobal']
h.v_init = -65

indiv_number = number_ind_1['indiv']

def initialize():
    h.finitialize()
    h.run()
    
initialize()

if spines_on == 0:
    #save files
    np.savetxt('04_vm_soma_no_spines.txt', np.column_stack((np.array(cell.time_vector), np.array(cell.vm_soma))), delimiter = ' ')

    img = plt.plot(np.array(cell.time_vector), np.array(cell.vm_soma))
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.savefig('04_vm_soma_nospines.eps')
    plt.close()
if spines_on == 1:
    #save files
    np.savetxt('04_vm_soma_spines.txt', np.column_stack((np.array(cell.time_vector), np.array(cell.vm_soma))), delimiter = ' ')

    img = plt.plot(np.array(cell.time_vector), np.array(cell.vm_soma))
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.savefig('04_vm_soma_spines.eps')
    plt.close()
quit()
