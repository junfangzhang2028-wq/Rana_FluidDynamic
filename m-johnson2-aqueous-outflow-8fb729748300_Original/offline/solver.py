# Imports
import numpy as np
from offline import gauss_seidel as gs
import matplotlib.pyplot as plt
from colorama import Fore, Style
import sys

# Set all constant parameters of the model
dt = np.float64  # The standard data type used will be double precision float
W = 230.0  # Width of SC (um)
u = 9e-8  # Viscosity of aqueous humor (mmHg * min)
Xcc = 1200.0  # Distance between adjacent CCs (um)
dx = 30.0  # Distance between adjacent SC nodes (um)


def get_rcc(iop):
    """
    Calculates overall collector channel resistance.

    Parameters
    ----------
    iop : float
        IOP - Pev (mmHg).

    Returns
    -------
    rcc : float
          Overall collector channel resistance (mmHg/ul/min).
    """

    # Rcc is constant above IOP = 25 mmHg and below IOP = 7 mmHg
    if Rcc > 0.0:
        rcc = Rcc

    elif iop <= 7:
        rcc = 1.8

    elif iop >= 25:
        rcc = 1.2

    else:
        rcc = 2.033 - 0.033 * iop  # 2.033 mmHg/ul/min, 0.033 1/ul/min

    return rcc


def get_h(p, iop, node):
    """
    Calculates the height of Schlemm's canal at a given node.

    Parameters
    ----------
    p : float
        Pressure in Schlemm's canal (mmHg).
    iop : float
        Intraocular pressure (mmHg).
    node : int
        The SC node at which height is being calculated

    Returns
    -------
    h : float
        Canal height (um).
    """

    # Determine pressure difference across the canal wall
    dp = (iop - Pev) - p

    if Etm == 0.0 and dp == 0:
        h = h0[node]

    elif Etm == 0.0:
        h = hs * (Ks[node] / dp) ** (1.0 / 3.0)

    else:
        # Calculate the height of the canal
        if dp < Ks[node]:
            h = h0[node] * (1 - dp / Etm)
        else:
            h = hs * (Ks[node] / dp) ** (1.0 / 3.0)

    if h > h0[node]:
        h = h0[node]

    return h


def get_gsc(p, i, iop, geometry='ellipse'):
    """
    Calculates the conductance of a resistor between the ith and (i+1)th node in Schlemm's canal.

    Parameters
    ----------
    p : array_like of float
        Pressure distribution in Schlemm's canal (mmHg).
    i : int
        Index of the resistor.
    iop : float
        Intraocular pressure (mmHg).
    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    Returns
    -------
    gsc : float
        Conductance of resistor (ul/min/mmHg).
    """

    h1 = get_h(p[i % (N * M)], iop, i % (N * M))

    h2 = get_h(p[(i + 1) % (N * M)], iop, (i + 1) % (N * M))

    if geometry == 'ellipse':
        gsc = 1.0e-9 * np.pi * W * (h1 ** 2) * (h2 ** 2) / (32 * u * dx * (h1 + h2))

    elif geometry == 'rectangle':
        gsc = 1.0e-9 * W * (h1 ** 2) * (h2 ** 2) / (6 * u * dx * (h1 + h2))  # 1e-9 is the conversion factor for
                                                                             # cubic um to ul
    return gsc


def guess_iop(qt):
    """
    Calculates an initial guess for IOP in the constant flow mode.

    Parameters
    ----------
    qt : float
        Total flowrate through the system (ul/min).

    Returns
    -------
    iop : float
        Intraocular pressure (mmHg).
    """

    iop = qt * (get_rcc(7 + Pev) + overall_rtm)

    return iop + Pev


def guess_pressure(iop, qt, mode):
    """
    Calculates an initial pressure estimate.

    Parameters
    ----------
    iop : float
        Intraocular pressure (mmHg).
    qt : float
        Total flowrate through the system (ul/min).
    mode : {'constant pressure', 'constant flow'}

        * 'constant pressure' : returns p_guess with N * M elements, all Schlemm's canal pressures,
                                calculated directly from iop.
        * 'constant flow'     : returns p_guess with N * M + 1 elements, the last element being the IOP
                                guess calculated from qt.

    Returns
    -------
    p_guess : ndarray of float
        Pressure estimates (mmHg).

    """

    if mode == 'constant pressure':
        p_guess = np.repeat(((iop - Pev) / overall_rtm) / (1 / get_rcc(iop) + 1 / overall_rtm), N * M)

    elif mode == 'constant flow':
        iop = guess_iop(qt)
        p_guess = np.repeat(qt * get_rcc(iop) - Pev, N * M)
        p_guess = np.append(p_guess, float(iop - Pev))

    return p_guess


def get_g(p, iop, mode, geometry, trabeculotomies, sinusotomies, yag_holes, stents, ccs):
    """
    Calculates the coefficient matrix of conductances g to solve the system 'gp = q'.

    Parameters
    ----------
    p : array_like of float
        Pressure distribution in Schlemm's canal (mmHg).
    iop : float
        Intraocular pressure (mmHg).
    mode : {'constant pressure', 'constant flow'}

        * 'constant pressure' : returns g with dimensions (N * M, N * M).
        * 'constant flow'     : returns g with dimensions (N * M + 1, N * M + 1).

    geometry: {'ellipse', 'rectangle'}

        * 'ellipse'   : models Schlemm's canal as an elliptical duct.
        * 'rectangle' : models Schlemm's canal as an rectangular duct.

    trabeculotomies : array_like of [int, int]
        Each inner list is of the form [start index, end index] representing the start and end of each
        removed section of trabecular meshwork.
    sinusotomies : array_like of (int, int), optional
        Each element is of the form (start index, end index) representing the start and end of each
        removed section of SC outer wall. Default is None, for no sinusotomies.
    yag_holes : array_like of int
        Each element is the index of a YAG laser hole.
    stents : array_like of (int, Stent)
        Each element is of the form (start index, stent). Default is None for no stents.
    ccs : array_like of tuples (int, float)
        Each element is of the form (index, relative conductance ratio), where 'index' is the location
        of a collector channel and relative conductance ratio is the conductance ratio relative to the
        other collector channels.

    Returns
    -------
    g : ndarray of float
        Coeffecient matrix of conductances (ul/min/mmHg).
    """

    if mode == 'constant pressure':
        g = np.zeros([N * M, N * M], dtype=dt)

    elif mode == 'constant flow':
        g = np.zeros([N * M + 1, N * M + 1], dtype=dt)

    for i in range(N * M):

        gsc2 = get_gsc(p, i, iop, geometry=geometry)
        gsc = get_gsc(p, i - 1, iop, geometry=geometry)
        gcc = 0.0
        g_add = 0.0

        tm_removed = False
        ow_removed = False
        inlet = False
        spine = False
        window = False

        if trabeculotomies is not None:
            for start, end in trabeculotomies:
                if start <= i <= end:
                    tm_removed = True
                    break

                elif i == (start - 1) % (N * M):
                    g_add = gsc2

                elif i == (end + 1) % (N * M):
                    g_add = gsc

        if sinusotomies is not None:
            for start, end in sinusotomies:
                if start <= i <= end:
                    ow_removed = True
                    gsc = 0
                    gsc2 = 0

        if yag_holes is not None:
            for hole in yag_holes:
                if hole - 1 <= i <= hole + 1:
                    tm_removed = True
                    break

                elif i == (hole - 2) % (N * M):
                    g_add = gsc2

                elif i == (hole + 2) % (N * M):
                    g_add = gsc

        if stents is not None:
            for loc, stent in stents:
                if loc < i < loc + len(stent):
                    if stent[i - loc][1] == 'inlet':
                        if stent[i - loc + 1][1] != 'inlet':
                            gsc2 = stent[i - loc + 1][0]

                        else:
                            gsc2 = 0

                        if stent[i - loc - 1][1] != 'inlet':
                            gsc = stent[i - loc - 1][0]
                            if not stent.two_way:
                                gsc = 0

                        else:
                            gsc = 0

                        inlet = True

                    elif stent[i - loc][1] == 'spine':
                        gsc = stent[i - loc][0]
                        if stent[i - loc + 1][1] != 'inlet':
                            gsc2 = stent[i - loc + 1][0]

                        else:
                            if stent.two_way:
                                gsc2 = stent[i - loc][0]
                            else:
                                gsc2 = 0
                            g_add = gsc2

                        if stent[i - loc - 1][1] == 'inlet':
                            g_add = gsc

                        spine = True

                    elif stent[i - loc][1] == 'window':
                        gsc = stent[i - loc][0]
                        if stent[i - loc + 1][1] != 'inlet':
                            gsc2 = stent[i - loc + 1][0]

                        else:
                            if stent.two_way:
                                gsc2 = stent[i - loc][0]
                            else:
                                gsc2 = 0
                            g_add = gsc2

                        window = True

                    break

                elif i == loc:
                    if stent[0][1] == 'inlet' and not stent.two_way:
                        gsc = 0
                        gsc2 = 0
                        inlet = True

                    elif stent[0][1] != 'inlet':
                        gsc2 = stent[0][0]
                        gsc = stent[0][0]
                        if stent[0][1] == 'spine':
                            spine = True

                        else:
                            window = True

                    elif stent[0][1] == 'inlet':
                        inlet = True

                    if stent[1][1] == 'inlet':
                        g_add = gsc2

                    break

                elif i == (loc - 1) % (N * M):
                    if stent[0][1] == 'inlet' and not stent.two_way:
                        gsc2 = 0

                    elif stent[0][1] != 'inlet':
                        gsc2 = stent[0][0]

                    else:
                        g_add = gsc2

                    break

                elif i == (loc + len(stent)) % (N * M):
                    if stent[-1][1] == 'inlet' and not stent.two_way:
                        gsc = 0
                        gsc2 = 0
                        inlet = True

                    elif stent[-1][1] != 'inlet':
                        gsc = stent[-1][0]
                        gsc2 = stent[-1][0]
                        if stent[-1][1] == 'spine':
                            spine = True

                        else:
                            window = True

                    elif stent[-1][1] == 'inlet':
                        inlet = True
                        g_add = gsc2

                    break

                elif i == (loc + len(stent) + 1) % (N * M):
                    if stent[-1][1] == 'inlet' and not stent.two_way:
                        gsc = 0

                    elif stent[-1][1] != 'inlet':
                        gsc = stent[-1][0]

                    else:
                        g_add = gsc

                    break

        for loc, g_ratio in ccs:
            if i == loc:
                if inlet or spine or window:
                    gcc += beta * g_ratio / (np.sum(ccs[:, 1]) * get_rcc(iop))

                elif not ow_removed:
                    gcc += g_ratio / (np.sum(ccs[:, 1]) * get_rcc(iop))

                break

            else:
                gcc = 0

            if ow_removed:
                gcc = 1 / (np.sum(ccs[:, 1]) * get_rcc(iop))

        if mode == 'constant flow':
            if not tm_removed and not ow_removed and not spine and not inlet:
                g[i, -1] = 1 / Rtm[i]
                g[-1, i] = -1 / Rtm[i] - g_add
                g[-1, -1] += 1 / Rtm[i] + g_add

                if i == 0:
                    g[0, -2] = gsc
                    g[-2, 0] = gsc

            elif tm_removed:
                g[-1, -1] += gcc
                g[i, i] = -1.0
                g[i, -1] = 1.0

                if i == 0:
                    g[-2, 0] = gsc

                elif i == N * M - 1:
                    g[-2, 0] = 0

            elif ow_removed:
                g[-1, -1] += 1 / Rtm[i]
                g[i, i] = 1.0
                g[-1, i] = -1 / Rtm[i]
                g[i, -1] = 0

            elif inlet:
                g[i, -1] = -1.0
                if i == 0:
                    g[-2, 0] = gsc

                elif i == N * M - 1:
                    g[-2, 0] = 0

            elif spine:
                g[-1, -1] += g_add
                g[-1, i] = -g_add
                if i == 0:
                    g[0, -2] = gsc
                    g[-2, 0] = gsc

        elif mode == 'constant pressure':
            if not tm_removed and not ow_removed and i == 0:
                g[-1, 0] = gsc
                g[0, -1] = gsc

            elif tm_removed:
                g[i, i] = 1.0
                if i == 0:
                    g[-1, 0] = gsc

                elif i == N * M - 1:
                    g[-1, 0] = 0

            elif ow_removed:
                g[i, i] = 1.0

        for k in range(N * M):
            if not tm_removed and not ow_removed and not spine and not inlet:
                if i == k:
                    g[i, k] = -(1 / Rtm[i] + gsc + gsc2 + gcc)

                elif k == i + 1:
                    g[i, k] = gsc2

                elif k == i - 1:
                    g[i, k] = gsc

                elif k > i + 1:
                    break

            elif spine:
                if i == k:
                    g[i, k] = -(gsc + gsc2 + gcc)

                elif k == i + 1:
                    g[i, k] = gsc2

                elif k == i - 1:
                    g[i, k] = gsc

                elif k > i + 1:
                    break

            elif inlet:
                if i == k:
                    g[i, k] = 1.0

                elif k > i + 1:
                    break

            else:
                break

    return g


def solve(iop=7.0, qt=2.0, mode='constant pressure', geometry='ellipse', unconventional=False, variable_rtm=False,
          variable_h0=False, trabeculotomies=None, sinusotomies=None, yag_holes=None, stents=None, ccs=None, guess=None,
          max_error=1e-4, plot_qsc=False, max_iter=200, **kwargs):
    """
    Solves the nonlinear system 'gp = q' iteratively for the pressure distribution in Schlemm's canal p.

    The coefficient matrix of conductances g is updated with each new linear solution of p.

    Parameters
    ----------
    iop : float, optional
        Intraocular pressure. Only used if mode = 'constant pressure'. Default is 7.0 mmHg.
    qt : float, optional
        Total flowrate through the system. Only used if mode = 'constant flow'. Default is 2.0 (ul/min).
    mode : {'constant pressure', 'constant flow'}, optional

        * 'constant pressure' : returns pressure with N * M elements. Calculated based on iop. (default)
        * 'constant flow'     : returns pressure with N * M + 1 elements, the last element being the IOP.
                                Calculated based on qt.

    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    unconventional : bool, optional
        If true, the unconventional outflow pathway is accounted for in the solution with Qu = 0.28 uL/min.
        If false, unconventional outflow is ignored. Note that the inclusion of unconventional outflow
        affects the value of Rtm.
    variable_rtm : bool, optional
        If true, rtm is taken as an array containing the resistance of each of the N*M TM resistors.
        If false, rtm is taken as a scalar indicating the overall resistance of the TM.
    variable_h0 : bool, optional
        If true, h0 is taken as an array containing the undeformed canal height at each node in SC.
        If false, h0 is taken as a scalar indicating the undeformed canal height at all nodes in SC.
    trabeculotomies : array_like of (int, int), optional
        Each element is of the form (start index, end index) representing the start and end of each
        removed section of trabecular meshwork. Default is None, for no trabeculotomies.
    sinusotomies : array_like of (int, int), optional
        Each element is of the form (start index, end index) representing the start and end of each
        removed section of SC outer wall. Default is None, for no sinusotomies.
    yag_holes : array_like of int, optional
        Each element is the index of a YAG laser hole. Default is None, for no YAG holes.
    stents : array_like of (int, Stent)
        Each element is of the form (start index, stent). Default is None for no stents.
    ccs : array_like of tuples (int, float), optional
        Each element is of the form (index, relative conductance ratio), where 'index' is the location
        of a collector channel and relative conductance ratio is the conductance ration relative to the
        other collector channels. Default is [] for a uniform distribution of collector channels.
    guess : array_like of float, optional
        An initial guess for the pressure distribution in Schlemm's canal to be used instead of
        guess_pressure(). If empty or not of length N * M, the guess_pressure() is used. Default is None.
    max_error : float, optional
        The maximum acceptable residual between nonlinear updates of the pressure distribution to arrive
        at a solution. Default is 1e-4.
    **kwargs :
        n (N, # of collector channels), m (M, # of nodes between collector channels), etm (Etm, stiffness of trabecular
        meshwork), h0 (undeformed canal height, if array_like, must have length N*M), rtm (Rtm, trabecular meshwork
        resistance, if array_like, must have length N*M), ksc (Ks, pressure at which septae support canal), and hs
        (septae height) can all be changed using **kwargs.

        Note: While potentially useful to model certain hypothetical scenarios, changing any of these
        values may make the system unstable or inaccurate. The model is especially sensitive to changes
        to Etm, Ks, and hs, as they affect the intersection point of the two height regimes for
        Schlemm's canal. If one these values is changed, it is most likely necessary to change one or
        both of the other two values as well to match the altered intersection point.

    Returns
    -------
    pressure : ndarray of float
        The Schlemm's canal pressure distribution reached when residual < max_error.
    """

    global N  # Number of CCs
    N = 30
    global M  # Number of nodes between CCs
    M = 40
    global Etm  # Trabecular meshwork stiffness (mmHg)
    Etm = 13.0
    global h0  # Undeformed canal height (um)
    if not variable_h0:
        h0 = np.repeat(20.0, N*M)
    global Rtm  # Overall resistance of TM (mmHg/ul/min)
    if not variable_rtm:
        Rtm = np.repeat(2.0*N*M, N*M)
    global hs  # The canal height at which the septae begin to support the canal (um)
    hs = 3.0
    global beta  # Factor by which to increase flow through CCs in stent regions
    beta = 1.0
    global Rcc  # Overall CC resistance (mmHg/ul/min)
    Rcc = 0
    global Pev  # Episcleral venous pressure (mmHg)
    Pev = 0.0
    global Qu  # Unconventional outflow rate (ul/min)
    if unconventional:
        Qu = 0.28
    else:
        Qu = 0.0

    for kw in kwargs:
        if kw == 'n' and kwargs[kw] is not None:
            N = int(kwargs[kw])

        elif kw == 'm' and kwargs[kw] is not None:
            M = int(kwargs[kw])

        elif kw == 'etm' and kwargs[kw] is not None:
            Etm = float(kwargs[kw])

        elif kw == 'h0' and kwargs[kw] is not None:
            if not variable_h0:
                h0 = np.repeat(float(kwargs[kw]), N*M)
            else:
                h0 = kwargs[kw]

        elif kw == 'rtm' and kwargs[kw] is not None:
            if not variable_rtm:
                Rtm = np.repeat(float(kwargs[kw]) * N * M, N*M)
            else:
                Rtm = kwargs[kw]
        elif kw == 'hs' and kwargs[kw] is not None:
            hs = float(kwargs[kw])

        elif kw == 'beta' and kwargs[kw] is not None:
            beta = float(kwargs[kw])

        elif kw == 'rcc' and kwargs[kw] is not None:
            Rcc = float(kwargs[kw])

        elif kw == 'pev' and kwargs[kw] is not None:
            Pev = float(kwargs[kw])

        elif kw == 'qu' and kwargs[kw] is not None and unconventional:
            Qu = float(kwargs[kw])

        # else:
        #     raise AttributeError(kw, ' is not a valid keyword argument for solve()')
    global dx
    dx = Xcc / M  # The distance between adjacent Schlemm's canal nodes (um)

    global Ks  # Septae stiffness (mmHg)
    Ks = Etm * (1 - hs/h0)

    global overall_rtm
    overall_rtm = 1 / np.sum([1/r for r in Rtm])

    if ccs is None:
        ccs = np.array([(loc, 1.0) for loc in range(0, N * M, M)])

    if mode == 'no sc resistance':
        pressure = (iop / overall_rtm + Pev / get_rcc(iop)) / (1 / get_rcc(iop) + 1 / overall_rtm)

    else:
        residual = max_error + 1
        j = 1
        if guess is None:
            pressure = guess_pressure(iop, qt, mode)

        elif len(guess) != N * M:
            print('Invalid guess. Using guess_pressure() method.')
            pressure = guess_pressure(iop, qt, mode)

        else:
            pressure = np.array(guess)

        if mode == 'constant pressure':
            if iop < Pev:
                raise ValueError('IOP must be greater than episcleral venous pressure')

            q = np.array([-(iop - Pev) / r for r in Rtm])

            if trabeculotomies is not None:
                for start, end in trabeculotomies:
                    q[start:end + 1] = iop - Pev

            if sinusotomies is not None:
                for start, end in sinusotomies:
                    q[start:end + 1] = -Pev

            if yag_holes is not None:
                for hole in yag_holes:
                    q[hole - 1:hole + 2] = iop - Pev

            if stents is not None:
                for loc, stent in stents:
                    q[np.where(stent[:][1] == 'inlet')[0] + loc] = iop - Pev
                    q[np.where(stent[:][1] == 'spine')[0] + loc] = 0.0

        elif mode == 'constant flow':
            if unconventional:
                qt = qt - Qu

            q = np.append(np.zeros([N * M, 1], dtype=dt), qt)
            iop = pressure[-1] + Pev

            if sinusotomies is not None:
                for start, end in sinusotomies:
                    q[start:end + 1] = -Pev

        while residual > max_error and j <= max_iter:

            if j == 31:
                print(Fore.YELLOW+'\n\nSwitching to Gauss-Seidel method\n')

            if mode == 'constant flow':
                iop = pressure[-1] + Pev

            g = get_g(pressure, iop, mode, geometry, trabeculotomies, sinusotomies, yag_holes, stents, ccs)

            if j <= 30:
                new_pressure = np.linalg.solve(g, q)

            else:
                # If the model fails to converge after 30 iterations of numpy's general solver (Intel LAPACK ?gesv
                # routine) switch to Gauss-Seidel method to allow convergence
                new_pressure = gs.solve(g, q, pressure, 10)

            residual = ((np.sum(np.square(new_pressure - pressure)) / len(new_pressure)) ** 0.5) / (iop - Pev)
            pressure = new_pressure
            if residual > max_error:
                sys.stdout.write(Fore.LIGHTBLUE_EX+'\riteration = ' + str(j) + ', residual = ' + str(residual)+Style.RESET_ALL)
            else:
                sys.stdout.write(Fore.GREEN+Style.BRIGHT+'\riteration = ' + str(j) + ', residual = ' + str(residual)+Style.RESET_ALL)
            j += 1

    if plot_qsc:
        x = np.array(list(range(N * M - 1)) + [0])
        y = np.array(list(range(1, N * M)) + [N * M - 1])
        gscs = g[x, y]
        qsc = np.zeros(N * M)
        for i, p in enumerate(pressure[:N * M - 1]):
            qsc[i] = (p - pressure[i + 1]) * gscs[i]

        qsc[-1] = (pressure[N * M - 1] - pressure[0]) * gscs[-1]
        xcc = np.arange(0, len(qsc)) / M
        plt.figure()
        plt.plot(xcc, qsc)
        plt.ylabel(r'Flow Rate (${\mu}l$/min)')
        plt.xlabel(r'Circumferential Canal Coordinate ($x/X_{cc}$)')
        plt.title('Circumferential Flow in SC')

    return pressure + Pev


class Stent:
    """
    A class to model most kinds of stents.

    Attributes
    ----------
    g : ndarray, shape (_length, 2)
        This is the primary functional attribute of the class. The first column contains all of the
        conductances at each node covered by the stent in order. The second column contains the type of
        region that the node is in. There are three possible values for the region:

            * 'inlet': pressure at SC nodes in an inlet region are equal to IOP. Inlets are modeled as
                single node fluid sources with zero flow resistance. If the inlet is the first or last
                index of g and two_way is False, no fluid flows into SC from this end of the stent, all
                flow is directed through the body of the stent.
            * 'spine': SC nodes in a spine region allow only circumferential flow and flow out of CCs.
                Flow from the TM is blocked. These nodes have a fixed conductance, corresponding to their
                fixed width and height.
            * 'window': SC nodes in a window region are treated the same as typical SC nodes, but with
                fixed conductance, corresponding to their fixed width and height.

    loc_inlet : int
        Represents the nodal location of the inlet relative to the leading edge of the stent.
    two_way : bool
        If True fluid is allowed to flow from both sides of the stents inlet. If loc_inlet is not the
        first or last index of g, this attribute has no effect.
    """

    def __init__(self, length=None, loc_inlet=None, w=None, hd=None, g=None, n_windows=0, l_window=None,
                 h_window=None, l_spine=None, h_spine=None, g_inlet=0.0, h_after=None, l_after=0, l_before=0,
                 two_way=False, geometry='ellipse', name='Generic Stent'):
        """
        __init__ method for the Stent class.

        All dimensions are in um, __init__() divides all lengths by dx and converts them into nodal
        lengths.

        Parameters
        ----------
        length : float, optional
            The length in um of the portion of the stent embeded in SC.
        loc_inlet : float, optional
            The distance in um from the leading edge of the stent to the near edge of the inlet.
        w : float, optional
            The width in um of the device in SC.
        hd : float, optional
            The height in um of the device in SC. If there are no windows and g is not specified, hd must
            be specified.
        g : array_like of float, shape (_length, 2)
            Instead of specifying the dimensions of the stent, the conductances and regions may be
            directly specified here. This overrides all other parameters if not None.
        n_windows : int, optional
            The number of window regions of the stent. Default is 0 and hd is used for all of g.
        l_window : float, optional
            The length in um of each the window region.
        h_window : float, optional
            The height in um of the window regions in SC.
        l_spine : float, optional
            The length in um of each spine region.
        h_spine : float, optional
            The height in um of the spine regions in SC.
        g_inlet: float, optional
            The conductance of the inlet in um. In most stents, the inlet is large enough that it presents negligible
            flow resistance, in which case this field can be left blank.
        h_after: float, optional
            The height in um that SC is held to after the end of the stent. In most stents this is equal to the height
            of the canal inside the stent, in which case this field can be left blank.
        l_after: float, optional
            The length of the canal in SC nodes that is dilated past the end of the stent. Default is 150 (1.5 clock
            hours).
        l_before: float, optional
            The length of the canal in SC nodes that is dilated before the start of the stent. Default is 150 (1.5 clock
            hours).
        two_way : bool, optional
            If True fluid is allowed to flow from both sides of the stents inlet. If loc_inlet is not the
            first or last index of g, this attribute has no effect. Default is False
        geometry: {'ellipse', 'rectangle'}, optional

            * 'ellipse'   : models the stent as an elliptical duct (default)
            * 'rectangle' : models the stent canal as an rectangular duct

        name : str, optional
            The name of the stent. Default is 'Generic Stent'.
        """

        if g is not None:
            self._length = len(g) - 1
            self.loc_inlet = np.where(g[:, 1] == 'inlet')[0][0]
            self.g = g
            self.two_way = two_way
            self._name = name

        else:
            self._length = int(length / dx)
            self.loc_inlet = int(loc_inlet / dx)
            self.g = np.repeat([(0.0, '')], self._length + 1, axis=0)
            self.two_way = two_way
            self._name = name
            self.h = np.zeros(self._length + 1, dtype=dt)

            if l_before is None:
                l_before = l_after

            self.g[self.loc_inlet] = (g_inlet, 'inlet')

            if n_windows > 0:
                if l_window is None:
                    raise AttributeError('l_window must be specified if n_windows > 0')

                elif h_window is None:
                    raise AttributeError('h_window must be specified if n_windows > 0')

                elif h_spine is None:
                    raise AttributeError('h_spine must be specified if n_windows > 0')

                elif l_spine is None:
                    raise AttributeError('l_spine must be specified if n_windows > 0')

                if geometry == 'ellipse':
                    g_window = 1.0e-9 * np.pi * w * (h_window ** 3.0) / (64 * u * dx)
                    g_spine = 1.0e-9 * np.pi * w * (h_spine ** 3.0) / (64 * u * dx)

                elif geometry == 'rectangle':
                    g_window = 1.0e-9 * w * (h_window ** 3.0) / (12 * u * dx)
                    g_spine = 1.0e-9 * w * (h_spine ** 3.0) / (12 * u * dx)

                else:
                    raise ValueError('Unsupported geometry: ', geometry)

                self.h[self.loc_inlet] = max(h_window, h_spine)

                window_len = int(l_window / dx)
                spine_len = int(l_spine / dx)
                window = False
                window_count = 0
                tracker = 0
                for i in range(len(self.g)):
                    if self.g[i, 1] == 'inlet':
                        continue

                    elif window and window_count < n_windows:
                        self.g[i] = (g_window, 'window')
                        self.h[i] = h_window
                        tracker += 1
                        if tracker >= window_len:
                            window = False
                            tracker = 0
                            window_count += 1

                    else:
                        self.g[i] = (g_spine, 'spine')
                        self.h[i] = h_spine
                        tracker += 1
                        if tracker >= spine_len:
                            window = True
                            tracker = 0

                if h_after is None:
                    h_after = h_spine

                if geometry == 'ellipse':
                    g_after = 1.0e-9 * np.pi * W * (h_after ** 3.0) / (64 * u * dx)

                elif geometry == 'rectangle':
                    g_after = 1.0e-9 * W * (h_after ** 3.0) / (12 * u * dx)

                self.g = np.append(self.g, np.repeat([[g_after, 'window']], l_after, axis=0), axis=0)
                self.h = np.append(self.h, np.repeat(h_after, l_after))

                self.g = np.append(np.repeat([[g_after, 'window']], l_before, axis=0), self.g, axis=0)
                self.h = np.append(np.repeat(h_after, l_before), self.h)
                self.loc_inlet = self.loc_inlet + l_before

            else:
                if hd is None:
                    raise AttributeError('hd must be specified if n_windows=0')

                if geometry == 'ellipse':
                    g_stent = 1.0e-9 * np.pi * w * (hd ** 3.0) / (64 * u * dx)

                elif geometry == 'rectangle':
                    g_stent = 1.0e-9 * w * (hd ** 3.0) / (12 * u * dx)

                else:
                    raise ValueError('Unsupported geometry: ', geometry)

                self.h[:] = hd
                for i in range(len(self.g)):
                    if self.g[i, 1] == 'inlet':
                        continue

                    else:
                        self.g[i] = (g_stent, 'spine')

                if h_after is None:
                    h_after = hd
                if geometry == 'ellipse':
                    g_after = 1.0e-9 * np.pi * W * (h_after ** 3.0) / (64 * u * dx)

                elif geometry == 'rectangle':
                    g_after = 1.0e-9 * W * (h_after ** 3.0) / (12 * u * dx)

                self.g = np.append(self.g, np.repeat([[g_after, 'window']], l_after, axis=0), axis=0)
                self.h = np.append(self.h, np.repeat(h_after, l_after))

                self.g = np.append(np.repeat([[g_after, 'window']], l_before, axis=0), self.g, axis=0)
                self.h = np.append(np.repeat(h_after, l_before), self.h)
                self.loc_inlet = self.loc_inlet + l_before

        self._length = len(self.g) - 1

    def __str__(self):

        return self._name

    def __iter__(self):

        self.i = 0
        return self

    def __next__(self):

        if self.i > self._length:
            raise StopIteration

        else:
            resistor = float(self.g[self.i, 0]), self.g[self.i, 1]
            self.i += 1

            return resistor

    def __len__(self):

        return self._length

    def __getitem__(self, key):

        if type(key) is not int and type(key) is not slice:
            raise TypeError('index must be either int or slice')

        return self.g[key, 0].astype(np.float), self.g[key, 1]

    def set_g(self, g):

        self.g = g
        self._length = len(g) - 1
        self.loc_inlet = np.where(g[:, 1] == 'inlet')[0][0]
