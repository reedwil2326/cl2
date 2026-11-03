from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator

# Step 1: Create a circuit with 5 qubits and 5 classical bits
qc = QuantumCircuit(5, 5)

# Step 2: Prepare an input state
qc.h(0)               # qubit 0 in superposition of |0> and |1>
qc.x(1)               # qubit 1 set to |1>

# Step 3: Apply the 5-qubit QFT
qc.compose(QFT(5), inplace=True)

# Step 4: Measure all qubits
qc.measure(range(5), range(5))

# Step 5: Run and display
sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=1024).result()
print("QFT results:", result.get_counts())