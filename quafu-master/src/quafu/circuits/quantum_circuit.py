import functools
from turtle import width
import numpy as np
from ..results.results import ExecResult, merge_measure
from ..elements.quantum_element import Barrier, ControlGate, MultiQubitGate, SingleQubitGate, TwoQubitGate
from ..elements.element_gates import *
from ..exceptions import CircuitError, ServerError
from typing import Iterable
 

class QuantumCircuit(object):
    def __init__(self, num):
        """
        Initialize a QuantumCircuit object
        
        Args:   
            num (int): Total qubit number used
        """
        self.num = num
        self.gates = []
        self.openqasm = ""
        self.circuit = []
        self.measures = dict(zip(range(num), range(num)))
        self.used_qubits = []


    def get_used_qubits(self):
        self.layered_circuit()
        return self.used_qubits

    def layered_circuit(self):
        """
        Make layered circuit from the gate sequence self.gates.

        Returns: 
            A layered list with left justed circuit.
        """
        num = self.num
        gatelist = self.gates
        gateQlist = [[] for i in range(num)]
        used_qubits = []
        for gate in gatelist:
            if isinstance(gate, SingleQubitGate):
                gateQlist[gate.pos].append(gate)
                if gate.pos not in used_qubits:
                    used_qubits.append(gate.pos)

            elif isinstance(gate, Barrier) or isinstance(gate, TwoQubitGate) or isinstance(gate, MultiQubitGate):
                pos1 = min(gate.pos)
                pos2 = max(gate.pos)
                gateQlist[pos1].append(gate)
                for j in range(pos1 + 1, pos2 + 1):
                    gateQlist[j].append(None)

                if isinstance(gate, TwoQubitGate) or isinstance(gate, MultiQubitGate):
                    for pos in gate.pos:
                        if pos not in used_qubits:
                            used_qubits.append(pos)

                maxlayer = max([len(gateQlist[j]) for j in range(pos1, pos2 + 1)])
                for j in range(pos1, pos2 + 1):
                    layerj = len(gateQlist[j])
                    pos = layerj - 1
                    if not layerj == maxlayer:
                        for i in range(abs(layerj - maxlayer)):
                            gateQlist[j].insert(pos, None)

        maxdepth = max([len(gateQlist[i]) for i in range(num)])

        for gates in gateQlist:
            gates.extend([None] * (maxdepth - len(gates)))

        for m in self.measures.keys():
            if m not in used_qubits:
                used_qubits.append(m)
        used_qubits = np.sort(used_qubits)

        new_gateQlist = []
        for old_qi in range(len(gateQlist)):
            gates = gateQlist[old_qi]
            if old_qi in used_qubits:
                new_gateQlist.append(gates)

        lc = np.array(new_gateQlist)
        lc = np.vstack((used_qubits, lc.T)).T
        self.circuit = lc
        self.used_qubits = list(used_qubits)
        return self.circuit

    def draw_circuit(self, width=4):
        """
        Draw layered circuit using ASCII, print in terminal.

        Args:
            width (int): The width of each gate. 
        """
        self.layered_circuit()
        gateQlist = self.circuit
        num = gateQlist.shape[0]
        depth = gateQlist.shape[1] - 1
        printlist = np.array([[""] * depth for i in range(2 * num)], dtype="<U30")

        reduce_map = dict(zip(gateQlist[:, 0], range(num)))
        reduce_map_inv = dict(zip(range(num), gateQlist[:, 0]))
        for l in range(depth):
            layergates = gateQlist[:, l + 1]
            maxlen = 1 + width
            for i in range(num):
                gate = layergates[i]
                if isinstance(gate, FixedSingleQubitGate):
                    gate_symbol = gate.name
                    if gate.name == "SX":
                        gate_symbol = "√X"
                    elif gate.name == "SY":
                        gate_symbol = "√Y"
                    elif gate.name == "SW":
                        gate_symbol = "√W"
                    
                    printlist[i * 2, l] = gate_symbol
                    maxlen = max(maxlen, len(gate_symbol) + width)
                elif isinstance(gate, ParaSingleQubitGate):
                    gatestr = "%s(%.3f)" % (gate.name, gate.paras)
                    printlist[i * 2, l] = gatestr
                    maxlen = max(maxlen, len(gatestr) + width)

                elif isinstance(gate, FixedTwoQubitGate) or isinstance(gate, FixedMultiQubitGate):
                    q1 = reduce_map[min(gate.pos)]
                    q2 = reduce_map[max(gate.pos)]
                    printlist[2 * q1 + 1:2 * q2, l] = "|"
                    printlist[reduce_map[gate.pos[0]] * 2, l] = "#"
                    printlist[reduce_map[gate.pos[1]] * 2, l] = "#"

                    if isinstance(gate, ControlGate): 
                        printlist[reduce_map[gate.ctrl] * 2, l] = "*"
                        if gate.targ_name == "X":
                            targ_symbol = "+"
                        else:
                            targ_symbol = gate.targ_name
                            maxlen = max(maxlen, len(targ_symbol) + width)
                        printlist[reduce_map[gate.targ] * 2, l] = targ_symbol

                    elif gate.name == "SWAP":
                        printlist[reduce_map[gate.pos[0]] * 2, l] = "x"
                        printlist[reduce_map[gate.pos[1]] * 2, l] = "x"

                    elif isinstance(gate, FixedMultiQubitGate):
                        if hasattr(gate, "ctrls") and hasattr(gate, "targs"):
                            for ctrl in gate.ctrls:
                                printlist[reduce_map[ctrl] * 2, l] = "*"
                            for ti in range(len(gate.targs)):
                                targ = gate.targs[ti]
                                if gate.targ_names[ti] == "SWAP":
                                    targ_symbol = "x"
                                elif gate.targ_names[ti] == "X":
                                    targ_symbol = "+"
                                else:
                                    targ_symbol = gate.targ_names[ti]
                                    maxlen = max(maxlen, len(targ_symbol) + width)
                                printlist[reduce_map[targ] * 2, l] = targ_symbol

                        else:
                            printlist[q1 + q2, l] = gate.name
                            maxlen = max(maxlen, len(gate.name) + width)

                    else:
                        printlist[q1 + q2, l] = gate.name
                        maxlen = max(maxlen, len(gate.name) + width)

                elif isinstance(gate, ParaTwoQubitGate) or isinstance(gate, ParaMultiQubitGate):
                    q1 = reduce_map(min(gate.pos))
                    q2 = reduce_map(max(gate.pos))
                    printlist[2 * q1 + 1:2 * q2, l] = "|"
                    printlist[reduce_map[gate.pos[0]] * 2, l] = "#"
                    printlist[reduce_map[gate.pos[1]] * 2, l] = "#"
                    gatestr = ""
                    if isinstance(gate.paras, Iterable):
                        gatestr = ("%s(" % gate.name + ",".join(
                            ["%.3f" % para for para in gate.paras]) + ")")
                    else:
                        gatestr = "%s(%.3f)" % (gate.name, gate.paras)
                    printlist[q1 + q2, l] = gatestr
                    maxlen = max(maxlen, len(gatestr) + width)

                elif isinstance(gate, Barrier):
                    pos = [i for i in gate.pos if i in reduce_map.keys()]
                    q1 = reduce_map[min(pos)]
                    q2 = reduce_map[max(pos)]
                    printlist[2 * q1:2 * q2 + 1, l] = "||"
                    maxlen = max(maxlen, len("||"))

            printlist[-1, l] = maxlen

        circuitstr = []
        for j in range(2 * num - 1):
            if j % 2 == 0:
                linestr = ("q[%d]" % (reduce_map_inv[j // 2])).ljust(6) + "".join(
                    [printlist[j, l].center(int(printlist[-1, l]), "-") for l in range(depth)])
                if reduce_map_inv[j // 2] in self.measures.keys():
                    linestr += " M->c[%d]" % self.measures[reduce_map_inv[j // 2]]
                circuitstr.append(linestr)
            else:
                circuitstr.append("".ljust(6) + "".join(
                    [printlist[j, l].center(int(printlist[-1, l]), " ") for l in range(depth)]))
        circuitstr = "\n".join(circuitstr)
        print(circuitstr)

    def from_openqasm(self, openqasm):
        """
        Initialize the circuit from openqasm text.
        """
        from numpy import pi
        import re
        self.openqasm = openqasm
        # lines = self.openqasm.strip("\n").splitlines(";")
        lines = self.openqasm.splitlines()
        lines = [line for line in lines if line]
        self.gates = []
        self.measures = {}
        measured_qubits = []
        global_valid = True
        for line in lines[2:]:
            if line:
                operations_qbs = line.split(" ", 1)
                operations = operations_qbs[0]
                if operations == "qreg":
                    qbs = operations_qbs[1]
                    self.num = int(re.findall("\d+", qbs)[0])
                elif operations == "creg":
                    pass
                elif operations == "measure":
                    qbs = operations_qbs[1]
                    indstr = re.findall("\d+", qbs)
                    inds = [int(indst) for indst in indstr]
                    mb = inds[0]
                    cb = inds[1]
                    self.measures[mb] = cb
                    measured_qubits.append(mb)
                else:
                    qbs = operations_qbs[1]
                    indstr = re.findall("\d+", qbs)
                    inds = [int(indst) for indst in indstr]
                    valid = True
                    for pos in inds:
                        if pos in measured_qubits:
                            valid = False
                            global_valid = False
                            break

                    if valid:
                        if operations == "barrier":
                            self.barrier(inds)

                        else:
                            sp_op = operations.split("(")
                            gatename = sp_op[0]
                            if len(sp_op) > 1:
                                paras = sp_op[1].strip("()")
                                parastr = paras.split(",")
                                paras = [eval(parai, {"pi": pi}) for parai in parastr]

                            if gatename == "cx":
                                self.cnot(inds[0], inds[1])
                            elif gatename == "cy":
                                self.cy(inds[0], inds[1])
                            elif gatename == "cz":
                                self.cz(inds[0], inds[1])
                            elif gatename == "swap":
                                self.swap(inds[0], inds[1])
                            elif gatename == "rx":
                                self.rx(inds[0], paras[0])
                            elif gatename == "ry":
                                self.ry(inds[0], paras[0])
                            elif gatename == "rz":
                                self.rz(inds[0], paras[0])
                            elif gatename == "x":
                                self.x(inds[0])
                            elif gatename == "y":
                                self.y(inds[0])
                            elif gatename == "z":
                                self.z(inds[0])
                            elif gatename == "h":
                                self.h(inds[0])
                            elif gatename == "s":
                                self.s(inds[0])
                            elif gatename == "sdg":
                                self.sdg(inds[0])
                            elif gatename == "t":
                                self.t(inds[0])
                            elif gatename == "sx":
                                self.sx(inds[0])
                            elif gatename == "ccx":
                                self.toffoli(inds[0], inds[1], inds[2])
                            elif gatename == "cswap":
                                self.fredkin(inds[0], inds[1], inds[2])
                            elif gatename == "u1":
                                self.rz(inds[0], paras[0])
                            elif gatename == "u2":
                                self.rz(inds[0], paras[1])
                                self.ry(inds[0], pi / 2)
                                self.rz(inds[0], paras[0])
                            elif gatename == "u3":
                                self.rz(inds[0], paras[2])
                                self.ry(inds[0], paras[0])
                                self.rz(inds[0], paras[1])
                            else:
                                print(
                                    "Warning: Operations %s may be not supported by QuantumCircuit class currently." % gatename)

        if not self.measures:
            self.measures = dict(zip(range(self.num), range(self.num)))
        if not global_valid:
            print("Warning: All operations after measurement will be removed for executing on experiment")

    def to_openqasm(self, compile=True):
        """
        Convert the circuit to openqasm text.

        Returns: 
            openqasm text.
        """
        qasm = '''OPENQASM 2.0;\ninclude "qelib1.inc";\n'''
        qasm += "qreg q[%d];\n" % self.num
        qasm += "creg meas[%d];\n" % len(self.measures)
        for gate in self.gates:
            if isinstance(gate, FixedSingleQubitGate):
                if gate.name == "SY":
                    qasm += "ry(pi/2) q[%d];\n" %(gate.pos)
                elif gate.name == "W":
                    qasm += "rz(-pi/4) q[%d];\nrx(pi) q[%d];\nrz(pi/4) q[%d];\n"  %(gate.pos, gate.pos, gate.pos)
                elif gate.name == "SW":
                    qasm += "rz(-pi/4) q[%d];\nrx(pi/2) q[%d];\nrz(pi/4) q[%d];\n"  %(gate.pos, gate.pos, gate.pos)
                else:
                    qasm += "%s q[%d];\n" % (gate.name.lower(), gate.pos)

            elif isinstance(gate, ParaSingleQubitGate):
                qasm += "%s(%s) q[%d];\n" % (gate.name.lower(), gate.paras, gate.pos)
            elif isinstance(gate, Barrier) or isinstance(gate, FixedTwoQubitGate) or isinstance(gate, FixedMultiQubitGate):
                if gate.name == "CS":
                    qasm += "cp(pi/2) " + "q[%d],q[%d];\n" % (gate.pos[0], gate.pos[1])
                elif gate.name == "CT":
                    qasm += "cp(pi/4)" + "q[%d],q[%d];\n" % (gate.pos[0], gate.pos[1])
                else:
                    qasm += "%s " %(gate.name.lower()) + ",".join(["q[%d]" % p for p in gate.pos]) + ";\n"

        for key in self.measures:
            qasm += "measure q[%d] -> meas[%d];\n" % (key, self.measures[key])

        self.openqasm = qasm
        return qasm

   
    def h(self, pos: int):
        """
        Hadamard gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(HGate(pos))
        return self

    def x(self, pos: int):
        """
        X gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(XGate(pos))
        return self

    def y(self, pos: int):
        """
        Y gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(YGate(pos))
        return self

    def z(self, pos: int):
        """
        Z gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(ZGate(pos))
        return self

    def t(self, pos: int):
        """
        T gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(TGate(pos))
        return self
    
    def s(self, pos: int):
        """
        S gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(SGate(pos))
        return self

    def sdg(self, pos: int):
        """
        Sdg gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(SdgGate(pos))
        return self

    def sx(self, pos: int):
        """
        √X gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(SXGate(pos))
        return self

    def sy(self, pos: int):
        """
        √Y gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(SYGate(pos))
        return self

    def w(self, pos: int):
        """
        W gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(WGate(pos))
        return self
    
    def sw(self, pos: int):
        """
        √W gate.

        Args:
            pos (int): qubit the gate act.
        """
        self.gates.append(SWGate(pos))
        return self
    
    def rx(self, pos: int, para):
        """
        Single qubit rotation Rx gate.

        Args:
            pos (int): qubit the gate act.
            para (float): rotation angle
        """
        if para != 0.:
            self.gates.append(RXGate(pos, para))
        return self

    def ry(self, pos: int, para):
        """
        Single qubit rotation Ry gate.
        
        Args:
            pos (int): qubit the gate act.
            para (float): rotation angle
        """
        if para != 0.:
            self.gates.append(RYGate(pos, para))
        return self

    def rz(self, pos: int, para):
        """
        Single qubit rotation Rz gate.
        
        Args:
            pos (int): qubit the gate act.
            para (float): rotation angle
        """
        if para != 0.:
            self.gates.append(RZGate(pos, para))
        return self

    def cnot(self, ctrl: int, tar: int):
        """
        CNOT gate.
        
        Args:
            ctrl (int): control qubit.
            tar (int): target qubit.
        """
        self.gates.append(CXGate([ctrl, tar]))
        return self

    def cy(self, ctrl: int, tar: int):
        """
        Control-Y gate.

        Args:
            ctrl (int): control qubit.
            tar (int): target qubit.
        """
        self.gates.append(CYGate([ctrl, tar]))
        return self

    def cz(self, ctrl: int, tar: int):
        """
        Control-Z gate.
        
        Args:
            ctrl (int): control qubit.
            tar (int): target qubit.
        """
        self.gates.append(CZGate([ctrl, tar]))
        return self

    def cs(self, ctrl: int, tar: int):
        """
        Control-S gate.
        Args:
            ctrl (int): control qubit.
            tar (int): target qubit.
        """
        self.gates.append(CSGate([ctrl, tar]))

    def ct(self, ctrl: int, tar: int):
        """
        Control-T gate.
        Args:
            ctrl (int): control qubit.
            tar (int): target qubit.
        """
        
        self.gates.append(CTGate([ctrl, tar]))

    # def fsim(self, q1, q2, theta, phi):
    #     """
    #     fSim gate.

    #     Args:
    #         q1, q2 (int): qubits the gate act.
    #         theta (float): parameter theta in fSim. 
    #         phi (float): parameter phi in fSim.
    #     """
    #     self.gates.append(FsimGate([q1, q2], [theta, phi]))

    def swap(self, q1: int, q2: int):
        """
        SWAP gate
        
        Args:
            q1 (int): qubit the gate act.
            q2 (int): qubit the gate act.
        """
        self.gates.append(SwapGate([q1, q2]))
        return self

    def toffoli(self, ctrl1, ctrl2, targ):
        """
        Toffoli gate

        Args:
            ctrl1 (int): control qubit
            ctrl2 (int): control qubit
            targ (int): target qubit
        """
        self.gates.append(ToffoliGate([ctrl1, ctrl2, targ]))
        return self
    
    def fredkin(self, ctrl, targ1, targ2):
        """
        Fredkin gate
        
        Args:
            ctrl (int):  control qubit
            targ1 (int): target qubit
            targ2 (int): target qubit
        """
        self.gates.append(FredkinGate([ctrl, targ1, targ2]))


    def barrier(self, qlist: List[int]):
        """
        Add barrier for qubits in qlist.
        
        Args:
            qlist (list[int]): A list contain the qubit need add barrier. When qlist contain at least two qubit, the barrier will be added from minimum qubit to maximum qubit. For example: barrier([0, 2]) create barrier for qubits 0, 1, 2. To create discrete barrier, using barrier([0]), barrier([2]).
        """
        self.gates.append(Barrier(qlist))
        return self

    def measure(self, pos, cbits: List[int] = []):
        """
        Measurement setting for experiment device.
        
        Args:
            pos (int): Qubits need measure.
            cbits (List[int]): Classical bits keeping the measure results.
        """

        self.measures = dict(zip(pos, range(len(pos))))

        if cbits:
            if len(cbits) == len(self.measures):
                self.measures = dict(zip(pos, cbits))
            else:
                raise CircuitError("Number of measured bits should equal to the number of classical bits")



