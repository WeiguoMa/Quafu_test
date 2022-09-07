# -*- coding: UTF-8 -*-
# Author: WeiguoM
# Mail: weiguo.m@iphy.ac.cn

from qiskit import *

def nswap(prog, qlist):
    prog.cnot(qlist[0], qlist[1])
    prog.cnot(qlist[1], qlist[0])
    prog.cnot(qlist[0], qlist[1])
    return prog

q = QuantumCircuit(2, 2)
q = nswap(q, [0, 1])
q.measure([0, 1], [0, 1])
q.draw()
