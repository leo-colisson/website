from tp_01_correction import *

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
        self.assertEqual(check_commit(Options(), bytes.fromhex("0b04c09abd3803bf921fc68d60d3bcbebbbc24c38edb4db2c8b7fd5f"), bytes.fromhex("87872e1e2c7e66ac102f"), b'coucou'), True, "This commit should be valid. Have you used sha3_224?")
        self.assertEqual(check_commit(Options(), bytes.fromhex("0b04c09abd3803bf921fc68d60d3bcbebbbc24c38edb4db2c8b7fd5f"), bytes.fromhex("87872e1e2c7e66ac102a"), b'coucou'), False, "This commit should be invalid.")

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

    def test_fiat_shamir_randomness(self):
        self.assertEqual(fiat_shamir_randomness(Options(rounds=10), b'randomcommitment', b'my message'),
                         [1, 0, 0, 1, 1, 0, 1, 1, 0, 1],
                         "The randomness extracted for the Fiat-Shamir transform is incorrect (single application of sha3-224)")
        self.assertEqual(fiat_shamir_randomness(Options(rounds=300), b'randomcommitment', b'my message'),
                         [
                             0, 1, 1, 0, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 1, 1, 1, 1, 1, 0, 0,
                             0, 0, 1, 0, 0, 1, 0, 0, 1, 0,
                             0, 1, 0, 1, 0, 1, 1, 1, 0, 1,
                             0, 0, 1, 1, 1, 0, 1, 0, 0, 1,
                             0, 0, 1, 1, 1, 0, 1, 1, 0, 1,
                             0, 0, 1, 0, 1, 0, 1, 0, 0, 0,
                             1, 1, 1, 0, 1, 1, 0, 1, 1, 1,
                             1, 0, 1, 1, 0, 0, 0, 1, 0, 1,
                             1, 1, 0, 1, 1, 1, 1, 0, 1, 0,
                             1, 0, 0, 1, 1, 0, 0, 1, 1, 1,
                             0, 1, 0, 1, 1, 0, 1, 0, 1, 1,
                             1, 1, 0, 1, 0, 1, 0, 1, 1, 1,
                             0, 1, 0, 1, 1, 1, 1, 0, 1, 1,
                             1, 0, 0, 1, 0, 0, 1, 0, 0, 0,
                             1, 1, 1, 1, 0, 0, 0, 1, 0, 0,
                             0, 1, 1, 0, 1, 1, 1, 0, 0, 0,
                             1, 0, 0, 0, 1, 1, 1, 1, 0, 1,
                             0, 0, 0, 0, 1, 1, 0, 0, 1, 0,
                             1, 0, 0, 1, 0, 0, 1, 1, 1, 0,
                             0, 1, 1, 1, 0, 1, 0, 0, 0, 0,
                             1, 1, 0, 0, 1, 0, 1, 0, 0, 0,
                             1, 1, 1, 1, 0, 1, 1, 0, 0, 1,
                             0, 1, 0, 1, 1, 1, 0, 1, 0, 0,
                             1, 0, 1, 0, 0, 0, 1, 1, 1, 1,
                             0, 1, 0, 0, 0, 1, 1, 1, 1, 1,
                             0, 1, 0, 1, 0, 0, 0, 1, 0, 1,
                             1, 1, 1, 1, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 1, 0, 1, 1, 1, 1, 0,
                             0, 0, 0, 1, 0, 1, 0, 0, 1, 1
                         ],
                         "The randomness extracted for the Fiat-Shamir transform is incorrect (multiple applications of sha3-224)")
        
    def test_fiat_shamir(self):
        g = Graph()
        a = g.add_node()
        b = g.add_node()
        g.add_edge(a, b)
        path = [a, b]
        fiat_proof = fiat_shamir_proof(g, path)
        (ok, reason) = verify_fiat_shamir_proof(g, fiat_proof)
        self.assertEqual(ok, True, "The Fiat-Shamir proof should pass the verification step")
        # If we change the signed message, this should not pass anymore
        (ok, reason) = verify_fiat_shamir_proof(g, fiat_proof, message=b"unrelated message")
        self.assertEqual(ok, False, "The same Fiat-Shamir proof should NOT pass the verification when changing the message")
        # If we change the security, this should not pass the test
        ok = False
        (ok, reason) = verify_fiat_shamir_proof(g, fiat_proof, options=Options(130))
        self.assertEqual(ok, False, "The same Fiat-Shamir proof should NOT pass the verification with higher security")
        # We try to send an explicit proof to check if the test passes:
        (ok, reason) = verify_fiat_shamir_proof(g, bytes.fromhex(
            "ee74b82ec5056e4528d1d49600e627b0cfcf6b6b15021d28fd86527ddb6120175974527e3798233f8e06b75a7c2757dd26a6" +
            "fc7b5c14269c0e12bfe952866f72db435aaa829fba222c183815f47f6d3d8f2b90c4c12c9e37b101015ab186f27a906beb17" +
            "192fdf6c7a7090e8758bdede0a710562f51bba996db5a4c37e1bb3bfbc3987de711c6e315b41d7084601957e778494e4b5cf" +
            "3bc7a731a12b1f05fd7c688c7395974121f22106f2c44d2c1384a9eec8cecd955b69e0d652a373f13d18508f8b04f96b5b7c" +
            "9214ae12aabf3697337edd69fc7abc5b273d4c3c96b117b2a434a257a129838cb7638aa7afda04f00b8fd3d1d6b28edf7352" +
            "ec58a3d9070c87f214e00f037631397ef760edddab737e4dc9386b058234ab0022f5c763a4586766c96343e3c3638552ed21" +
            "aa5b1024cbd6ec385971b79991c4f2201bca3f7b7723e5da4d0c3465082c1a1f140028ebceecd2ca1c09278086a1471d3d28" +
            "c8cfe5c47c66098a20fdbe3140a3c81ad74222b87cb5ba8689b61f67453ca1935d05f8cf640246c2cb6946b609efd79ad6bf" +
            "9785e253e59f040995456b4e89d80b4585ac57234e5bd58e1c8ebb4140717c52efba6a6d1ab76e3c79f5b90bd00d02c33b2d" +
            "e34d1eba4af3a2d546b9e2022fd844f57a64f12d7b335d2e5ce88ce1557a048a53a0928f468efe57dca64badfd14d465e994" +
            "09579d9f2e24f8171579b097cae8a6df441f91a42ad9cbb6df7575d87853ff6195946ee18f8ba36b5c1be37d43b518c20083" +
            "03371187224a73ae95b565f1157d84cd78f6a1603350cb358e5923d39973c0b1bc20c10935ebfa1c18c4ec4c9e0f99ce099d" +
            "ba1e83c4810a219c79bdb86120a656777a2c257de074d9cb28ded38529ccde09ce7988635d452b9c95b2a01a9a0fd92330ef" +
            "20b33e71cc8408cb9af6579aa5906cad873eb75782e04232068b77667071d13113296288f3f4df4751678ebec01f29bdbe80" +
            "94eceacb8eb1b3744edce1c77080167a6098eec1436394ba24253d1c3dcf8e390d51481aa4463f04d27cbf4c27b7929beb56" +
            "62172655782e73b621ebc28caa5754b260e5a2357bdc8ad1f137fcb743ea9f2c5e8cb73830ddd025db84640672f52eb0aaf3" +
            "99edef13000183a0e9ac42ea9ce73f0160467ec736a4108c9cba3abf77fac83f13dbbb310d4d89b7b65c91f878d72e01d469" +
            "84959f96e26e8ee5966125267710a0118a8dd89582e4866c0a62b697ca8964020260776ae1f089c64b6b50e8afe1b388c9ee" +
            "d2f10eeedc53ecfc4fc3440d41ebf53e9b87e58c0de1ae2c06eef43986916279a2a8b57dfbf996686ff95e2f3a04e457eb62" +
            "0e4f268adb3ca1a6d1569a3310b92a7c01d66190774762bb49574f7ff85c561a65a9b59b046b72e2fa231cd419cf4aed24be" +
            "a05676c810aaab6afac03224d6a5fc5a7c54c21ce57c039f0e443db74ecbc793b6baed563dd63e8f4ad02d0c0c4b8d266105" +
            "8a0f7b63ba1e5e714f687d47288f8cbef330ccb2245a1a2f43ad9c302c88311e4016603cb8146db37a80b5be15679245117a" +
            "cde728e8dfe6443f76518305f0bccd57b77cd1af5e4d529b910ba970fd2df5e35210d8ea59dc46c126a395cb04d988b04e3c" +
            "e5c2323b32b4aa49d3d66ff20e8f9c27378a51c44d666119c6aae836c9114f9992cfb13449dd33b49b2f5bb698f8c25de904" +
            "4fbd4b88fde838bf392c8ee029aad6bc2a606e22f30e741f95c64271359a3ef622179559ff74050c087635b498dc2d12ac97" +
            "11d7f88140e979da79d191ec0922d7826b2a5b4570af624264410f2c08a9b8309f998bb09e6b0330a1c3ea42d0268d66219c" +
            "f6d19b80560a7337fc2c94b70da9450750d82f8a7907df978adc180138e12631cd23bc2e7c8700913e9c269028e7f63daaf9" +
            "fa3eec0526f85e9f4fed95abdd6b3c9c09a0fb8b8f88f63bef63e1b4943a1fbc1641b62be59a25740ebb98c978576a4f85bd" +
            "7ffc4183ba3f322ce233a805e26f9e655431fc47dc4446bddcea0e693204339ba3fbf18e357a53765ee5cb60f134b1753076" +
            "1db0e859e1a7a9a514da5595a179e1fc285be8fb0e82a1064e74f877778c1a0f2f1f11bd6df59bbc281247108a5ef934dc59" +
            "c611130acc27cc92f61fb793fd6706ab6138c1dd46dea2c4f051c400cc668c97eb17093afe3cf7be358006713bb0aae77c7f" +
            "b66a77d47a107c42769933f9f76c36624212e6c6328e2c971a7455f8761b45e2e7aecf48ead51099ea8ed26868382c67fb67" +
            "36607ff9394587284e9743a11a3b67a7f14807bea419708a0a4ba717731dc9be3462214401c70c7a97817e36e57d64f8ac79" +
            "141e2cf899ac392524a3d25e76d9e3411e228242d283d8273e6ba79d5f5b470ea770aab2fea593a913055b1b65b6e911ce28" +
            "d84c95eb218bd24c9ae86ddf6a0d1f0458b0f506916ce151c2c543cb2baebb098ebecec5362373a47b1b5792c2343fca70a6" +
            "9d1c5e696954e8fdd405dfa58099f563f1f6c9b34225fb90c4ca27bdba234927c6af1a4f3907d7a4bfae1dd9879f7eb8e536" +
            "1d92e73fb1cdc8980ac325a9b319d37be3e52b165465699e8eb13a4710182f99052fdab9e39b6d56f0d93fc151d7429ae5fc" +
            "4beabc439e28ee9c423f9c778eecb3fab83822ca3f6098357ad2f06684b2f22a7b4b692bf23c765cd58a26f1e06776a380de" +
            "2f2d8b72c685cc8576b426b2e4b5a3847ef193deb83ab6ce2a86c760c79cd96ea45438c189fa609c4c8ffb122e0e2f0f9ac5" +
            "1da35427d213cf5bb2caa1b73e96e5087c87a15c03dcd6e313cc6abe96634edb91e3b6ccba828ad995fa7adbb7ec6f2d6434" +
            "e007c406e0d3be6f2b52c5afa54547a4fe191f32e202fae7b1ed85561715d30672336e7b000b67ad9cfa518fc74347df99a2" +
            "76ef5e47737c09f69224ca140616dea0ef10324185846832a1feb072b19d0777ef20fd5ef6b1adbcd303509a903f54e2bded" +
            "f49a4a63d655888cc9a70ef478d2562dee494012fae5be250e5ec7704770bcdc328546976e3ec218c77f41576d13f8ecdba4" +
            "d64cd2dde412deabfa7475128a25bee815caec16bac6fe3af72a5b42ab28655fc4c51dfb7196d55bdf260c4a7378a6bbd3fa" +
            "8a10b1b94918089d44279209ef84081d88e6ad6614efe4a0a20e575dea153e897100c04e3318795556563dd13a948aeae2e9" +
            "5dc7f590febadf4871f8a6c20d9a3c2fd8d71303485750dda8cd38edb70052a6d6100268c110e9740dc7523bf73a82338831" +
            "5d043ad565e906fbe79cc9bdcb7d27d2342a57fb8ca5d34617a4ac38ec1e20b66e3fdbed6f31adeaaf182f14d24f803acf11" +
            "5bbb4e5240437336cafbfee0f4c0c6756800b6b9232d7f31924c699d5e436ec0dc93a8c7331ba6d03ace29787a9925e77adf" +
            "a6ee77b41352f2f69e9f2ccaa77d1b3fd1d0d747a6d89f26dba893fc5a165856c7f8b47773b6cf7705ec52b3785e24cf17a3" +
            "cfae67ac071f669a7363e83a4aab842b9cccb8beb1381ca9742ec9e4cfc3872f3b813696da1c53b92fce84e7b96f6f26d8a2" +
            "d7941899c6c765bcde22d09b4e86c8dfe19e2a393d08b283a97110d66a2f130767c3d2b28401e2175a833c808f976196fc8b" +
            "f03cbddd285b88312ed21a40d44664e26d5d712bb98caa3c33730d9ba94f089c102d7b364ecd40d3958dfcb6b2e4599b4fc3" +
            "0b659501b5a1e0db6421bbefaa2bcfaf8f7de592936be9ee9332a11a345335d257ddee41263b7f4fc0e8e333a261f424912d" +
            "1f8c04847a7c98ac727c182ecb3be76b79ea62e15981869ad14bea81e3307c428126eaa693258720ccef3bbc3189bd93dd77" +
            "47b1224cd34b8f8dda9fcc99dd076be9b99b2cbfc051756a5f0c3c2cadc1891b27c128bcfb6c42fa6e38aa25efcff1fd5e18" +
            "c523fb2b4773aae68403f664cd19ca0c3f693b5e2fd800c30bddd5e922bf90515f63381053f2a9e2b497e1e8ca6853665aca" +
            "be98b3401f64203ead46203ecbac21c1a96de016a39fb57bc98d0b3d5b72d5218526b47289a78986aced7f5ebae6e93660a6" +
            "f50355a23cca061210af46fd71236980c28fcf562e1c7c156a364ed625d56d8a7eb3f33e1f6b21d01e28f2856d84e2ba580c" +
            "ada9328468830777f85326a354a178e6b8a34ecf365529a281e35e2f71088e38dcdedc041393ec4c91a65f8bd9b74f8e93c3" +
            "8edaa4a590a75621ecc163532e544c1d28127fdaa8918e1c026bfb43fb02852a920122c8eff12493ff4e90849344c6c3bf31" +
            "cccc05798b2bba873b93c9fa9832666448fd8be746131bf6225d5bf17ff58bcb391b6eff4e7809f5582fa90c5a2f1b8927cf" +
            "a235fe96de94befc06667ea20218f7979c8637172bf947ae8de73faa3cc4f1db55669390abcb2bead1099f794e60cc83a772" +
            "4bce52b40335fe28d515eb0944679333ff23c37ffdced19b8ea222575bb04f77950f55dff8d6fb2573ef95b7e8f6137d1022" +
            "dee1c095179b6fc540a89cba783838839f5dcf0fe8ce7131c20169a601459388f3370fbeea126ae86cfdcebd78c705f2f389" +
            "4dccaf9945346f478d4975782c59a8f8d618eadae3635b8d8d86f13e501c7885351c61ede2e06924075b8c272a004966eff9" +
            "b73eecb58fd29644297a2eeba30cdd8f601d210c5c3e060959a9bcf5e776a1234d8529b21dd2f0954927ca43cc7121f41858" +
            "5018e6e030893426544e7549fd507694c946cde2c09254befb03dd9e32b2f206587b532f026d83e5feb1f96193c1291ef9f2" +
            "4bc21ba3c5ebfd359b2b99c5cd8ca14c44a090ac5f1ae464d59d874b49261c496cc91071d757b1f4dca7cd4b8249de1b7444" +
            "ab95a8f9da5a5b77b451533abf8817e955f41b4db77c377ba76b6e537b40dfa1bc6882106a0a761b26ea0c952d355344d176" +
            "bf0f858bf129fd65cc9062d1c9c08f23dade68a83f595656ceacd9108d98aa3fb00eb9b34a3afec9f61bf7bab093974445a6" +
            "49afc2d77b4a94c6b977655e1a1e78ad79fe2cbaecb6392dc353252419be70206e567a4661972b4d27b30e523bab36320eaa" +
            "ba3c8aa24da43e18655c96acbca313f8b9048c6b30eedb25c635015c0f7cc319385ec719cb163bb0e29ca11cfacc83af46c0" +
            "59b7eddeedd68f35eee81a94651907a2940e09f6207678b67240f664afe92e0b084aad994a7b78c8ab64a15cbb80065d544f" +
            "1dad4e16f20f10c744e0f89ab513454c99982746e66f5ec77f0832577b3aa16880fced6ad6b24d8c5088ddf32f637668d187" +
            "855ad20a0e71bf27de19979b8dbcc807d48f038446421dbb5d2817301a6dd131b4fc34e1fa6bcf60f0d9ce91a47e2b95bf4d" +
            "c00ff36f150398dc9ca9af22c15998012b10cc073a9b567ad551edd8ec767632eb78d67fc347b263a0633d24a85a7b079e9e" +
            "1ae3a7027820e6bd2418d07b1e3016abfa02155d9c23471f41a20b6e179518265e4254331015117808646196f4411d0aedf1" +
            "0abe59c2fb3574f221c8a95999fa2cb69c7457168d7c055bcb51b3e88e405a945182fa4283af9084e6892a51b4b9596f161d" +
            "cec2cf94a66efe12bd750fc877d315f98ecd679ac3823d60887c34f79ede0f64e0cc7e1bde5baf640eb93f54a620813105a5" +
            "90e5b39ec66cfa535c8e57952526c5854c5a92bf2527b19ea274256721daa544d83a7780aed863c89f420e0621b2fe2c0415" +
            "f723f732b106e3b9148161a667ad12e2e83ef5a427c4dfbfb76e12517f19d2705b407cdcd18aefb2fa70e68919857db9432f" +
            "d7dee76c2a1313de78e60f6aa6d6a1627aeed190f1cc414a2a56f33490e4847fd034a2be2a0d00afe692ddd6a8dee55932c4" +
            "2107169557bbf45e2f77da912790b988cd972362d47e172c458550356a4c4594b7d7a46ba9a1758098063925f1f0703baa29" +
            "d78553981345e969eaf366709f550515f91a4fdd6c4054a230ad51303f3605ea75057b2c02a73d9617377a0be44a5aada95c" +
            "89adddf6b8bd31d51ea56bfdd280a99ef7249f35b860c387d11483b343b6003ebe871fa7cda47e41f82ab1cb18a71f95f265" +
            "fea86369ec257a1902937e1dccc62fbb3745826faa03c6c48fdb275ed9d9c0f7bad78dc9eb1c0f71b66ec1f2afb66d699ef3" +
            "7e805cf4d860d8cb381c926cdefe2fad4d77cf003d040a285ab46ddb9d8a8e1fb868383e0e091a29bfbd85f8d09bd10e873d" +
            "db5555be8ac35d105f2bb300258388b48a5846d95036d04ec6059e6fcde83d23abbce3d157caeb5f3646c56e8107e0043aea" +
            "5961a0382d90c9d6b0f9d7760b921d0f05b4a19509427fe6410e9caf07177904763eebee0c7911987d154ff0e3b5df36da83" +
            "7de18bf59c49851565f3497e02fc011c2159cbec6ec315e0f05760d3de480001b389e5af921e7cc6717c014920080d18f45c" +
            "f5f1000101fa2ac508c8910584412500010c976668ba7056bc6f15000001612494ee909c4af26a6cb6c73976771a5fce7a1a" +
            "0001001c666e4b97c6d69394d4010169b2e0a1e3aec525e1c00001d3f63abedf5e88f530ec000082b480373debea628f8701" +
            "010008d30d3260fba3500c3b9dad4934fa585fb987940100013c2c5b86fdf94be3972300000198fc9a7e564cb8a23704c482" +
            "7ebd8c2ab6d02d1800010122c0530b32d6853f2148000061700fffd0e5410762320101a1d7ca9a35173e7faa8f000100674b" +
            "9b578b7f24887f89668d9d4b36caf6ca2ca5010001a9deecb6d636a3d061ea0001985d2fdcac27a9c1033600014da6280819" +
            "c9c3eb881f00003ceefe3ec1006ac09a5f0101ce1309c91dd23b118160000138865edd2be524eb5f1c000100c62aa7e46b2f" +
            "69adde195ec62235bbbfd1497189010000e7a1b91859e241c0803e010001f34281d8570ca71b6c6b060e7861a716a42cb860" +
            "000100fba2a29d68abe55752f1010100e09d2e14bf8ce48a8160013da1570843945ab96b01000001fb8bee3d3dfbe6eefa68" +
            "2f341024bcfbcc84bfa5000101094d2c8470875c23d1f0000001a8b9d5c799311e7e91703ff9805c5ece87cf800400010001" +
            "aa3a9eb113d9086dd51d093c2dedfc8aa054b8890001001cd4117cdef56ab1b352010100ca4663561e184146736087b60591" +
            "cfc444918c750100010329770f803df4392ae0000100dddfd099a97de424522712d22d9254c7559b4207010001bb5930b511" +
            "5e93ba57840001265da70d33e15bfdb8dc0000654801e2e36d570fb5b401019eb6fe06d9a9f5e4aa7e00000103e17dd4a5e7" +
            "90fa47d612c4f486bfa023f05bbb0001000165470a9ad4cdd077dad921ac172346183eba78d5000101b8653293591b7fe2ff" +
            "5300010002b63751a8235cfb9e38b2b252effcda19b5e98c010000018762d72c83088cb6916353847850bdf53b7e9ae80001" +
            "000123ce051b93648cc36424ebac7d71cac72ea3f19c0001012e65bb10b0fea95e3fcb00012925ec1ca13e984557f8000001" +
            "e31e96518d498733f2a06d4fd5306d98bcc03674000100a517d27267ab5d4ace63010028229b2cd1115e0ef777010100ca58" +
            "38fac30288403d41d0b3bf02ffe3693828190100016bf29aed8f3b770bc57200010040fdbae21bf2c08c0cf30adda0c6b516" +
            "83bfb8fe0100004980264576812e9461f10101000fcdabe667f60669195fc5ff4a5daef1b918cebd010001368bc069b82076" +
            "23152a000100dab46a82a1552eff649f9ee254df14b743c83b7e01000001bcbc3331ab70da075c1199481e7458f0f918283f" +
            "0001014e83fdd1be23c126f4d5000001378ca7ab8e1813a734a9c378d781ef7d11508358000100801a9b857d94ed23f69001" +
            "0001cb8d849873a47520891748d8896f521cbd31d5c000010100f5eefc51d580debb82d393501a9a5a5c476c525a01000043" +
            "cebb14fe7636f0ce73010100121edaabf78f47bb438ce56618d5309f9a6d022e010000017d4ea8be6371b2a01b783d1094c2" +
            "c28258ed1c28000100b57b2f24c48074f61340010001a5bfaa3b54f415bf15f24444f926579b76a2d65900010001bc2b59e1" +
            "52394f7452c64de0bf46c21e67bd73ea00010104afe6c3546bf4a674c0000156f62071a47a6cf9c5c50001004302607d318c" +
            "7f324f4a80b0346bdd59890848500100000127cf61fea370187af284879ef4d3b201f62dc7c9000101d60087ef7232c9ea0c" +
            "19000047308ae1b15e4d0b25770100017a928172dae3670eb520e3ede7b105986b48890700010142b2c8d308fbe99d918600" +
            "0052b965fcf544c68e160f010100558b02d10a8b0428d7bbd5e0817f84e75f9f65d101000001fd8df7722f4d48d2bc74977c" +
            "fa8425eeb62c0da2000100a423fae29ee2fb9afce101"))
        self.assertEqual(ok, True, "We expect this fiat-shamir proof to be true")
        # We try to send an explicit (unvalid) proof to check if the test passes:
        (ok, reason) = verify_fiat_shamir_proof(g, bytes.fromhex(
            "ee74b82ec5056e4528d1d4a600e627b0cfcf6b6b15021d28fd86527ddb6120175974527e3798233f8e06b75a7c2757dd26a6" +
            "fc7b5c14269c0e12bfe952866f72db435aaa829fba222c183815f47f6d3d8f2b90c4c12c9e37b101015ab186f27a906beb17" +
            "192fdf6c7a7090e8758bdede0a710562f51bba996db5a4c37e1bb3bfbc3987de711c6e315b41d7084601957e778494e4b5cf" +
            "3bc7a731a12b1f05fd7c688c7395974121f22106f2c44d2c1384a9eec8cecd955b69e0d652a373f13d18508f8b04f96b5b7c" +
            "9214ae12aabf3697337edd69fc7abc5b273d4c3c96b117b2a434a257a129838cb7638aa7afda04f00b8fd3d1d6b28edf7352" +
            "ec58a3d9070c87f214e00f037631397ef760edddab737e4dc9386b058234ab0022f5c763a4586766c96343e3c3638552ed21" +
            "aa5b1024cbd6ec385971b79991c4f2201bca3f7b7723e5da4d0c3465082c1a1f140028ebceecd2ca1c09278086a1471d3d28" +
            "c8cfe5c47c66098a20fdbe3140a3c81ad74222b87cb5ba8689b61f67453ca1935d05f8cf640246c2cb6946b609efd79ad6bf" +
            "9785e253e59f040995456b4e89d80b4585ac57234e5bd58e1c8ebb4140717c52efba6a6d1ab76e3c79f5b90bd00d02c33b2d" +
            "e34d1eba4af3a2d546b9e2022fd844f57a64f12d7b335d2e5ce88ce1557a048a53a0928f468efe57dca64badfd14d465e994" +
            "09579d9f2e24f8171579b097cae8a6df441f91a42ad9cbb6df7575d87853ff6195946ee18f8ba36b5c1be37d43b518c20083" +
            "03371187224a73ae95b565f1157d84cd78f6a1603350cb358e5923d39973c0b1bc20c10935ebfa1c18c4ec4c9e0f99ce099d" +
            "ba1e83c4810a219c79bdb86120a656777a2c257de074d9cb28ded38529ccde09ce7988635d452b9c95b2a01a9a0fd92330ef" +
            "20b33e71cc8408cb9af6579aa5906cad873eb75782e04232068b77667071d13113296288f3f4df4751678ebec01f29bdbe80" +
            "94eceacb8eb1b3744edce1c77080167a6098eec1436394ba24253d1c3dcf8e390d51481aa4463f04d27cbf4c27b7929beb56" +
            "62172655782e73b621ebc28caa5754b260e5a2357bdc8ad1f137fcb743ea9f2c5e8cb73830ddd025db84640672f52eb0aaf3" +
            "99edef13000183a0e9ac42ea9ce73f0160467ec736a4108c9cba3abf77fac83f13dbbb310d4d89b7b65c91f878d72e01d469" +
            "84959f96e26e8ee5966125267710a0118a8dd89582e4866c0a62b697ca8964020260776ae1f089c64b6b50e8afe1b388c9ee" +
            "d2f10eeedc53ecfc4fc3440d41ebf53e9b87e58c0de1ae2c06eef43986916279a2a8b57dfbf996686ff95e2f3a04e457eb62" +
            "0e4f268adb3ca1a6d1569a3310b92a7c01d66190774762bb49574f7ff85c561a65a9b59b046b72e2fa231cd419cf4aed24be" +
            "a05676c810aaab6afac03224d6a5fc5a7c54c21ce57c039f0e443db74ecbc793b6baed563dd63e8f4ad02d0c0c4b8d266105" +
            "8a0f7b63ba1e5e714f687d47288f8cbef330ccb2245a1a2f43ad9c302c88311e4016603cb8146db37a80b5be15679245117a" +
            "cde728e8dfe6443f76518305f0bccd57b77cd1af5e4d529b910ba970fd2df5e35210d8ea59dc46c126a395cb04d988b04e3c" +
            "e5c2323b32b4aa49d3d66ff20e8f9c27378a51c44d666119c6aae836c9114f9992cfb13449dd33b49b2f5bb698f8c25de904" +
            "4fbd4b88fde838bf392c8ee029aad6bc2a606e22f30e741f95c64271359a3ef622179559ff74050c087635b498dc2d12ac97" +
            "11d7f88140e979da79d191ec0922d7826b2a5b4570af624264410f2c08a9b8309f998bb09e6b0330a1c3ea42d0268d66219c" +
            "f6d19b80560a7337fc2c94b70da9450750d82f8a7907df978adc180138e12631cd23bc2e7c8700913e9c269028e7f63daaf9" +
            "fa3eec0526f85e9f4fed95abdd6b3c9c09a0fb8b8f88f63bef63e1b4943a1fbc1641b62be59a25740ebb98c978576a4f85bd" +
            "7ffc4183ba3f322ce233a805e26f9e655431fc47dc4446bddcea0e693204339ba3fbf18e357a53765ee5cb60f134b1753076" +
            "1db0e859e1a7a9a514da5595a179e1fc285be8fb0e82a1064e74f877778c1a0f2f1f11bd6df59bbc281247108a5ef934dc59" +
            "c611130acc27cc92f61fb793fd6706ab6138c1dd46dea2c4f051c400cc668c97eb17093afe3cf7be358006713bb0aae77c7f" +
            "b66a77d47a107c42769933f9f76c36624212e6c6328e2c971a7455f8761b45e2e7aecf48ead51099ea8ed26868382c67fb67" +
            "36607ff9394587284e9743a11a3b67a7f14807bea419708a0a4ba717731dc9be3462214401c70c7a97817e36e57d64f8ac79" +
            "141e2cf899ac392524a3d25e76d9e3411e228242d283d8273e6ba79d5f5b470ea770aab2fea593a913055b1b65b6e911ce28" +
            "d84c95eb218bd24c9ae86ddf6a0d1f0458b0f506916ce151c2c543cb2baebb098ebecec5362373a47b1b5792c2343fca70a6" +
            "9d1c5e696954e8fdd405dfa58099f563f1f6c9b34225fb90c4ca27bdba234927c6af1a4f3907d7a4bfae1dd9879f7eb8e536" +
            "1d92e73fb1cdc8980ac325a9b319d37be3e52b165465699e8eb13a4710182f99052fdab9e39b6d56f0d93fc151d7429ae5fc" +
            "4beabc439e28ee9c423f9c778eecb3fab83822ca3f6098357ad2f06684b2f22a7b4b692bf23c765cd58a26f1e06776a380de" +
            "2f2d8b72c685cc8576b426b2e4b5a3847ef193deb83ab6ce2a86c760c79cd96ea45438c189fa609c4c8ffb122e0e2f0f9ac5" +
            "1da35427d213cf5bb2caa1b73e96e5087c87a15c03dcd6e313cc6abe96634edb91e3b6ccba828ad995fa7adbb7ec6f2d6434" +
            "e007c406e0d3be6f2b52c5afa54547a4fe191f32e202fae7b1ed85561715d30672336e7b000b67ad9cfa518fc74347df99a2" +
            "76ef5e47737c09f69224ca140616dea0ef10324185846832a1feb072b19d0777ef20fd5ef6b1adbcd303509a903f54e2bded" +
            "f49a4a63d655888cc9a70ef478d2562dee494012fae5be250e5ec7704770bcdc328546976e3ec218c77f41576d13f8ecdba4" +
            "d64cd2dde412deabfa7475128a25bee815caec16bac6fe3af72a5b42ab28655fc4c51dfb7196d55bdf260c4a7378a6bbd3fa" +
            "8a10b1b94918089d44279209ef84081d88e6ad6614efe4a0a20e575dea153e897100c04e3318795556563dd13a948aeae2e9" +
            "5dc7f590febadf4871f8a6c20d9a3c2fd8d71303485750dda8cd38edb70052a6d6100268c110e9740dc7523bf73a82338831" +
            "5d043ad565e906fbe79cc9bdcb7d27d2342a57fb8ca5d34617a4ac38ec1e20b66e3fdbed6f31adeaaf182f14d24f803acf11" +
            "5bbb4e5240437336cafbfee0f4c0c6756800b6b9232d7f31924c699d5e436ec0dc93a8c7331ba6d03ace29787a9925e77adf" +
            "a6ee77b41352f2f69e9f2ccaa77d1b3fd1d0d747a6d89f26dba893fc5a165856c7f8b47773b6cf7705ec52b3785e24cf17a3" +
            "cfae67ac071f669a7363e83a4aab842b9cccb8beb1381ca9742ec9e4cfc3872f3b813696da1c53b92fce84e7b96f6f26d8a2" +
            "d7941899c6c765bcde22d09b4e86c8dfe19e2a393d08b283a97110d66a2f130767c3d2b28401e2175a833c808f976196fc8b" +
            "f03cbddd285b88312ed21a40d44664e26d5d712bb98caa3c33730d9ba94f089c102d7b364ecd40d3958dfcb6b2e4599b4fc3" +
            "0b659501b5a1e0db6421bbefaa2bcfaf8f7de592936be9ee9332a11a345335d257ddee41263b7f4fc0e8e333a261f424912d" +
            "1f8c04847a7c98ac727c182ecb3be76b79ea62e15981869ad14bea81e3307c428126eaa693258720ccef3bbc3189bd93dd77" +
            "47b1224cd34b8f8dda9fcc99dd076be9b99b2cbfc051756a5f0c3c2cadc1891b27c128bcfb6c42fa6e38aa25efcff1fd5e18" +
            "c523fb2b4773aae68403f664cd19ca0c3f693b5e2fd800c30bddd5e922bf90515f63381053f2a9e2b497e1e8ca6853665aca" +
            "be98b3401f64203ead46203ecbac21c1a96de016a39fb57bc98d0b3d5b72d5218526b47289a78986aced7f5ebae6e93660a6" +
            "f50355a23cca061210af46fd71236980c28fcf562e1c7c156a364ed625d56d8a7eb3f33e1f6b21d01e28f2856d84e2ba580c" +
            "ada9328468830777f85326a354a178e6b8a34ecf365529a281e35e2f71088e38dcdedc041393ec4c91a65f8bd9b74f8e93c3" +
            "8edaa4a590a75621ecc163532e544c1d28127fdaa8918e1c026bfb43fb02852a920122c8eff12493ff4e90849344c6c3bf31" +
            "cccc05798b2bba873b93c9fa9832666448fd8be746131bf6225d5bf17ff58bcb391b6eff4e7809f5582fa90c5a2f1b8927cf" +
            "a235fe96de94befc06667ea20218f7979c8637172bf947ae8de73faa3cc4f1db55669390abcb2bead1099f794e60cc83a772" +
            "4bce52b40335fe28d515eb0944679333ff23c37ffdced19b8ea222575bb04f77950f55dff8d6fb2573ef95b7e8f6137d1022" +
            "dee1c095179b6fc540a89cba783838839f5dcf0fe8ce7131c20169a601459388f3370fbeea126ae86cfdcebd78c705f2f389" +
            "4dccaf9945346f478d4975782c59a8f8d618eadae3635b8d8d86f13e501c7885351c61ede2e06924075b8c272a004966eff9" +
            "b73eecb58fd29644297a2eeba30cdd8f601d210c5c3e060959a9bcf5e776a1234d8529b21dd2f0954927ca43cc7121f41858" +
            "5018e6e030893426544e7549fd507694c946cde2c09254befb03dd9e32b2f206587b532f026d83e5feb1f96193c1291ef9f2" +
            "4bc21ba3c5ebfd359b2b99c5cd8ca14c44a090ac5f1ae464d59d874b49261c496cc91071d757b1f4dca7cd4b8249de1b7444" +
            "ab95a8f9da5a5b77b451533abf8817e955f41b4db77c377ba76b6e537b40dfa1bc6882106a0a761b26ea0c952d355344d176" +
            "bf0f858bf129fd65cc9062d1c9c08f23dade68a83f595656ceacd9108d98aa3fb00eb9b34a3afec9f61bf7bab093974445a6" +
            "49afc2d77b4a94c6b977655e1a1e78ad79fe2cbaecb6392dc353252419be70206e567a4661972b4d27b30e523bab36320eaa" +
            "ba3c8aa24da43e18655c96acbca313f8b9048c6b30eedb25c635015c0f7cc319385ec719cb163bb0e29ca11cfacc83af46c0" +
            "59b7eddeedd68f35eee81a94651907a2940e09f6207678b67240f664afe92e0b084aad994a7b78c8ab64a15cbb80065d544f" +
            "1dad4e16f20f10c744e0f89ab513454c99982746e66f5ec77f0832577b3aa16880fced6ad6b24d8c5088ddf32f637668d187" +
            "855ad20a0e71bf27de19979b8dbcc807d48f038446421dbb5d2817301a6dd131b4fc34e1fa6bcf60f0d9ce91a47e2b95bf4d" +
            "c00ff36f150398dc9ca9af22c15998012b10cc073a9b567ad551edd8ec767632eb78d67fc347b263a0633d24a85a7b079e9e" +
            "1ae3a7027820e6bd2418d07b1e3016abfa02155d9c23471f41a20b6e179518265e4254331015117808646196f4411d0aedf1" +
            "0abe59c2fb3574f221c8a95999fa2cb69c7457168d7c055bcb51b3e88e405a945182fa4283af9084e6892a51b4b9596f161d" +
            "cec2cf94a66efe12bd750fc877d315f98ecd679ac3823d60887c34f79ede0f64e0cc7e1bde5baf640eb93f54a620813105a5" +
            "90e5b39ec66cfa535c8e57952526c5854c5a92bf2527b19ea274256721daa544d83a7780aed863c89f420e0621b2fe2c0415" +
            "f723f732b106e3b9148161a667ad12e2e83ef5a427c4dfbfb76e12517f19d2705b407cdcd18aefb2fa70e68919857db9432f" +
            "d7dee76c2a1313de78e60f6aa6d6a1627aeed190f1cc414a2a56f33490e4847fd034a2be2a0d00afe692ddd6a8dee55932c4" +
            "2107169557bbf45e2f77da912790b988cd972362d47e172c458550356a4c4594b7d7a46ba9a1758098063925f1f0703baa29" +
            "d78553981345e969eaf366709f550515f91a4fdd6c4054a230ad51303f3605ea75057b2c02a73d9617377a0be44a5aada95c" +
            "89adddf6b8bd31d51ea56bfdd280a99ef7249f35b860c387d11483b343b6003ebe871fa7cda47e41f82ab1cb18a71f95f265" +
            "fea86369ec257a1902937e1dccc62fbb3745826faa03c6c48fdb275ed9d9c0f7bad78dc9eb1c0f71b66ec1f2afb66d699ef3" +
            "7e805cf4d860d8cb381c926cdefe2fad4d77cf003d040a285ab46ddb9d8a8e1fb868383e0e091a29bfbd85f8d09bd10e873d" +
            "db5555be8ac35d105f2bb300258388b48a5846d95036d04ec6059e6fcde83d23abbce3d157caeb5f3646c56e8107e0043aea" +
            "5961a0382d90c9d6b0f9d7760b921d0f05b4a19509427fe6410e9caf07177904763eebee0c7911987d154ff0e3b5df36da83" +
            "7de18bf59c49851565f3497e02fc011c2159cbec6ec315e0f05760d3de480001b389e5af921e7cc6717c014920080d18f45c" +
            "f5f1000101fa2ac508c8910584412500010c976668ba7056bc6f15000001612494ee909c4af26a6cb6c73976771a5fce7a1a" +
            "0001001c666e4b97c6d69394d4010169b2e0a1e3aec525e1c00001d3f63abedf5e88f530ec000082b480373debea628f8701" +
            "010008d30d3260fba3500c3b9dad4934fa585fb987940100013c2c5b86fdf94be3972300000198fc9a7e564cb8a23704c482" +
            "7ebd8c2ab6d02d1800010122c0530b32d6853f2148000061700fffd0e5410762320101a1d7ca9a35173e7faa8f000100674b" +
            "9b578b7f24887f89668d9d4b36caf6ca2ca5010001a9deecb6d636a3d061ea0001985d2fdcac27a9c1033600014da6280819" +
            "c9c3eb881f00003ceefe3ec1006ac09a5f0101ce1309c91dd23b118160000138865edd2be524eb5f1c000100c62aa7e46b2f" +
            "69adde195ec62235bbbfd1497189010000e7a1b91859e241c0803e010001f34281d8570ca71b6c6b060e7861a716a42cb860" +
            "000100fba2a29d68abe55752f1010100e09d2e14bf8ce48a8160013da1570843945ab96b01000001fb8bee3d3dfbe6eefa68" +
            "2f341024bcfbcc84bfa5000101094d2c8470875c23d1f0000001a8b9d5c799311e7e91703ff9805c5ece87cf800400010001" +
            "aa3a9eb113d9086dd51d093c2dedfc8aa054b8890001001cd4117cdef56ab1b352010100ca4663561e184146736087b60591" +
            "cfc444918c750100010329770f803df4392ae0000100dddfd099a97de424522712d22d9254c7559b4207010001bb5930b511" +
            "5e93ba57840001265da70d33e15bfdb8dc0000654801e2e36d570fb5b401019eb6fe06d9a9f5e4aa7e00000103e17dd4a5e7" +
            "90fa47d612c4f486bfa023f05bbb0001000165470a9ad4cdd077dad921ac172346183eba78d5000101b8653293591b7fe2ff" +
            "5300010002b63751a8235cfb9e38b2b252effcda19b5e98c010000018762d72c83088cb6916353847850bdf53b7e9ae80001" +
            "000123ce051b93648cc36424ebac7d71cac72ea3f19c0001012e65bb10b0fea95e3fcb00012925ec1ca13e984557f8000001" +
            "e31e96518d498733f2a06d4fd5306d98bcc03674000100a517d27267ab5d4ace63010028229b2cd1115e0ef777010100ca58" +
            "38fac30288403d41d0b3bf02ffe3693828190100016bf29aed8f3b770bc57200010040fdbae21bf2c08c0cf30adda0c6b516" +
            "83bfb8fe0100004980264576812e9461f10101000fcdabe667f60669195fc5ff4a5daef1b918cebd010001368bc069b82076" +
            "23152a000100dab46a82a1552eff649f9ee254df14b743c83b7e01000001bcbc3331ab70da075c1199481e7458f0f918283f" +
            "0001014e83fdd1be23c126f4d5000001378ca7ab8e1813a734a9c378d781ef7d11508358000100801a9b857d94ed23f69001" +
            "0001cb8d849873a47520891748d8896f521cbd31d5c000010100f5eefc51d580debb82d393501a9a5a5c476c525a01000043" +
            "cebb14fe7636f0ce73010100121edaabf78f47bb438ce56618d5309f9a6d022e010000017d4ea8be6371b2a01b783d1094c2" +
            "c28258ed1c28000100b57b2f24c48074f61340010001a5bfaa3b54f415bf15f24444f926579b76a2d65900010001bc2b59e1" +
            "52394f7452c64de0bf46c21e67bd73ea00010104afe6c3546bf4a674c0000156f62071a47a6cf9c5c50001004302607d318c" +
            "7f324f4a80b0346bdd59890848500100000127cf61fea370187af284879ef4d3b201f62dc7c9000101d60087ef7232c9ea0c" +
            "19000047308ae1b15e4d0b25770100017a928172dae3670eb520e3ede7b105986b48890700010142b2c8d308fbe99d918600" +
            "0052b965fcf544c68e160f010100558b02d10a8b0428d7bbd5e0817f84e75f9f65d101000001fd8df7722f4d48d2bc74977c" +
            "fa8425eeb62c0da2000100a423fae29ee2fb9afce101"))
        self.assertEqual(ok, False, "We expect this fiat-shamir proof to be false")

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
        with open("proof_110_five_true.proof", "rb") as in_file:
            proof = in_file.read()
            (ok, reason) = game_110_zk_verify([True] * 5, 4, proof)
            self.assertEqual(ok, True, "Why don't you trust my proof that I know a configuration going to TTTTT in 4 iterations?")
            (ok, reason) = game_110_zk_verify([False] * 5, 4, proof)
            self.assertEqual(ok, False, "Impossible to have a proof proving that the last position is TTTTT and FFFFF at the same time!")
        
if __name__ == '__main__':
    unittest.main()
