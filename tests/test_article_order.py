import unittest
import numpy as np
from hutter_research.article_order import compress, decompress, edge_matrix, cost, swap_descent


class Ordering(unittest.TestCase):
    def test_paid_permutation_reconstructs_exact_article_bytes(self):
        pages = [b"\x00\xffalpha", b"beta\n" * 4, b"", b"gamma" * 10]
        for order in [[0, 1, 2, 3], [3, 0, 2, 1]]:
            self.assertEqual(decompress(compress(pages, order)), pages)

    def test_directed_swaps_never_increase_declared_proxy(self):
        rng = np.random.default_rng(7)
        edge = rng.uniform(0, 100, (16, 16))
        np.fill_diagonal(edge, np.inf)
        order = list(range(16))
        result = swap_descent(edge, order)
        self.assertEqual(sorted(result), order)
        self.assertLessEqual(cost(edge, result), cost(edge, order))


if __name__ == "__main__":
    unittest.main()
