

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