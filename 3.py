# pip install qiskit qiskit-aer
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# ---------- Problem definition ----------
# Board cells are numbered:   [0 1]
#                             [2 3]      (0 = blank tile)
START = (3, 1, 0, 2)
GOAL  = (1, 2, 3, 0)
DEPTH = 3                                   # number of moves in a solution

NAMES = ["up", "down", "left", "right"]     # rule 0,1,2,3 (2 qubits per move)
SHIFT = [-2, 2, -1, 1]                      # how the blank's index changes per rule


# ---------- Production rules ----------
def apply(state, rule):
    """Apply one move. Returns the new state, or None if the move is not allowed."""
    b = state.index(0)                      # position of blank
    n = b + SHIFT[rule]                     # new position of blank
    if not 0 <= n < 4 or (rule >= 2 and n // 2 != b // 2):
        return None                         # off the board / wrapped around a row
    s = list(state)
    s[b], s[n] = s[n], s[b]
    return tuple(s)


def decode(k):
    """Convert basis state k into a list of moves (2 bits per move)."""
    return [(k >> (2 * i)) & 3 for i in range(DEPTH)]


def reaches_goal(k):
    """Check if the move sequence k takes START to GOAL."""
    s = START
    for r in decode(k):
        s = apply(s, r)
        if s is None:
            return False
    return s == GOAL


# ---------- Find marked states (used to build the oracle) ----------
n = 2 * DEPTH                               # total qubits = 6
marked = [k for k in range(2 ** n) if reaches_goal(k)]
print("Solutions (basis states):", marked)


# ---------- Oracle: flips the phase (-1) of every solution ----------
oracle = QuantumCircuit(n)
for k in marked:
    zeros = [i for i in range(n) if not (k >> i) & 1]
    if zeros:
        oracle.x(zeros)
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)   # multi-controlled Z
    oracle.h(n - 1)
    if zeros:
        oracle.x(zeros)


# ---------- Diffusion: inversion about the mean ----------
diffusion = QuantumCircuit(n)
diffusion.h(range(n))
diffusion.x(range(n))
diffusion.h(n - 1)
diffusion.mcx(list(range(n - 1)), n - 1)    # multi-controlled Z
diffusion.h(n - 1)
diffusion.x(range(n))
diffusion.h(range(n))


# ---------- Grover circuit ----------
qc = QuantumCircuit(n)
qc.h(range(n))                              # superposition of all move sequences

iters = int(np.pi / 4 * np.sqrt(2 ** n / len(marked)))
for _ in range(iters):
    qc.compose(oracle, inplace=True)        # 1) mark the solution
    qc.compose(diffusion, inplace=True)     # 2) amplify it

qc.measure_all()


# ---------- Run and display ----------
sim = AerSimulator()
counts = sim.run(transpile(qc, sim), shots=1024).result().get_counts()

best = max(counts, key=counts.get)
top3 = dict(sorted(counts.items(), key=lambda x: -x[1])[:3])

print("Grover iterations:", iters, "| top results:", top3)
print("Solution moves:", [NAMES[r] for r in decode(int(best, 2))])