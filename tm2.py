# -*- coding: UTF-8 -*-
# Author: WeiguoM
# Mail: weiguo.m@iphy.ac.cn

from qiskit import *
from qiskit.providers.aer import QasmSimulator
import numpy as np
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram
from qiskit import IBMQ


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



"""
circuit.h(0)
circuit.cp(-np.pi/2, 1, 0)
circuit.swap(1, 2)
circuit.cp(-np.pi/4, 1, 0)
circuit.h(2)
circuit.cp(-np.pi/2, 1, 2)
circuit.h(1)
"""


def iqft(prog, qlist):
    prog.h(qlist[0])
    prog = cpt(prog, [qlist[1], qlist[0]], -np.pi/2)
    prog.swap(qlist[1], qlist[2])
    prog = cpt(prog, [qlist[1], qlist[0]], -np.pi/4)
    prog.h(qlist[2])
    prog = cpt(prog, [qlist[1], qlist[2]], -np.pi/2)
    prog.h(qlist[1])
    return prog

simulator = QasmSimulator()

qreg_cn = QuantumRegister(3, 'cn')
qreg_tr = QuantumRegister(2, 'tg')
creg = ClassicalRegister(3, 'c')

circuit = QuantumCircuit(qreg_cn, qreg_tr, creg)

circuit.h([0, 1, 2])
circuit.barrier()
# circuit.draw()
#%%

circuit.swap(3, 4)
circuit.cnot(2, 3)
circuit.swap(1, 2)
circuit.cnot(2, 3)
circuit.cnot(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.cnot(3, 4)
circuit.barrier()

#%%
circuit.swap(0, 1)
circuit.swap(1, 2)
circuit.x(3)
circuit.barrier()
circuit.swap(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.x(4)
circuit.cnot(4, 3)
circuit.swap(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.cnot(3, 4)
circuit.barrier()

#%%

# circuit = iqft(circuit, [0, 1, 2])
circuit.measure([0, 1, 2], [2, 0, 1])
circuit.draw('mpl', filename='D:\\Python_project\\target.png')

#%%

simulator = Aer.get_backend('qasm_simulator')
results = execute(circuit, backend=simulator,
                  shots=8196).result()
counts = results.get_counts()

print('result: {}'.format(counts))
plot_histogram(counts)


