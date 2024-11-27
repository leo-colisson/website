from tp_01_correction import *

print(Options().secpar)

import unittest


class TestsTP01(unittest.TestCase):

    def test_options(self):
        self.assertEqual(Options().secpar, 80, "Secpar should be 80 by default")
        self.assertEqual(Options().rounds, 80, "Rounds should equal secpar by default")
        self.assertEqual(Options(secpar=42).rounds, 42, "Rounds should equal secpar by default")
        self.assertEqual(Options(secpar=42).secpar, 42, "Secpar should be modifiable")
        self.assertEqual(Options(secpar=42,rounds=2).rounds, 2, "Rounds should be modifiable independantly of secpar")
        self.assertEqual(Options(secpar=42,rounds=2).secpar, 42, "Rounds should be modifiable independantly of secpar")

    def test_graph(self):
        g = Graph()
        a = g.add_node()
        b = g.add_node()
        c = g.add_node()
        g.add_double_edge(b,c)
        g.add_edge(a,b)
        self.assertEqual(g.edge_exists(a,b), True, "The edge should be present")
        self.assertEqual(g.edge_exists(b,c), True, "The edge should be present")
        self.assertEqual(g.edge_exists(c,b), True, "The edge should be present")
        self.assertEqual(g.edge_exists(b,a), False, "This edge is not present")
        self.assertEqual([a,b,c], [0,1,2], "The nodes should be labeled 0 and 1")
        self.assertEqual(g.edges(), [(0,1), (1,2), (2,1)], "The edges should be ordered alphabetically")

    def test_hamiltonian(self):
        g = Graph()
        a = g.add_node()
        b = g.add_node()
        c = g.add_node()
        g.add_edge(a, b)
        g.add_edge(b, a)
        g.add_edge(c, a)
        self.assertEqual(is_hamiltonian_path(g, [c, a, b]), True, "This path is hamiltonian")
        self.assertEqual(is_hamiltonian_path(g, [a, b, c]), False, "This path is not in g")
        self.assertEqual(is_hamiltonian_path(g, [a, b]), False, "Do not cover c")
        self.assertEqual(is_hamiltonian_path(g, [a, b, a]), False, "Do not cover c")

    def test_generate_permutation(self):
        self.assertEqual(len(generate_permutation(42)), 42, "Bad length of the permutation")
        a = generate_permutation(100)
        b = generate_permutation(100)
        self.assertEqual(a != b, True, "Highly unlikely that a equals b if truly random")
        l = [ generate_permutation(2) for _ in range(100) ]
        self.assertEqual([0,1] in l and [1,0] in l, True, "Highly unlikely that we don't sample both permutations")

    def test_commit(self):
        m = b'coucou'
        options = Options(secpar=43)
        (r, c) = commit(options, m)
        (r2, c2) = commit(options, m)
        self.assertEqual(check_commit(options, c, r, m), True, "The commit should be accepted")
        self.assertEqual(r2 != r, True, "The randomness is not random")
        self.assertEqual(c2 != c, True, "The randomness is not random")
        self.assertEqual(len(r), math.ceil(options.secpar/8), "The randomness should have the proper size")

    def test_zk_protocol(self):
        g = Graph()
        a = g.add_node()
        b = g.add_node()
        g.add_edge(a, b)
        n = g.len()
        N = math.ceil(math.log(n, 256))
        e = len(g.edges())
        E = math.ceil(math.log(e, 256))
        R = math.ceil(Options().secpar/8)
        path = [a, b]
        (info_open, commitments) = commit_phase(g, path)
        self.assertEqual(len(commitments), 28*(1+1), f"The commitment has not the good length")
        openings0 = open_phase(info_open, 0)
        self.assertEqual(len(openings0), n * N + R + e * (R + 2*N), f"The opening 0 has not the good length")
        (res, reason) = verify(g, commitments, 0, openings0)
        self.assertEqual(res, True, f"The opening of 0 is not correct ({reason})")
        openings1 = open_phase(info_open, 1)
        self.assertEqual(len(openings1), N + (n-1) * (E + R + N), f"The opening 0 has not the good length")
        (res, reason) = verify(g, commitments, 1, openings1)
        self.assertEqual(res, True, f"The opening of 1 is not correct ({reason})")

    def test_fiat_shamir(self):
        g = Graph()
        a = g.add_node()
        b = g.add_node()
        g.add_edge(a, b)
        path = [a, b]
        fiat_proof = fiat_shamir_proof(g, path)
        (ok, reason) = verify_fiat_shamir_proof(g, fiat_proof)
        self.assertEqual(ok, True, "The Fiat-Shamir proof should pass the verification step")

    def test_graph_from_sat(self):
        g = graph_from_sat([[1]])
        self.assertEqual(g.edges(), sorted([
            (1,2),
            (2,8),
            (1,7),
            (7,8),
            (2,3),
            (3,4),
            (4,5),
            (5,6),
            (6,7),
            (7,6),
            (6,5),
            (5,4),
            (4,3),
            (3,2),
            (4,0),
            (0,5)
        ]))
        g = graph_from_sat([[-1]])
        self.assertEqual(g.edges(), sorted([
            (1,2),
            (2,8),
            (1,7),
            (7,8),
            (2,3),
            (3,4),
            (4,5),
            (5,6),
            (6,7),
            (7,6),
            (6,5),
            (5,4),
            (4,3),
            (3,2),
            (5,0),
            (0,4)
        ]))
        g = graph_from_sat([[1], [-1, 2]])
        self.assertEqual(g.edges(), sorted([
            (5,0),
            (0,6),
            (9,1),
            (1,8),
            (16,1),
            (1,17),
            (2,3),
            (2,11),
            (3,12),
            (11,12),
            (12,13),
            (13,14),
            (13,19),
            (14,20),
            (19,20),
            (3,4),
            (4,5),
            (5,6),
            (6,7),
            (7,8),
            (8,9),
            (9,10),
            (10,11),
            (11,10),
            (10,9),
            (9,8),
            (8,7),
            (7,6),
            (6,5),
            (5,4),
            (4,3),
            (14,15),
            (15,16),
            (16,17),
            (17,18),
            (18,19),
            (19,18),
            (18,17),
            (17,16),        
            (16,15),
            (15,14)
        ]))
        # Test assignements
        (g, path) = graph_from_sat([[1]], {1: True})
        self.assertEqual(is_hamiltonian_path(g, path), True, "The resulting path is not hamiltonian")
        (g, path) = graph_from_sat([[1], [-1, 2]], {1: True, 2: True})
        self.assertEqual(is_hamiltonian_path(g, path), True, "The resulting path is not hamiltonian")
        (g, path) = graph_from_sat([[-1], [-1, 2]], {1: False, 2: True})
        self.assertEqual(is_hamiltonian_path(g, path), True, "The resulting path is not hamiltonian")

    def test_game_110(self):
        n = 3
        starting_position = [False, True, True, False]
        (sat, evaluation, last_position) = game_110_sat(starting_position, n)
        self.assertEqual(last_position, [True, True, True, False], "The last position is not computed correctly")
        (g, path) = graph_from_sat(sat, evaluation=evaluation)
        (sat2, _, _) = game_110_sat(last_position, n, is_starting=False)
        g2 = graph_from_sat(sat2)
        self.assertEqual(g.edges(), g2.edges(), "The two graphs (verifier and prover) should be identical")
        self.assertEqual(g.len(), g2.len(), "The two graphs (verifier and prover) should be identical")
        (proof, last_position) = game_110_zk_proof(starting_position, n)
        (ok, reason) = game_110_zk_verify(last_position, n, proof)
        self.assertEqual(ok, True, "The test should pass the verification procedure")
        
if __name__ == '__main__':
    unittest.main()
