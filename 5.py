import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# ---------- Step 1: Build a noise model ----------
# Every H, S and Sdg gate has a 2% chance of a depolarizing error
noise = NoiseModel()
error = depolarizing_error(0.02, 1)
noise.add_all_qubit_quantum_error(error, ["h", "s", "sdg"])

sim = AerSimulator(noise_model=noise)

# ---------- Step 2: Run for different sequence lengths ----------
for length in [1, 2, 4, 8]:
    successes = 0
    shots = 100                                   # number of random circuits per length

    for _ in range(shots):
        # a) Pick a random sequence of gates
        gates = [random.choice(["h", "s"]) for _ in range(length)]

        qc = QuantumCircuit(1, 1)

        # b) Apply the random sequence
        for gate in gates:
            getattr(qc, gate)(0)

        # c) Apply the inverse sequence in reverse order
        #    (H is its own inverse, S inverse is Sdg)
        for gate in reversed(gates):
            inverse = "h" if gate == "h" else "sdg"
            getattr(qc, inverse)(0)

        # d) Measure: without noise the result is always 0
        qc.measure(0, 0)

        result = sim.run(
            transpile(qc, sim, optimization_level=0),   # level 0 keeps gates unmerged
            shots=1
        ).result()

        if result.get_counts().get("0", 0) == 1:
            successes += 1

    # ---------- Step 3: Survival probability ----------
    print(f"Length {length}: Survival = {successes / shots:.2f}")