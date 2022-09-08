

from quafu import *
import numpy as np



def initialize_q(prog):
    """
    :param prog: Input: Circuit
    :return: Circuit
    """
    prog.h(phy[0])
    prog.barrier([0, 4])
    prog.h(phy[1])
    prog.barrier([0, 4])
    prog.h(phy[2])
    prog.barrier([0, 4])
    return prog

def optim_tof(prog, qlist):
    prog.ry(qlist[2], np.pi/4)
    prog.barrier([0, 4])
    prog.cnot(qlist[1], qlist[2])
    prog.barrier([0, 4])
    prog.ry(qlist[2], np.pi/4)
    prog.barrier([0, 4])
    prog.cnot(qlist[0], qlist[2])
    prog.ry(qlist[2], -np.pi/4)
    prog.barrier([0, 4])
    prog.cnot(qlist[1], qlist[2])
    prog.ry(qlist[2], -np.pi/4)
    prog.barrier([0, 4])
    return prog

def cp(prog, qlist, para):
    prog.rz(qlist[0], para/2)
    prog.barrier([0, 4])
    prog.cnot(qlist[0], qlist[1])
    prog.rz(qlist[1], -para/2)
    prog.barrier([0, 4])
    prog.cnot(qlist[0], qlist[1])
    prog.rz(qlist[1], para/2)
    prog.barrier([0, 4])
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

phy = [0, 1, 2, 3, 4]
num = phy[4]

circuit = QuantumCircuit(num + 1)


#%%
circuit = initialize_q(circuit)

# circuit.cnot(phy[2], phy[3])
circuit.cnot(phy[2], phy[3])
circuit = Fix_swap(circuit, [phy[2], phy[3]])
circuit.cnot(phy[2], phy[3])
circuit.cnot(phy[3], phy[4])
circuit = optim_tof(circuit, [phy[2], phy[4], phy[3]])
circuit.cnot(phy[3], phy[4])
circuit.x(phy[3])
circuit.barrier([0, 4])
circuit = Fix_swap(circuit, [phy[0], phy[1]])
circuit.barrier([0, 4])
circuit = Fix_swap(circuit, [phy[1], phy[2]])
circuit.barrier([0, 4])
circuit = Fix_swap(circuit, [phy[3], phy[4]])
circuit.barrier([0, 4])
circuit = optim_tof(circuit, [phy[2], phy[4], phy[3]])
circuit.x(phy[4])
circuit.barrier([0, 4])
circuit.cnot(phy[4], phy[3])
circuit = Fix_swap(circuit, [phy[3], phy[4]])
circuit = optim_tof(circuit, [phy[2], phy[4], phy[3]])
circuit.cnot(phy[3], phy[4])

#%%
circuit = iqft(circuit, [phy[0], phy[1], phy[2]])
circuit.barrier([0, 4])
circuit.measure([phy[1], phy[0], phy[2]], [0, 1, 2])

circuit.draw_circuit()
#%%

task = Task()
task.load_account()
task.config(backend="ScQ-P10", shots=8196, compile=False)
res = task.send(circuit)

print(res.counts)
print(res.amplitudes)
res.plot_amplitudes()


# simu_res = simulate(circuit, output='amplitudes')
# simu_res.plot_amplitudes(full=True)
