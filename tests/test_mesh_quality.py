import numpy as np
from scripts.common.fluent_h5_mesh import equiangle_skewness

def test_ideal_triangle_and_square_have_zero_equiangle_skewness():
    tri = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2]])
    square = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    assert abs(equiangle_skewness(tri)) < 1e-14
    assert abs(equiangle_skewness(square)) < 1e-14

def test_distorted_quad_has_positive_skewness():
    quad = np.array([[0.0, 0.0], [2.0, 0.0], [1.2, 1.0], [0.0, 1.0]])
    assert 0.0 < equiangle_skewness(quad) < 1.0
