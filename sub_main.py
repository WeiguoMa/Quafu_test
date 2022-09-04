# -*- coding: UTF-8 -*-
# Author: WeiguoM
# Mail: weiguo.m@iphy.ac.cn
import qiskit
from qiskit import *
from qiskit.providers.aer import QasmSimulator
import numpy as np
from qiskit.visualization import plot_histogram

simulator = QasmSimulator()

qreg_cn = QuantumRegister(3, 'cn')
qreg_tr = QuantumRegister(2, 'tg')
creg = ClassicalRegister(3, 'c')

circuit = QuantumCircuit(qreg_cn, qreg_tr, creg)

circuit.h([0, 1, 2])

circuit.draw()
#%%

circuit.cnot(2, 4)
circuit.cnot(1, 4)
circuit.cnot(4, 3)
circuit.toffoli(1, 3, 4)
circuit.cnot(4, 3)
circuit.x(4)
circuit.toffoli(0, 4, 3)
circuit.x(4)
circuit.cnot(4, 3)
circuit.toffoli(0, 3, 4)
circuit.cnot(4, 3)

circuit.draw()



#%%
circuit.barrier()

circuit.swap(0, 2)
circuit.h(2)
circuit.cp(-np.pi/2, 1, 2)
circuit.cp(-np.pi/4, 0, 2)
circuit.h(1)
circuit.cp(-np.pi/2, 0, 1)
circuit.h(0)
circuit.u3

circuit.draw()
#%%

circuit.barrier([0, 1, 2])
circuit.measure([0, 1, 2], [0, 1, 2])

circuit.draw()

#%%

simulator = Aer.get_backend('qasm_simulator')
results = execute(circuit, backend=simulator,
                 shots=8196).result()
counts = results.get_counts()

print('result: {}'.format(counts))
plot_histogram(counts)
