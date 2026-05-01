import numpy as np


def solve(a, b, x, n):
    """
    Solves the linear system 'ax = b' using the Gauss-Seidel iterative method.

    Parameters
    ----------
    a : array_like of float, shape (M, N)
        The coefficient matrix a of the linear system.
    b : array_like of float, length M
        The left-hand side of the linear system.
    x : array_like of float, length N
        An initial guess for the solution to the linear system.
    n : int
        The number of iterations before returning x.

    Returns
    -------
    x : ndarray, length N
        The solution to the system arrived at after n iterations of Gauss-Seidel
    """

    L = np.tril(a)
    U = a - L

    for i in range(n):
        x = np.dot(np.linalg.inv(L), b - np.dot(U, x))

    return x
