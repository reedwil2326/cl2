from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Qubits: 0,1,2 = data qubits | 3,4 = ancilla (syndrome) qubits
# Classical bits: 0,1 = syndrome | 2 = final result
qc = QuantumCircuit(5, 3)

# Step 1: Encode the state into 3 qubits
qc.ry(1.0, 0)        # prepare a state on qubit 0
qc.cx(0, 1)          # copy to qubit 1
qc.cx(0, 2)          # copy to qubit 2

# Step 2: Introduce a bit-flip error on qubit 1
qc.x(1)

# Step 3: Detect the error (syndrome measurement)
qc.cx(0, 3)          # ancilla 3 checks qubit 0 vs qubit 1
qc.cx(1, 3)
qc.cx(0, 4)          # ancilla 4 checks qubit 0 vs qubit 2
qc.cx(2, 4)
qc.measure(3, 0)     # syndrome bit 0
qc.measure(4, 1)     # syndrome bit 1

# Step 4: Correct the error based on the syndrome
with qc.if_test((qc.clbits[0], 1)):          # syndrome 10 -> qubit 1 flipped
    with qc.if_test((qc.clbits[1], 0)):
        qc.x(1)

with qc.if_test((qc.clbits[0], 0)):          # syndrome 01 -> qubit 2 flipped
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(2)

with qc.if_test((qc.clbits[0], 1)):          # syndrome 11 -> qubit 0 flipped
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(0)

# Step 5: Measure the data qubit after correction
qc.measure(0, 2)

# Step 6: Run and show results
sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=1024).result()
print("Error correction results:", result.get_counts())
