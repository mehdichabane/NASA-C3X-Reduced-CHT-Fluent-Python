import numpy as np
from scripts.common.gradient_reconstruction import reconstruct_gradient

def test_linear_manufactured_field_is_exact():
    xs, ys = np.meshgrid(np.linspace(0, 1, 5), np.linspace(0, 1, 5))
    xy = np.column_stack([xs.ravel(), ys.ravel()])
    ids = np.arange(1, len(xy) + 1)
    adjacency = {int(i): set() for i in ids}
    n = 5
    for j in range(n):
        for i in range(n):
            c = j * n + i + 1
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ii, jj = (i + di, j + dj)
                if 0 <= ii < n and 0 <= jj < n:
                    adjacency[c].add(jj * n + ii + 1)
    values = 3.25 * xy[:, 0] - 1.75 * xy[:, 1] + 8.0
    gradient, *_ = reconstruct_gradient(ids, xy, values, adjacency, minimum_neighbours=6)
    np.testing.assert_allclose(gradient, np.tile([3.25, -1.75], (len(ids), 1)), rtol=0, atol=2e-12)
