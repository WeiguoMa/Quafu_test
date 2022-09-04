# -*- coding: UTF-8 -*-
# Author: WeiguoM
# Mail: weiguo.m@iphy.ac.cn

from qiskit import *
from qiskit.providers.aer import QasmSimulator


def initialize_q(prog_n, qlist):
    prog_n.h(qlist[0])
    prog_n.h(qlist[1])
    prog_n.h(qlist[2])
    return prog_n

####################





####################

simulator = QasmSimulator()

qreg_cn = QuantumRegister(3, 'cn')
qreg_tr = QuantumRegister(2, 'tg')
creg = ClassicalRegister(3, 'c')

circuit = QuantumCircuit(qreg_cn, qreg_tr, creg)

circuit = initialize_q(circuit, qreg_cn)

circuit.draw()

#%%
