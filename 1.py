# Import required libraries
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Step 1: Create a circuit with 16 qubits and 16 classical bits
qc = QuantumCircuit(16, 16)

# Step 2: Apply a Hadamard gate to every qubit (puts each in superposition)
qc.h(range(16))

# Step 3: Measure all qubits into the classical bits
qc.measure(range(16), range(16))

# Step 4: Run the circuit on the Aer simulator (1 shot = 1 random number)
sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=1).result()

# Step 5: Display the result
bitstring = list(result.get_counts())[0]
print("Random 16-bit number:", bitstring)
print("Decimal value       :", int(bitstring, 2))   # optional: shows the number in decimal