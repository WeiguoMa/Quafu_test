<<<<<<< HEAD


from quafu import *
import numpy as np


def optim_tof(prog, qlist):
    prog.ry(qlist[2], np.pi/4)
    prog.cnot(qlist[1], qlist[2])
    prog.ry(qlist[2], np.pi/4)
    prog.cnot(qlist[0], qlist[2])
    prog.ry(qlist[2], -np.pi/4)
    prog.cnot(qlist[1], qlist[2])
    prog.ry(qlist[2], -np.pi/4)
    return prog

def cp(prog, qlist, para):
    prog.rz(qlist[0], para/2)
    prog.cnot(qlist[0], qlist[1])
    prog.rz(qlist[1], -para/2)
    prog.cnot(qlist[0], qlist[1])
    prog.rz(qlist[1], para/2)
    return prog

def Fix_swap(prog, qlist):
    prog.cnot(qlist[0], qlist[1])
    prog.cnot(qlist[1], qlist[0])
    prog.cnot(qlist[0], qlist[1])
    return prog
user = User()
user.save_apitoken('kJLQz9B8dz4yvt1guWiEOEIDOi1mrlcdZA4ypspITjd.Qf3YjM1UTO0YjNxojIwhXZiwiIxYjI6ICZpJye.9JiN1IzUIJiOicGbhJCLiQ1VKJiOiAXe0Jye')


circuit = QuantumCircuit(46)

circuit.h(7)
circuit.h(8)
circuit.h(20)

circuit.cnot(8, 9)
circuit = Fix_swap(circuit, [8, 9])
circuit.cnot(8, 9)
circuit.cnot(9, 10)
circuit = optim_tof(circuit, [8, 10, 9])
circuit.cnot(9, 10)
circuit.x(9)
circuit = Fix_swap(circuit, [8, 20])
circuit = Fix_swap(circuit, [9, 10])
circuit = optim_tof(circuit, [8, 10, 9])
circuit.x(10)
circuit.cnot(10, 9)
circuit = Fix_swap(circuit, [9, 10])
circuit = optim_tof(circuit, [8, 10, 9])
circuit.cnot(9, 10)
circuit = Fix_swap(circuit, [7, 8])
circuit.h(7)
circuit = Fix_swap(circuit, [7, 8])
circuit = cp(circuit, [20, 8], -np.pi/2)
circuit = cp(circuit, [7, 8], -np.pi/4)
circuit.h(20)
circuit = Fix_swap(circuit, [7, 8])
circuit = cp(circuit, [8, 20], -np.pi/2)
circuit.h(8)

circuit.measure([8, 7, 20], [0, 1, 2])
circuit.draw_circuit()

# simu_res = simulate(circuit, output='amplitudes')
# simu_res.plot_amplitudes(full=True)



task = Task()
task.load_account()
task.config(backend="ScQ-P50", shots=8196, compile=False)
res = task.send(circuit)

print(res.counts)
print(res.amplitudes)
res.plot_amplitudes()
=======
# -*- coding: UTF-8 -*-
# Author: WeiguoM
# Mail: weiguo.m@iphy.ac.cn

from qiskit import *
from qiskit.providers.aer import QasmSimulator
import numpy as np
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram
from qiskit import IBMQ


def nswap(prog, qlist):
    prog.cnot(qlist[0], qlist[1])
    prog.cnot(qlist[1], qlist[0])
    prog.cnot(qlist[0], qlist[1])
    return prog


def optim_tof(prog, qlist):
    prog.ry(np.pi/4, qlist[2])
    prog.cnot(qlist[1], qlist[2])
    prog.ry(np.pi/4, qlist[2])
    prog.cnot(qlist[0], qlist[2])
    prog.ry(-np.pi/4, qlist[2])
    prog.cnot(qlist[1], qlist[2])
    prog.ry(-np.pi/4, qlist[2])
    return prog

def cpt(prog, qlist, params):
    prog.rz(params / 2, qlist[0])
    prog.cnot(qlist[0], qlist[1])
    prog.rz(-params / 2, qlist[1])
    prog.cnot(qlist[0], qlist[1])
    prog.rz(params / 2, qlist[1])
    return prog


# def iqft(prog, qlist):
#     prog = nswap(prog, [qlist[0], qlist[1]])
#     prog = nswap(prog, [qlist[1], qlist[2]])
#     prog.h(qlist[1])
#     prog = cpt(prog, [qlist[0], qlist[1]], -np.pi/2)
#     # circuit.cp(-np.pi/2, 0, 1)
#     prog = cpt(prog, [qlist[2], qlist[1]], -np.pi/4)
#     # circuit.cp(-np.pi/4, 2, 1)
#     prog.h(qlist[0])
#     prog = nswap(prog, [qlist[1], qlist[2]])
#     prog = cpt(prog, [qlist[1], qlist[0]], -np.pi/2)
#     # circuit.cp(-np.pi/2, 1, 0)
#     prog.h(qlist[1])
#     prog.barrier()
#     return prog


simulator = QasmSimulator()

qreg_cn = QuantumRegister(3, 'cn')
qreg_tr = QuantumRegister(2, 'tg')
creg = ClassicalRegister(3, 'c')

circuit = QuantumCircuit(qreg_cn, qreg_tr, creg)

circuit.h([qreg_cn[0], qreg_cn[1], qreg_cn[2]])
circuit.barrier()
circuit.draw()
#%%
circuit.cnot(qreg_cn[2], qreg_tr[1])
circuit = nswap(circuit, [qreg_cn[1], qreg_cn[2]])
circuit.cnot(qreg_cn[2], qreg_tr[1])
circuit.cnot(qreg_tr[1], qreg_tr[0])
circuit = optim_tof(circuit, [qreg_cn[2], qreg_tr[0], qreg_tr[1]])
circuit.cnot(qreg_tr[1], qreg_tr[0])
circuit.x(qreg_tr[1])
circuit = nswap(circuit, [qreg_cn[2], qreg_cn[0]])
circuit = nswap(circuit, [qreg_tr[1], qreg_tr[0]])
circuit = optim_tof(circuit, [qreg_cn[2], qreg_tr[0], qreg_tr[1]])
circuit.x(qreg_tr[0])
circuit.cnot(qreg_tr[0], qreg_tr[1])
circuit = nswap(circuit, [qreg_tr[1], qreg_tr[0]])
circuit = optim_tof(circuit, [qreg_cn[2], qreg_tr[0], qreg_tr[1]])
circuit.cnot(qreg_tr[1], qreg_tr[0])
circuit = nswap(circuit, [qreg_cn[1], qreg_cn[2]])


#%%
circuit.h(qreg_cn[1])
circuit = nswap(circuit, [qreg_cn[1], qreg_cn[2]])
circuit = cpt(circuit, [qreg_cn[0], qreg_cn[2]], -np.pi/2)
circuit = cpt(circuit, [qreg_cn[1], qreg_cn[2]], -np.pi/4)
circuit.h(qreg_cn[0])
circuit = nswap(circuit, [qreg_cn[1], qreg_cn[2]])
circuit = cpt(circuit, [qreg_cn[2], qreg_cn[0]], -np.pi/2)
circuit.h(qreg_cn[2])
circuit.barrier()
circuit.measure([qreg_cn[0], qreg_cn[1], qreg_cn[2]], [0, 1, 2])

circuit.draw('mpl')

#%%

# simulator = Aer.get_backend('qasm_simulator')
# results = execute(circuit, backend=simulator,
#                   shots=8196).result()
# counts = results.get_counts()
#
# print('result: {}'.format(counts))
# plot_histogram(counts)

#%%
IBMQ.save_account('0639082da4ca91f28f79d93bbc1ec3ed5adcc32299523f942270326ac03c65bb8d51ddce542ec869ef7154dca84ef682606220c84d4e9b8243a81927881c8bfa',
                  overwrite=True)

IBMQ.load_account()
provider = IBMQ.get_provider(group='open', project='main')
qcomp = provider.get_backend('ibmq_lima')


job = execute(circuit, backend=qcomp, shots=8196, initial_layout={
    qreg_cn[1]: 0,
    qreg_cn[2]: 1,
    qreg_cn[0]: 2,
    qreg_tr[1]: 3,
    qreg_tr[0]: 4
})

job_monitor(job)

result = job.result()
plot_histogram(result.get_counts(circuit))

#%%
>>>>>>> df24fa60552294a418bdfda38309122ba670fc4d
