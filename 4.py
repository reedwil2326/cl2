from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Qubit 0 = state to send (Alice) | Qubit 1 = Alice's half of the pair | Qubit 2 = Bob
qc = QuantumCircuit(3, 3)

# Step 1: Prepare the state to teleport on qubit 0
qc.ry(1.0, 0)

# Step 2: Create an entangled (Bell) pair between qubit 1 and qubit 2
qc.h(1)
qc.cx(1, 2)

# Step 3: Alice's Bell-basis measurement setup
qc.cx(0, 1)
qc.h(0)

# Step 4: Alice measures her two qubits
qc.measure(0, 0)
qc.measure(1, 1)

# Step 5: Bob applies corrections using Alice's classical results
with qc.if_test((qc.clbits[1], 1)):    # if qubit 1 result = 1 -> X gate
    qc.x(2)

with qc.if_test((qc.clbits[0], 1)):    # if qubit 0 result = 1 -> Z gate
    qc.z(2)

# Step 6: Measure Bob's qubit to verify the state arrived
qc.measure(2, 2)

# Step 7: Run and display
sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=1024).result()
print("Teleportation results:", result.get_counts())