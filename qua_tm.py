

from quafu import *
import numpy as np



def initialize_q(prog):
    """
    :param prog: Input: Circuit
    :return: Circuit
    """
    prog.h(0)
    prog.barrier([0, 4])
    prog.h(1)
    prog.barrier([0, 4])
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

def Fix_swap(prog, qlist):
    prog.cnot(qlist[0], qlist[1])
    prog.cnot(qlist[1], qlist[0])
    prog.cnot(qlist[0], qlist[1])
    return prog

def iqft(prog, qlist):
    prog.h(qlist[0])
    prog.barrier([0, 4])
    prog = cp(prog, [qlist[1], qlist[0]], -np.pi/2)
    prog.barrier([0, 4])
    prog = Fix_swap(prog, [qlist[1], qlist[2]])
    prog = cp(prog, [qlist[1], qlist[0]], -np.pi/4)
    prog.barrier([0, 4])
    prog.h(qlist[2])
    prog = cp(prog, [qlist[1], qlist[2]], -np.pi/2)
    prog.h(qlist[1])
    return prog


user = User()
user.save_apitoken('kJLQz9B8dz4yvt1guWiEOEIDOi1mrlcdZA4ypspITjd.Qf3YjM1UTO0YjNxojIwhXZiwiIxYjI6ICZpJye.9JiN1IzUIJiOicGbhJCLiQ1VKJiOiAXe0Jye')


circuit = QuantumCircuit(5)

#%%
circuit = initialize_q(circuit)
#%%
# circuit.swap(3, 4)
circuit = Fix_swap(circuit, [3, 4])
circuit.cnot(2, 3)
#%%
circuit = Fix_swap(circuit, [1, 2])
# circuit.swap(1, 2)
circuit.cnot(2, 3)
circuit.cnot(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.cnot(3, 4)
circuit.barrier([0, 4])
circuit = Fix_swap(circuit, [0, 1])
# circuit.swap(0, 1)
circuit = Fix_swap(circuit, [1, 2])
# circuit.swap(1, 2)
circuit.barrier([0, 4])
#%%
circuit.x(3)
circuit.barrier([0, 4])
# circuit.swap(3, 4)
circuit = Fix_swap(circuit, [3, 4])
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.barrier([0, 4])
circuit.x(4)
circuit.cnot(4, 3)
circuit = Fix_swap(circuit, [3, 4])
# circuit.swap(3, 4)
# circuit.toffoli(2, 4, 3)
circuit = optim_tof(circuit, [2, 4, 3])
circuit.cnot(3, 4)
circuit.barrier([0, 4])

#%%

circuit = iqft(circuit, [0, 1, 2])
circuit.measure([0, 1, 2], [0, 2, 1])
# circuit.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
circuit.draw_circuit()

# ----------------------------------------


# circuit.h(0)
# circuit = cp(circuit, [1, 0], -np.pi/2)
# circuit.swap(1, 2)
# circuit = cp(circuit, [2, 0], -np.pi/4)
# circuit.h(2)
# circuit = cp(circuit, [1, 2], -np.pi/2)
# circuit.h(1)
# circuit.measure([0, 1, 2], [1, 0, 2])

#%%
print("-----------------------QASM---BELOW--------------------")
simu_res = simulate(circuit, output='amplitudes')
simu_res.plot_amplitudes(full=True)

#%%
print("-----------------------EXPERIMENT---BELOW--------------------")
task = Task()
task.load_account()
task.config(backend="ScQ-P10", shots=8196, compile=False)
res = task.send(circuit)

print(res.counts)
print(res.amplitudes)
res.plot_amplitudes()


