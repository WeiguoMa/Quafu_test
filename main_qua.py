

from quafu import *
import numpy as np



def initialize_q(prog):
    """
    :param prog: Input: Circuit
    :return: Circuit
    """
    prog.h(0)
    prog.h(1)
    prog.h(2)
    prog.barrier([0, 4])
    return prog

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

user = User()
user.save_apitoken('kJLQz9B8dz4yvt1guWiEOEIDOi1mrlcdZA4ypspITjd.Qf3YjM1UTO0YjNxojIwhXZiwiIxYjI6ICZpJye.9JiN1IzUIJiOicGbhJCLiQ1VKJiOiAXe0Jye')


circuit = QuantumCircuit(5)

#%%
circuit = initialize_q(circuit)

circuit.swap(3, 4)
circuit.cnot(2, 3)
circuit.swap(1, 2)
circuit.cnot(2, 3)
circuit.cnot(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.cnot(3, 4)
circuit.barrier([0, 4])
#%%
circuit.swap(0, 1)
circuit.swap(1, 2)
circuit.x(3)
circuit.barrier([0, 4])
circuit.swap(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.x(4)
circuit.cnot(4, 3)
circuit.swap(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.cnot(3, 4)
circuit.barrier([0, 4])
#%%
circuit.swap(0, 1)
circuit.swap(1, 2)
circuit.h(1)
circuit = cp(circuit, [0, 1], -np.pi/2)
circuit = cp(circuit, [2, 1], -np.pi/4)
circuit.h(0)
circuit.swap(1, 2)
circuit = cp(circuit, [1, 0], -np.pi/2)
circuit.h(1)
circuit.measure([0, 1, 2], [1, 0, 2])
circuit.draw_circuit()
#%%

# task = Task()
# task.load_account()
# task.config(backend="ScQ-P10", shots=8196, compile=True)
# res = task.send(circuit)
#
# print(res.counts)
# print(res.amplitudes)
# res.plot_amplitudes()


simu_res = simulate(circuit, output='amplitudes')
simu_res.plot_amplitudes(full=True)