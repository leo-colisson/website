# Don't load any other library
import math
from secrets import randbelow, token_bytes
from hashlib import sha3_224

### Helper functions


def serialize_list(N, int_list):
    """Returns a byte list containing |int_list| blocks of length N bytes encoding the list of integers
    (N must be large enough to encode the largest element in the list)"""
    return b''.join(i.to_bytes(N, byteorder='big') for i in int_list)

def deserialize_list(N, bytes_str):
    """Inverse of serialize_list"""
    if len(bytes_str) % N != 0:
        raise NameError(f'The serialized list is not a multiple of {N}')
    return [ int.from_bytes(bytes_str[i:i+N]) for i in range(0, len(bytes_str), N) ]

def deserialize_tuple(list_of_byte_size, bytes_str):
    """Like serialize_list but when we have a known number of element of different size. See the pdf for an example of use."""
    if len(bytes_str) != sum([x if isinstance(x,int) else x[1] for x in list_of_byte_size]):
        raise NameError('The size of the serialized couple is wrong.')
    i = 0
    elements = []
    for x in list_of_byte_size:
        if isinstance(x, int):
            elements.append(int.from_bytes(bytes_str[i:i+x]))
            i += x
        else:
            if x[0] == "bytes":
                elements.append(bytes_str[i:i+x[1]])
                i += x[1]
            else:
                raise NameError(f"{x} should be of type integer or string equal to bytes")
    return tuple(elements)

### Your code starts here

class Options:
    def __init__(self, secpar=80, rounds=None):
        print("TODO")
    
class Graph:
    def __init__(self):
        print("TODO")

    def add_node(self):
        print("TODO")
        return 42

    def add_edge(self, a, b):
        print("TODO")

    def add_double_edge(self, a, b):
        print("TODO")

    def len(self):
        print("TODO")
        return 42

    def edges(self):
        print("TODO")
        return []
        
    def edge_exists(self, a, b):
        print("TODO")
        return False

    def get_graphviz(self):
        print("TODO")
        return r"digraph G {n0 -> n1; n1 -> n2}"


def is_hamiltonian_path(g, path):
    print("TODO")
    return True

# Fisher-Yates shuffles
def generate_permutation(n):
    print("TODO")
    return range(n)

def commit(options, message):
    print("TODO")
    return (b'', b'')

def check_commit(options, c, r, message):
    print("TODO")
    return False

def commit_phase(g, path, options=Options()):
    """Phase to commit. Takes as input a graph and a path (list of node ID forming a
    Hamiltonian path).
    Returns a tuple, where the first element is an arbitrary structure kept
    by the prover to help in the opening phase, and the second part is of type bytes,
    and will be send to the verifier during the commit phase. The structure of this is:
    |[224 bits = 28 bytes] Commitment of serialized permutation|
    |[e blocks of size 224 bits = 28 bytes] commitments of each edge, serialization of [a, b]|
    """
    return ({"anything": "you want"}, b'')

def open_phase(info_open, b):
    """
    This is the opening phase. If b=0, the format is:
    |[n blocks of N bytes] serialized permutation |
    |[R bytes] randomness used to commit the permutation |
    |[e blocks of size R + 2N] serialized list [r, a, b] where r is the randomness used to commit the i-th edge (a,b)|
    If b=1, the format is:
    |[N] path node 0|
    |[E] id of first edge|
    |[r] opening of the first edge|
    |[N] path node 1|
    |[E] id of second edge|
    |[R] opening of second edge|
    …(n-1 times for all edges in the path)
    |[N] last node in path|
    """
    print("TODO")
    return b'TODO'


def verify(g, commitments, b, openings, options=Options()):
    """This checks if the opening is correct based on the commitments and the challenge b."""
    return (False, "TODO, give here the reason of a potential failure")

def get_bit(bytes_str, i):
    """Function provided: Returns the i-th bit of the byte string bytes_str"""
    return 0 if (bytes_str[i // 8] & (128 >> (i % 8))) == 0 else 1

def fiat_shamir_proof(g, path, message=b'', options=Options()):
    """Fiat-shamir transform, extended to also allow signature.
    The output is the concatenation of the commitments followed by the concatenation of all openings."""
    return b''

def verify_fiat_shamir_proof(g, proof, message=b'', options=Options()):
    """Verification procedure, outputs a tuple (ok, reason)."""
    return (False, "TODO: put here the reasons of a potential failure of the verification")


def graph_from_sat(sat, evaluation=None):
    """This takes as input a sat formula, i.e. a list of list of integers >= 1.
    When it is negative integer -i, this is interpreted as the negative literal i.
    (hence the removal of the 0 integer). From this, we generate a graph
    as described in the course. For compatibility reasons, the naming of the nodes
    is done as follows:
    - the node associated to the first clause is given id 0, then the next clause is 1 etc
    - then, we follow the order of the nodes given in the course for the diamonds, where ID increases from top to bottow, then left to right. The first diamond corresponds to the first variable, ordered by (absolute) value.
    - in the horizontal line, the groups of two nodes corresponding to a given clause to fulfill are added in the order they appear in the "sat" input list (from left to right), i.e.\ for a given variable .
    - the convention is that a true clause will follow these horizontal nodes from left to right.
    For simplicity, we assume that a clause never contains both a and -a (these are trivial to ensure).
    Evaluation is either none, or a dictionary t such that T[i] contains the assignment (True or False)
    to the variable i to make the sat formula true. If set, this function also generates a Hamiltonian path.
    """
    g = Graph()
    path = []
    print("TODO")
    if evaluation:
        return (g, path)
    else:
        return g

class Circuit:
    def __init__(self):
        print("TODO")

    def get_sat(self):
        print("TODO")
        return {}

    def add_var(self, val=None):
        print("TODO")
        return 1
    
    def is_true(self, a):
        print("TODO")
    
    def is_false(self, a):
        print("TODO")

    def add_and(self, a, b, c=None):
        print("TODO")
        return 1

    def add_or(self, a, b):
        print("TODO")
        return 1

    def add_xor(self, a, b):
        print("TODO")
        return 1

    def add_not(self, a):
        print("TODO")
        return 1
    
    def get_evaluation(self):
        print("TODO")
        return {}
    
def game_110_sat(starting_position, n, is_starting=True):
    print("TODO")
    return ([], {}, starting_position)

def game_110_zk_proof(starting_position, n, options=Options()):
    print("TODO")
    return (b'', starting_position)

def game_110_zk_verify(last_position, n, proof, options=Options()):
    print("TODO")
    return (False, "Reason to fail is not implemented")

