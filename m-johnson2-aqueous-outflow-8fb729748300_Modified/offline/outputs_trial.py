# Imports
from offline import solver as md
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
import pandas as pd


# Set defaults for plotting
mpl.rcParams['lines.linewidth'] = 1.0

# Load data for comparisons
# PR Curves
# yan_pr = np.genfromtxt('../ComparisonData/YanPRCorrected.csv', delimiter=',', dtype=md.dt)
# yan_pr_glauc = np.genfromtxt('../ComparisonData/YanGlaucomatousPR.csv', delimiter=',', dtype=md.dt)
# yan_pr_exp = np.array([[10, 4.12, 0.85], [50, 5.46, 1.14]], dtype=md.dt)
# brubaker_pr_pct10 = np.genfromtxt('../ComparisonData/BrubakerPR.csv', delimiter=',', dtype=md.dt)

# Height distributions
# yan_h5 = np.genfromtxt('../ComparisonData/YanHP5.csv', delimiter=',', dtype=md.dt)
# yan_h10 = np.genfromtxt('../ComparisonData/YanHP10.csv', delimiter=',', dtype=md.dt)
#yan_h15 = np.genfromtxt('../ComparisonData/YanHP15.csv', delimiter=',', dtype=md.dt)
#yan_h30 = np.genfromtxt('../ComparisonData/YanHP30.csv', delimiter=',', dtype=md.dt)

# # Pressure distributions
# yan_p10 = np.genfromtxt('../ComparisonData/YanP10.csv', delimiter=',', dtype=md.dt)
# yan_p20 = np.genfromtxt('../ComparisonData/YanP20.csv', delimiter=',', dtype=md.dt)
# yan_p30 = np.genfromtxt('../ComparisonData/YanP30.csv', delimiter=',', dtype=md.dt)
# yan_p50 = np.genfromtxt('../ComparisonData/YanP50.csv', delimiter=',', dtype=md.dt)
# yan_p100 = np.genfromtxt('../ComparisonData/YanP100.csv', delimiter=',', dtype=md.dt)
#
# # Trabeculotomy height distributions
# yan_h7_1h_trab = np.genfromtxt('../ComparisonData/Yan1hP7Height.csv', delimiter=',', dtype=md.dt)
# yan_h7_4h_trab = np.genfromtxt('../ComparisonData/Yan4hP7Height.csv', delimiter=',', dtype=md.dt)
# yan_h25_4h_trab = np.genfromtxt('../ComparisonData/Yan4hP25Height.csv', delimiter=',', dtype=md.dt)
# yan_h25_1h_trab = np.genfromtxt('../ComparisonData/Yan1hP25Height.csv', delimiter=',', dtype=md.dt)
# yan_h25_4h_trab_weak_TM = np.genfromtxt('../ComparisonData/Yan4hP25HeightWeakTM.csv', delimiter=',', dtype=md.dt)

# Trabeculotomy facility changes
yan_f7 = np.array([[0, 0.263], [1, 0.381], [4, 0.543], [12, 0.556]])
yan_f7_exp = np.array([[0, 0.0, 0.0], [1, 0.54, 0.23], [4, 0.99, 0.32], [12, 1.0, 0.0]])
yan_f25 = np.array([[0, 0.215], [1, 0.382], [4, 0.800], [12, 0.833]])
yan_f25_exp = np.array([[0, 0.0, 0.0], [1, 0.19, 0.05], [4, 0.55, 0.07], [12, 1.0, 0.0]])

# YAG holes
# yan_yag_q2_normal = np.genfromtxt('../ComparisonData/YanYAGNormal.csv', delimiter=',', dtype=md.dt)
# yan_yag_q2_glauc = np.genfromtxt('../ComparisonData/YanYAGGlauc.csv', delimiter=',', dtype=md.dt)
#
# # Non-Uniform CCs
# yan_weak_TM_a = np.genfromtxt('../ComparisonData/YanWeakTMA.csv', delimiter=',', dtype=md.dt)
# yan_weak_TM_b = np.genfromtxt('../ComparisonData/YanWeakTMB.csv', delimiter=',', dtype=md.dt)
# yan_weak_TM_uniform = np.genfromtxt('../ComparisonData/YanWeakTMUniform.csv', delimiter=',', dtype=md.dt)
#
# # Yuan et al. iStent
# yuan_p10_1istent = np.genfromtxt('../ComparisonData/Psc1iStent.csv', delimiter=',', dtype=md.dt)
# yuan_jcc10_1istent = np.genfromtxt('../ComparisonData/Jcc1iStent.csv', delimiter=',', dtype=md.dt)
# yuan_p10_2istent = np.genfromtxt('../ComparisonData/Psc2iStents.csv', delimiter=',', dtype=md.dt)
# yuan_jcc10_2istent = np.genfromtxt('../ComparisonData/Jcc2iStents.csv', delimiter=',', dtype=md.dt)
#
# # Yuan et al. Hydrus
# yuan_p10_hydrus8 = np.genfromtxt('../ComparisonData/PscHydrus8.csv', delimiter=',', dtype=md.dt)
# yuan_jcc10_hydrus8 = np.genfromtxt('../ComparisonData/JccHydrus8.csv', delimiter=',', dtype=md.dt)
# yuan_p10_hydrus15 = np.genfromtxt('../ComparisonData/PscHydrus15.csv', delimiter=',', dtype=md.dt)
# yuan_jcc10_hydrus15 = np.genfromtxt('../ComparisonData/JccHydrus15.csv', delimiter=',', dtype=md.dt)


def solve_cp(iop, geometry='ellipse', unconventional=False, variable_rtm=False, variable_h0=False, trabeculotomies=None,
             sinusotomies=None, yag_holes=None, stents=None, ccs=None, guess=None, max_error=1e-4, **kwargs):
    """
    Solves the model in the constant pressure mode.

    Parameters
    ----------
    iop : float
        Intraocular pressure (mmHg).

    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    unconventional : bool, optional
        If true, the unconventional outflow pathway is accounted for in the solution with Qu = 0.28 uL/min.
        If false, unconventional outflow is ignored. Note that the inclusion of unconventional outflow
        affects the values of Rtm.
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
        Each element is the index of a YAG laser hole. Default is [], for no YAG holes.
    stents : array_like of (int, Stent)
        Each element is of the form (start index, stent). Default is None for no stents.
    ccs : array_like of tuples (int, float), optional
        Each element is of the form (index, conductance multiplier), where 'index' is the location
        of a collector channel and the multiplier scales only that collector channel relative to the
        baseline per-channel conductance. Default is [] for a uniform distribution of collector channels.
    guess : array_like of float, optional
        An initial guess for the pressure distribution in Schlemm's canal to be used instead of
        guess_pressure(). If empty or not of length N * M, the guess_pressure() is used. Default is [].
    max_error : float, optional
        The maximum acceptable residual between nonlinear updates of the pressure distribution to arrive
        at a solution. Default is 1e-4.
    **kwargs :
        n (N, # of collector channels), m (M, # of nodes between collector channels), etm (Etm, stiffness
        of trabecular meshwork), rtm (Rtm, trabecular meshwork resistance), ksc (Ks, septae stiffness), hs (septae
        height), beta (stent CC dilation factor), rcc(Rcc, collector channel resistance), pev (Pev, episcleral venous
        pressure), and qu (Qu, unconventional outflow rate) can all be changed using **kwargs.

        Note: While potentially useful to model certain hypothetical scenarios, changing any of these
        values may make the system unstable or inaccurate. The model is especially sensitive to changes
        to Etm, Ksc, and hs, as they affect the intersection point of the two height regimes for
        Schlemm's canal. If one these values is changed, it is most likely necessary to change the
        one or both of the other two values as well to match the altered intersection point.

    Returns
    -------
    dict with keys:
        pressure : ndarray of float
            The Schlemm's canal pressure distribution reached when residual < max_error.
        flowrate : float
            The total flowrate into the system (ul/min).
        resistance : float
            The total flow resistance of the system (mmHg/ul/min).
        facility : float
            The total facility of the system (ul/min/mmHg).
    """

    iop = float(iop)

    pressure = md.solve(iop=iop, mode='constant pressure', geometry=geometry, variable_rtm=variable_rtm,
                        variable_h0=variable_h0, trabeculotomies=trabeculotomies, sinusotomies=sinusotomies,
                        yag_holes=yag_holes, stents=stents, ccs=ccs, guess=guess, max_error=max_error, **kwargs)

    beta = 1.0
    Pev = 0.0
    M = 40
    N = 30
    Qu = 0.0
    if unconventional:
        Qu = 0.28

    # Any keyword arguments relevant for calculating CC flow should be included here
    for kw in kwargs:
        if kw == 'beta' and kwargs[kw] is not None:
            beta = float(kwargs[kw])

        elif kw == 'pev' and kwargs[kw] is not None:
            Pev = float(kwargs[kw])

        elif kw == 'qu' and kwargs[kw] is not None and unconventional:
            Qu = kwargs[kw]

        elif kw == 'm' and kwargs[kw] is not None:
            M = kwargs[kw]

    if ccs is None:
        ccs = np.array([(loc, 1.0) for loc in range(0, len(pressure), M)])

    else:
        N = len(ccs)


    qt = 0.0

    # Any surgical intervention that directly alters the calculation for CC flow must have its own loop that tells the
    # program what nodes are affected and adds any additional flow not accounted for in the CCs. The general format that
    # should be used is any SC flow should be added directly in the loop and then create a boolean vector that runs
    # parallel to the pressure vector to be used in the CCs loop.
    has_stent = np.zeros(len(pressure), dtype='bool_')
    if stents is not None:
        for loc, stent in stents:
            has_stent[range(loc, loc + len(stent))] = True

    no_ow = np.zeros(len(pressure), dtype='bool_')
    if sinusotomies is not None:
        for start, end in sinusotomies:
            qt += np.sum((iop - pressure[start:end + 1]) * md.Rtm[start:end + 1])
            qt += (pressure[start - 1] - pressure[start]) * md.get_gsc(pressure, start - 1, iop)
            qt += (pressure[end + 1] - pressure[end]) * md.get_gsc(pressure, end, iop)
            no_ow[start:end + 1] = True

    # CC Loop
    cc_flow = np.zeros(len(ccs), dtype=md.dt)
    i = 0
    for loc, g_ratio in ccs:
        # Add to this if statement for each boolean vector
        if not has_stent[int(loc)] and not no_ow[int(loc)]:
            cc_flow[i] = (pressure[int(loc)] - Pev) * g_ratio / (len(ccs) * md.get_rcc(iop))
            qt += cc_flow[i]
        elif not no_ow[int(loc)]:
            cc_flow[i] = beta * (pressure[int(loc)] - Pev) * g_ratio / (len(ccs) * md.get_rcc(iop))
            qt += cc_flow[i]

        i += 1

    rt = (iop - Pev) / qt  # Calculate the total resistance of the network
    ct = qt / (iop - Pev)  # Calculate the total facility of the network
    if unconventional:
        rt = 1/(Qu / iop + qt / (iop - Pev))
        ct += Qu / iop
        qt += Qu

    print('\n\n' + geometry.capitalize() + ' Geometry')

    if unconventional:
        print('Unconventional Flowrate = ' + str(Qu) + ' ul/min')

    if trabeculotomies is not None:
        for trab in trabeculotomies:
            print('Trabeculotomy: TM resistors ' + str(trab[0]) + ' through ' + str(trab[1]) + ' removed')

    if yag_holes is not None:
        for hole in yag_holes:
            print('YAG hole at node ' + str(hole))

    if stents is not None:
        for loc, stent in stents:
            print(stent, 'placed at node', str(loc))

    for kw in kwargs:
        print(f"{kw} = {kwargs[kw]}")

    print('Constant Pressure Mode\nIOP = ' + str(iop) + ' mmHg\nQt = ' + str(qt) + ' ul/min\nR = ' + str(rt) +
          ' mmHg/ul/min\nC = ' + str(ct) + ' ul/min/mmHg\n-----------------------------------\n')

    return dict(pressure=pressure, iop=iop, flowrate=qt, resistance=rt, facility=ct, jcc=cc_flow)


def solve_cf(qt, geometry='ellipse', unconventional=False, variable_rtm=False, variable_h0=False, trabeculotomies=None,
             sinusotomies=None, yag_holes=None, stents=None, ccs=None, guess=None, max_error=1e-4, **kwargs):
    """
    Solves the model in constant flow mode.

    Parameters
    ----------
    qt : float
        Total flowrate through the system.

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
        Each element is the index of a YAG laser hole. Default is [], for no YAG holes.
    stents : array_like of (int, Stent)
        Each element is of the form (start index, stent). Default is None for no stents.
    ccs : array_like of tuples (int, float), optional
        Each element is of the form (index, conductance multiplier), where 'index' is the location
        of a collector channel and the multiplier scales only that collector channel relative to the
        baseline per-channel conductance. Default is [] for a uniform distribution of collector channels.
    guess : array_like of float, optional
        An initial guess for the pressure distribution in Schlemm's canal to be used instead of
        guess_pressure(). If empty or not of length N * M, the guess_pressure() is used. Default is [].
    max_error : float, optional
        The maximum acceptable residual between nonlinear updates of the pressure distribution to arrive
        at a solution. Default is 1e-4.
    **kwargs :
        n (N, # of collector channels), m (M, # of nodes between collector channels), etm (Etm, stiffness
        of trabecular meshwork), rtm (Rtm, overall trabecular meshwork resistance), ksc (Ksc, septae
        stiffness), and hs (septae height) can all be changed using **kwargs.

        Note: While potentially useful to model certain hypothetical scenarios, changing any of these
        values may make the system unstable or inaccurate. The model is especially sensitive to changes
        to Etm, Ksc, and hs, as they affect the intersection point of the two height regimes for
        Schlemm's canal. If one these values is changed, it is most likely necessary to change one or
        both of the other two values as well to match the altered intersection point.

    Returns
    -------
    dict with keys:
        pressure : ndarray of float
            The Schlemm's canal pressure distribution reached when residual < max_error.
        iop : float
            Intraocular pressure (mmHg).
        resistance : float
            The total flow resistance of the system (mmHg/ul/min).
        facility : float
            The total facility of the system (ul/min/mmHg).
    """

    qt = float(qt)

    if ccs is None:
        ccs = np.array([(loc, 1.0) for loc in range(0, 1200, 40)])

    beta = 1.0
    Pev = 0.0
    Qu = 0.0
    if unconventional:
        Qu = 0.28

    for kw in kwargs:
        if kw == 'beta' and kwargs[kw] is not None:
            beta = float(kwargs[kw])
            
        elif kw == 'pev' and kwargs[kw] is not None:
            Pev = float(kwargs[kw])

        elif kw == 'qu' and kwargs[kw] is not None and unconventional:
            Qu = float(kwargs[kw])

    pressure = md.solve(qt=qt, mode='constant flow', geometry=geometry, unconventional=unconventional,
                        variable_rtm=variable_rtm, variable_h0=variable_h0, trabeculotomies=trabeculotomies,
                        sinusotomies=sinusotomies, yag_holes=yag_holes, stents=stents, ccs=ccs, guess=guess,
                        max_error=max_error, **kwargs)

    iop = pressure[-1]
    pressure = pressure[:-1]
    rt = (iop - Pev)/qt
    ct = qt/(iop - Pev)
    if unconventional:
        rt = 1/(Qu / iop + qt / (iop - Pev))
        ct += Qu / iop

    # Same rules apply here as the corresponding loop in solve_cp(), however it only affects the CC flow plot, not the
    # facility or total flow calculations, so it is less important.
    has_stent = np.zeros(md.N * md.M, dtype='bool_')
    if stents is not None:
        for loc, stent in stents:
            has_stent[range(loc, loc + len(stent))] = True

    no_ow = np.zeros(md.N * md.M, dtype='bool_')
    if sinusotomies is not None:
        for start, end in sinusotomies:
            no_ow[start:end + 1] = True

    cc_flow = np.zeros(len(ccs), dtype=md.dt)
    i = 0
    for loc, g_ratio in ccs:
        if not has_stent[int(loc)] and not no_ow[int(loc)]:
            cc_flow[i] = (pressure[int(loc)] - Pev) * g_ratio / (len(ccs) * md.get_rcc(iop))
        elif not no_ow[int(loc)]:
            cc_flow[i] = beta * (pressure[int(loc)] - Pev) * g_ratio / (len(ccs) * md.get_rcc(iop))

        i += 1

    print(f'\n{geometry.capitalize()} Geometry')

    if unconventional:
        print(f'Unconventional Flowrate = {str(Qu)} ul/min')

    if trabeculotomies is not None:
        for start, end in trabeculotomies:
            print(f'Trabeculotomy: TM resistors {str(start)} through {str(end)} removed')

    if sinusotomies is not None:
        for start, end in sinusotomies:
            print(f'Sinusotomy: SC resistors {str(start)} through {str(end)} removed')

    if yag_holes is not None:
        for hole in yag_holes:
            print(f'YAG hole at node {str(hole)}')

    if stents is not None:
        for loc, stent in stents:
            print(f'{stent} placed at node {str(loc)}')

    for kw in kwargs:
        print(f'{kw} = {kwargs[kw]}')

    print(f'Constant Flow Mode\nQt = {str(qt)} ul/min\nIOP = {str(iop)} mmHg\nR = {str(rt)} mmHg/ul/min\nC = {str(ct)} '
          f'ul/min/mmHg\n-----------------------------------\n')

    return dict(pressure=pressure, flowrate=qt, iop=iop, resistance=rt, facility=ct, jcc=cc_flow)


def plot_pr_curve(iops=None, show_glaucoma=False, normalized=False, **kwargs):
    """
    Solves the model in constant pressure mode for IOPs from 1 mmHg to 100 mmHg and plots them
    against their respective resistances.

    Gives the same graph as Figure 5.4 in the thesis.

    Parameters
    ----------
    iops : array_like of float
        The set of IOPs to calculate resistance at. If not specified IOPs 1, and then 5 to 100 mmHg will
        be used
    show_glaucoma : bool, optional
        If True, plots and returns the P-R curve for a glaucomatous eye model (Rtm = 7 mmHg) along with
        the normal eye. Default is False.
    normalized : bool, optional
        If True, resistances are normalized by the resistance at IOP = 10 mmHg.
    **kwargs : all parameters that can be changed in solve_cp() can also be changed here.

    Returns
    -------
    resistance_norm : ndarray of float
        The resistance of the normal eye corresponding to each value in iops.
    resistance_glauc : ndarray of float, optional
        The resistance of the glaucomatous eye (Rtm = 7 mmHg) corresponding to each value in iops.
    """

    Pev = 0
    for kw in kwargs:
        if kw == 'pev':
            Pev = kwargs[kw]

    if iops is None:
        iops = list(range(5, 51, 5))
        iops = [1] + iops
        iops = np.array(iops, dtype=md.dt) + Pev
    elif np.any(iops <= 0):
        raise ValueError('All IOPs must be > 0')

    resistance_normal = np.zeros(len(iops), dtype=md.dt)
    p_guess_norm = np.array([], dtype=md.dt)

    if show_glaucoma:
        resistance_glauc = np.zeros(len(iops), dtype=md.dt)
        p_guess_glauc = np.array([], md.dt)

    for i, iop in enumerate(iops):
        # Normal eye
        p_guess_norm = p_guess_norm * iop
        sol_norm = solve_cp(iop=iop, guess=p_guess_norm, **kwargs)
        p_guess_norm = sol_norm['pressure'] / iop
        resistance_normal[i] = sol_norm['resistance']

        # Glaucomatous eye
        if show_glaucoma:
            p_guess_glauc = p_guess_glauc * iop
            sol_glauc = solve_cp(iop=iop, glaucoma=True, guess=p_guess_glauc, **kwargs)
            p_guess_glauc = sol_glauc['pressure'] / iop
            resistance_glauc[i] = sol_glauc['resistance']

    plt.title('P-R Curve')
    plt.xlabel('IOP (mmHg)')
    plt.ylabel(r'Resistance (mmHg/$\mu$l/min)')
    plt.ylim((0, 10))
    plt.xlim((0, 51))
    plt.minorticks_on()

    if normalized:
        resistance_normal = resistance_normal / resistance_normal[2]
        # print(brubaker_pr_pct10)
        # plt.errorbar(brubaker_pr_pct10[:, 0], brubaker_pr_pct10[:, 1], brubaker_pr_pct10[:, 2], fmt='go')
        plt.title('Normalized P-R Curve')
        plt.ylabel(r'Resistance ($R/R_{10}$)')
        plt.ylim((0.9, 2))

    if not show_glaucoma:
        plt.plot(iops, resistance_normal)
        plt.legend(['Model', 'Brubaker'])

        return resistance_normal

    else:

        plt.ylim((0, 20))
        plt.plot(iops, resistance_normal, iops, resistance_glauc)
        plt.legend(['Normal Eye', 'Glaucomatous Eye'], loc=0, fontsize='small', numpoints=1)

        return resistance_normal, resistance_glauc


def plot_pressure_dist(iop=7.0, qt=2.0, geometry='ellipse', mode='constant pressure', plot=True, show_all=True,
                       normalize=False, **kwargs):
    """
    Solves the model and plots the pressure distribution(s).

    Gives a graph similar to Figure 5.6 in the thesis.

    Parameters
    ----------
    iop : float, optional
        The IOP to plot CC outflow. Default is 7.0 mmHg. Only used if mode = 'constant pressure'
    qt : float, optional
        The flowrate to plot CC outflow. Default is 2.0 ul/min. Only used if mode = 'constant
        pressure'

    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    mode : {'constant pressure', 'constant flow'}, optional

        * 'constant pressure' : returns pressure with N * M elements. Calculated based on iop. (default)
        * 'constant flow'     : returns pressure with N * M + 1 elements, the last element being the IOP.
                                Calculated based on qt.

    plot : bool, optional
        If True, plots the pressure distributions (default).
    show_all : bool, optional
        If True, plots all pressures from node 0 to 1199
    normalize : bool, optional
        If True, pressures distributions are divided by their corresponding iop. Useful if comparing
        multiple IOPs. Default is False.
    **kwargs : all parameters that can be changed in solve_cp() or solve_cf() can also be changed here.

    Returns
    -------
    pressures : ndarray of float
        Each element is a pressure distribution.
    """

    Pev = 0.0
    for kw in kwargs:
        if kw == 'pev':
            Pev = kwargs[kw]
    
    if mode == 'constant flow':
        sol = solve_cf(qt, geometry=geometry, **kwargs)

    else:
        sol = solve_cp(iop, geometry=geometry, **kwargs)

    if not show_all:
        sol['pressure'] = sol['pressure'][:md.M + 1]

    x = np.array(range(len(sol['pressure'])), dtype=md.dt) * md.dx / 1000.0

    if plot:
        plt.figure()
        if normalize:
            plt.plot(x, (sol['pressure'] - Pev) / (sol['iop'] - Pev))
            plt.ylabel(r'Normalized Pressure ($\frac{P_{sc}(x)-P_{ev}}/{IOP-P_{EV}}$)')

        else:
            plt.plot(x, sol['pressure'])
            plt.ylabel(r'$P_{sc}(x)$ (mmHg)')

        plt.xlabel(r'$x$ (mm)')
        plt.ylim(ymin=0)
        plt.minorticks_on()

    return sol


def plot_height_dist(iop=7.0, qt=2.0, geometry='ellipse', show_all=True, show_p=True, stents=None, **kwargs):
    """
    Solves the model and plots the canal height distribution.

    Gives a graph similar to Figure 5.6 in the Yan thesis.

    Parameters
    ----------
    iop : float, optional
        The IOP to plot CC outflow. Default is 7.0 mmHg. Only used if mode = 'constant pressure'
    qt : float, optional
        The flowrate to plot CC outflow. Default is 2.0 ul/min. Only used if mode = 'constant
        pressure'

    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    stents : array_like of (int, Stent)
        Each element is of the form (start index, stent). Default is None for no stents.
    **kwargs : all parameters that can be changed in solve_cp() or solve_cf() can also be changed here.

    Returns
    -------
    dict with keys:
        pressures : ndarray of float
            Each element is a pressure distribution.
        heights : ndarray of float
            Each element is a height distribution.
    """

    sol = plot_pressure_dist(iop, qt, geometry=geometry, plot=show_p, show_all=show_all, stents=stents, **kwargs)

    if not show_all:
        sol['pressure'] = sol['pressure'][:md.M + 1]

    heights = np.zeros(len(sol['pressure']))

    for i, p in enumerate(sol['pressure']):
        heights[i] = md.get_h(p, sol['iop'], i)

    if stents is not None:
        for loc, stent in stents:
            heights[loc:(loc + len(stent) + 1)] = stent.h

    x = np.arange(len(sol['pressure']), dtype=md.dt) * md.dx / 1000.0

    if show_p:
        plt.twinx()
        plt.plot([], [], x, heights)
        plt.legend(['Pressure', 'Height'])
        plt.ylim(ymin=0)

    else:
        plt.figure()
        plt.title('Height Distribution in Canal')
        plt.plot(x, heights)

    # plt.plot(yan_h5[:, 0], yan_h5[:, 1], 'C0--', yan_h10[:, 0], yan_h10[:, 1]
    #          , 'C1--', yan_h15[:, 0], yan_h15[:, 1], 'C2--', yan_h30[:, 0],
    #          yan_h30[:, 1], 'C3--')
    plt.ylabel(r'$h_{sc}(x)$ ($\mu m$)')
    if show_all:
        plt.xlim((0.0, 36.0))
    # plt.xlabel(r'Circumferential Canal Coordinate ($x/X_{cc}$)')
    # plt.legend(['Me IOP = 5 mmHg', 'Me IOP = 10 mmHg', 'Me IOP = 15 mmHg', 'Me IOP = 30 mmHg', 'Yan IOP = 5 mmHg',
    #             'Yan IOP = 10 mmHg', 'Yan IOP = 15 mmHg', 'Yan IOP = 30 mmHg'], loc=1, fontsize='small')

    plt.minorticks_on()

    return {'solution': sol, 'heights': heights}


def plot_jcc(iop=7.0, qt=2.0, mode='constant pressure', geometry='ellipse', **kwargs):
    """
    Plots the outflow through each CC.

    Parameters
    ----------
    iop : float, optional
        The IOP to plot CC outflow. Default is 7.0 mmHg. Only used if mode = 'constant pressure'
    qt : float, optional
        The flowrate to plot CC outflow. Default is 2.0 ul/min. Only used if mode = 'constant
        pressure'

    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    mode : {'constant pressure', 'constant flow'}, optional

        * 'constant pressure' : returns pressure with N * M elements. Calculated based on iop. (default)
        * 'constant flow'     : returns pressure with N * M + 1 elements, the last element being the IOP.
                                Calculated based on qt.
    **kwargs : all parameters that can be changed in solve_cp() or solve_cf() can also be changed here.

    Returns
    -------
    sol : dict
        The dict object returned by solve_cp() or solve_cf()
    """

    if mode == 'constant flow':
        sol = solve_cf(qt, geometry=geometry, **kwargs)

    else:
        sol = solve_cp(iop, geometry=geometry, **kwargs)

    xcc = np.array(range(md.N), dtype=md.dt)

    plt.figure()
    plt.plot(xcc, sol['jcc'], '^')
    plt.xlabel(r'Circumferential Canal Coordinate ($x/X_{cc}$)')
    plt.ylabel(r'$J_{CC}(x)$ (${\mu}l$/min)')
    plt.title('Collector Channel Flow')
    plt.xlim((0, 30))
    ymin, ymax = plt.ylim()
    plt.ylim((0, ymax*1.2))

    return sol


def solve_trabeculotomy(iop=7.0, qt=2.0, hours=1, trabeculotomies=None, geometry='ellipse', mode='constant pressure',
                        show_height=True, glaucoma=False, guess=[], **kwargs):
    """
    Solves the model for a given trabeculotomy case. It is not necessary to use this function to model
    trabeculotomies, but it allows you to plot the canal height distribution and also gives the option
    to use a few predefined trabeculotomies.

    Parameters
    ----------
    iop : float, optional
        Intraocular pressure. Only used if mode = 'constant pressure'. Default is 7.0 mmHg.
    qt : float, optional
        Total flowrate through the system. Only used if mode = 'constant flow'. Default is 2.0 (ul/min).
    hours : {1, 4, 12}, optional
        Extent of trabeculotomy measured in clock hours. Default is 1.
    trabeculotomies : array_like of (int, int), optional
        Each element is of the form (start index, end index) representing the start and end of each
        removed section of trabecular meshwork. Default is None, for no trabeculotomies.
    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    mode : {'constant pressure', 'constant flow'}, optional

        * 'constant pressure' : returns pressure with N * M elements. Calculated based on iop. (default)
        * 'constant flow'     : returns pressure with N * M + 1 elements, the last element being the IOP.
                                Calculated based on qt.

    show_height : bool, optional
        If True plots the canal height distribution (default).
    glaucoma : bool, optional
        If rtm is not specified in **kwargs, Rtm is set to 7.0 mmHg/ul/min if True or 2.0 mmHg/ul/min if
        False (default).
    guess : array_like of float, optional
        An initial guess for the pressure distribution in Schlemm's canal to be used instead of
        guess_pressure(). If empty or not of length N * M, the guess_pressure() is used. Default is [].
    **kwargs : all parameters that can be changed in solve_cp() or solve_cf() can also be changed here.

    Returns
    -------
    sol : the dictionary objects returned by solve_cp() and solve_cf()
    """

    if trabeculotomies is not None:
        hours = False
        # yan = False

    elif hours == 0:
        trabeculotomies = None
        # yan = False

    elif hours == 1:
        trabeculotomies = [(550, 650)]
        # yan = np.array([[0, 1], [30, 1]])
        # if iop == 7:
        #     yan = yan_h7_1h_trab
        #
        # elif iop == 25:
        #     yan = yan_h25_1h_trab

    elif hours == 4:
        trabeculotomies = [(100, 200), (400, 500), (700, 800), (1000, 1100)]
        # yan = np.array([[0, 1], [30, 1]])
        # if iop == 7:
        #     yan = yan_h7_4h_trab
        #
        # elif iop == 25:
        #     yan = yan_h25_4h_trab

    elif hours == 12:
        trabeculotomies = [(0, 1199)]
        # yan = np.array([[0, 1], [30, 1]])

    elif hours > 12:
        raise ValueError('Hours must be <= 12')

    if mode == 'constant flow':
        sol = solve_cf(qt, geometry=geometry, glaucoma=glaucoma, trabeculotomies=trabeculotomies, guess=guess,
                       **kwargs)
    else:
        sol = solve_cp(iop, geometry=geometry, glaucoma=glaucoma, trabeculotomies=trabeculotomies, guess=guess, **kwargs
                       )

    if show_height:
        rel_heights = np.array([md.get_h(p, iop) / md.h0 for p in sol['pressure'][:md.N * md.M]])
        x = np.array(range(md.N * md.M), dtype=md.dt) / md.M

        plt.figure()
        plt.plot(x, rel_heights)
        # if np.any(yan):
        #     plt.plot(yan[:, 0], yan[:, 1])
        #     plt.legend(['My Model', 'Yan Model'], loc=0)

        if np.any(hours):
            plt.title('Canal Height Distribution following '+str(hours)+'-hour Trabeculotomy at IOP = '+
                      str(iop)+' mmHg')

        else:
            plt.title('Canal Height Distribution following User Defined Trabeculotomy at IOP = ' + str(iop) + ' mmHg')

        plt.ylabel(r'Normalized Height ($h(x)/h_0$)')
        plt.xlabel(r'Circumferential Canal Coordinate ($x/X_{cc}$)')
        plt.ylim((0, 1))
        plt.xlim((0, 30))
        plt.minorticks_on()

        return sol

    else:
        return sol


def plot_dc_trab(iop=7, **kwargs):
    """
    Plots the normalized facility change as a function of the extent of trabeculotomy measured in clock
    hours.

    Parameters
    ----------
    iop : float, optional
        Intraocular pressure. Only used if mode = 'constant pressure'. Default is 7.0 mmHg.
    **kwargs : all parameters that can be changed in solve_trabeculotomy(), other than trabeculotomies
        and hours, can also be changed here.
    """

    dc = np.zeros(4, dtype=md.dt)
    hours = np.array([0, 1, 4, 12])

    for i, h in enumerate(hours):
        dc[i] = solve_trabeculotomy(iop, hours=h, show_height=False, **kwargs)['facility']

    dc_norm = (dc - dc[0]) / (dc[-1] - dc[0])

    plt.figure()
    plt.plot(hours, dc_norm)
    plt.ylabel(r'$\Delta\overline{C_i}=\frac{C_i-C_0}{C_{12}-C_0}$')
    plt.xlabel('Extent of Trabeculotomy (clock hours)')
    plt.title(f'Normalized Post-Trabeculotomy Facility Change at IOP = {str(iop)} mmHg')
    plt.ylim((0, 1))
    plt.minorticks_on()

    # if iop == 7:
    #     # yan_model = (yan_f7[:, 1] - yan_f7[0, 1]) / (yan_f7[-1, 1] - yan_f7[0, 1])
    #     # yan_exp = yan_f7_exp
    #     # yan = True
    #
    # elif iop == 25:
    #     # yan_model = (yan_f25[:, 1] - yan_f25[0, 1]) / (yan_f25[-1, 1] - yan_f25[0, 1])
    #     yan_exp = yan_f25_exp
    #     yan = True
    #
    # else:
    #     yan = False
    #
    # if yan:
    #     # plt.plot(hours, yan_model, '--')
    #     plt.errorbar(yan_exp[:, 0], yan_exp[:, 1], yan_exp[:, 2], fmt='o')
    #     plt.legend(['My Model', 'Experimental'], loc=0, numpoints=1)


def solve_yag_holes(qt=2.0, iop=7.0, n=1, holes=[], geometry='ellipse', mode='constant flow', glaucoma=False, guess=[],
                    **kwargs):
    """
    Solves the model with a given YAG laser holes case. It is not necessary to use this function to model
    YAG laser holes, but it gives the option to use a few predefined YAG hole cases.

    Parameters
    ----------
    qt : float, optional
        Total flowrate through the system. Only used if mode = 'constant flow'. Default is 2.0 (ul/min).
    iop : float, optional
        Intraocular pressure. Only used if mode = 'constant pressure'. Default is 7.0 mmHg.
    n : int, optional
        Number of equidistant YAG holes. Must be <= 6. Default is 1.
    holes : array_like of int, optional
        Each element is the index of a YAG laser hole. Overrides n if not empty.
    geometry: {'ellipse', 'rectangle'}, optional

        * 'ellipse'   : models Schlemm's canal as an elliptical duct (default)
        * 'rectangle' : models Schlemm's canal as an rectangular duct

    mode : {'constant pressure', 'constant flow'}, optional

        * 'constant pressure' : returns pressure with N * M elements. Calculated based on iop.
        * 'constant flow'     : returns pressure with N * M + 1 elements, the last element being the IOP.
                                Calculated based on qt. (default)

    glaucoma : bool, optional
        If rtm is not specified in **kwargs, Rtm is set to 7.0 mmHg/ul/min if True or 2.0 mmHg/ul/min if
        False (default).
    guess : array_like of float, optional
        An initial guess for the pressure distribution in Schlemm's canal to be used instead of
        guess_pressure(). If empty or not of length N * M, the guess_pressure() is used. Default is [].
    **kwargs : all parameters that can be changed in solve_cp() or solve_cf() can also be changed here.

    Returns
    -------
    sol : the dictionary objects returned by solve_cp() or solve_cf()
    """

    if len(holes) > 0:
        n = None

    elif n == 0:
        holes = None

    elif n == 1:
        holes = [600]

    elif n == 2:
        holes = [300, 900]

    elif n == 3:
        holes = [200, 600, 1000]

    elif n == 4:
        holes = [150, 450, 750, 1050]

    elif n == 5:
        holes = [120, 360, 600, 840, 1080]

    elif n == 6:
        holes = [100, 300, 500, 700, 900, 1100]

    else:
        raise ValueError('Invalid value of n. Use holes parameter for > 6 holes')

    if mode == 'constant pressure':
        return solve_cp(iop, geometry=geometry, glaucoma=glaucoma, yag_holes=holes, guess=guess, **kwargs)
    else:
        return solve_cf(qt, geometry=geometry, glaucoma=glaucoma, yag_holes=holes, guess=guess, **kwargs)


def plot_iop_change_yag(qt=2.0, **kwargs):
    """
    Plots the change in IOP for glaucomatous and normal eyes after up to 6 equidistant YAG holes.

    Parameters
    ----------
    qt : float, optional
        Total flowrate through the system. Only used if mode = 'constant flow'. Default is 2.0 (ul/min).
    **kwargs : all parameters that can be changed in solve_yag_holes(), besides n, holes and mode, can also be
        changed here.
    """

    holes = np.array(range(7))
    iops_norm = np.zeros(len(holes), dtype=md.dt)
    iops_glauc = np.zeros(len(holes), dtype=md.dt)

    for i, n in enumerate(holes):
        iops_norm[i] = solve_yag_holes(qt, n=n, **kwargs)['iop']
        iops_glauc[i] = solve_yag_holes(qt, n=n, glaucoma=True, **kwargs)['iop']

    plt.figure()
    plt.plot(holes, iops_norm, holes, iops_glauc)
    # plt.plot(yan_yag_q2_normal[:, 0], yan_yag_q2_normal[:, 1], 'C0--', yan_yag_q2_glauc[:, 0], yan_yag_q2_glauc[:, 1],
    #          'C1--')
    plt.title('Effect of YAG Holes of IOP')
    plt.ylabel('IOP (mmHg)')
    plt.xlabel('Number of YAG Holes in Meshwork')
    plt.legend(['Normal Eye', 'Glaucomatous Eye'])
    plt.ylim(ymin=0)
    plt.xlim((0, 6))
    plt.minorticks_on()


def solve_nonuniform_cc(iop=7.0, qt=2.0, ccs=None, dist='A', mode='constant pressure', **kwargs):
    """Solves the system for non-uniform CC distributions.

    Parameters
    ----------
    iop : float, optional
        Intraocular pressure. Only used if mode = 'constant pressure'. Default is 7.0 mmHg.
    qt : float, optional
        Total flowrate through the system. Only used if mode = 'constant flow'. Default is 2.0 (ul/min).
    ccs : array_like of tuples (int, float), optional
        Each element is of the form (index, conductance multiplier), where 'index' is the location
        of a collector channel and the multiplier scales only that collector channel relative to the
        baseline per-channel conductance. Overrides dist if not None.
    dist : {'A', 'B', 'uniform'}, optional

        * 'A'       : 5 large CCs with conductance ratios of 10 distributed evenly between 25 small CCs
            with conductance ratios of 1. (default)
        * 'B'       : 5 large CCs concentrated in one area separated by 3Xcc, 2Xcc, 2Xcc, and 3Xcc and
            25 small CCs.
        * 'uniform' : A uniform distribution of equally sized CCs.

    mode : {'constant pressure', 'constant flow'}, optional

        * 'constant pressure' : returns pressure with N * M elements. Calculated based on iop. (default)
        * 'constant flow'     : returns pressure with N * M + 1 elements, the last element being the IOP.
                                Calculated based on qt.
    **kwargs : all parameters that can be changed in solve_cp() or solve_cf() can also be changed here.

    Returns
    -------
    sol : the dictionary objects returned by solve_cp() or solve_cf()
    """

    if ccs is not None:
        ksc = 3.0
        for key in kwargs:
            if key == 'ksc':
                ksc = kwargs[key]

    elif dist == 'A':
        ccs = np.array([(0, 10.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 1.0), (240, 10.0), (280, 1.0),
                        (320, 1.0), (360, 1.0), (400, 1.0), (440, 1.0), (480, 10.0), (520, 1.0), (560, 1.0), (600, 1.0),
                        (640, 1.0), (680, 1.0), (720, 10.0), (760, 1.0), (800, 1.0), (840, 1.0), (880, 1.0), (920, 1.0),
                        (960, 10.0), (1000, 1.0), (1040, 1.0), (1080, 1.0), (1120, 1.0), (1160, 1.0)])

    elif dist == 'B':
        ccs = np.array([(0, 1.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 10.0), (240, 1.0), (280, 1.0),
                        (320, 1.0), (360, 1.0), (400, 10.0), (440, 1.0), (480, 1.0), (520, 10.0), (560, 1.0),
                        (600, 10.0), (640, 1.0), (680, 10.0), (720, 1.0), (760, 1.0), (800, 10.0), (840, 1.0),
                        (880, 1.0), (920, 1.0), (960, 1.0), (1000, 1.0), (1040, 1.0), (1080, 1.0), (1120, 1.0),
                        (1160, 1.0)])

    elif dist == 'uniform':
        ccs = None
        ksc = 3.0

    if mode == 'constant pressure':
        return solve_cp(iop, ccs=ccs, **kwargs)

    else:
        return solve_cf(qt, ccs=ccs, **kwargs)


def plot_pr_curve_nonuniform(normalize=True, **kwargs):
    """
    Solves the model in constant pressure mode for IOPs 10 mmHg to 100 mmHg with CC distributions A
    and B and compares them to the PR curve for a uniform CC distribution.

    Parameters
    ----------
    normalize : bool, optional
        If True, resistances are normalized by the resistance at IOP = 10 mmHg (default).
    **kwargs : all parameters that can be changed in solve_cp(), besides iop and Ksc, can also be
        changed here.
    """

    iops = [10, 20, 30, 50, 70, 100]

    pr_a = np.zeros(len(iops), dtype=md.dt)
    pr_b = np.zeros(len(iops), dtype=md.dt)
    pr_uniform = np.zeros(len(iops), dtype=md.dt)

    for i, iop in enumerate(iops):
        pr_a[i] = solve_nonuniform_cc(iop=iop, dist='A', **kwargs)['resistance']
        pr_b[i] = solve_nonuniform_cc(iop=iop, dist='B', **kwargs)['resistance']
        pr_uniform[i] = solve_nonuniform_cc(iop=iop, dist='uniform', **kwargs)['resistance']

    if normalize:
        pr_a = pr_a / pr_a[0]
        pr_b = pr_b / pr_b[0]
        pr_uniform = pr_uniform / pr_uniform[0]

    plt.figure()
    plt.plot(iops, pr_uniform, iops, pr_a, iops, pr_b)
    plt.title('Normalized P-R Curve of Different CC Distributions')
    plt.xlabel('IOP (mmHg)')
    plt.ylabel(r'Resistance (mmHg/${\mu}l$/min')
    plt.legend(['Uniform', 'A', 'B'])
    plt.ylim(ymin=1)
    plt.xlim((0, 100))
    plt.minorticks_on()


def plot_weak_tm_nonuniform(**kwargs):
    """
    Plots the effect of TM weakening on IOP for CC distributions A and B, compares to a uniform distribution.

    Parameters
    ----------
    **kwargs : all parameters that can be changed in solve_cf(), besides Etm and Ks, can also be changed here.
    """

    etms = [0.0, 3.0, 5.0, 10.0]

    iops_uniform = np.zeros(len(etms), dtype=md.dt)
    iops_a = np.zeros(len(etms), dtype=md.dt)
    iops_b = np.zeros(len(etms), dtype=md.dt)

    for i, etm in enumerate(etms):
        iops_uniform[i] = solve_nonuniform_cc(qt=2.0, dist='uniform', mode='constant flow', etm=etm, **kwargs)['iop']
        iops_a[i] = solve_nonuniform_cc(qt=2.0, dist='A', mode='constant flow', etm=etm, **kwargs)['iop']
        iops_b[i] = solve_nonuniform_cc(qt=2.0, dist='B', mode='constant flow', etm=etm, **kwargs)['iop']

    plt.figure()
    plt.plot(etms, iops_uniform, etms, iops_a, etms, iops_b)
    plt.title('Effect of Meshwork Weakening on IOP')
    plt.xlabel(r'$E_{tm}$ (mmHg)')
    plt.ylabel('IOP (mmHg)')
    plt.legend(['Uniform', 'A', 'B'])
    plt.ylim((0, 20))
    plt.xlim((0, 10))
    plt.minorticks_on()


def generate_rtm_cor(rtms=np.arange(0.1, 25.1, 0.1), corr_name="iop-rtm-correlation", qt=2.0, pev=8.0, **kwargs):
    """
    Generates csv and JSON files containing IOP data as a function of Rtm for the purpose of efficiently determining expected baseline IOP for a given Rtm value and vice versa using linear interpolation between known data points.

    Used in the calc_rtm() function as well as the website.

    :param rtms:optional, array_like.
        List of Rtm values for which to calculate IOP. Default is np.arange(0.1, 25.1, 0.1).
    :param corr_name:optional, string.
        File name for both CSV and JSON files. Do not include a file extension.
    :param qt:optional, float.
        Flowrate for which the correlation is made. Default is 2.0 µL/min.
    :param pev:optional, float.
        Episcleral venous pressure to use for the correlation. Default is 8.0 mmHg.
    :param kwargs:
        Any optional arguments to solve_cf can be supplied here, except for Rtm, which is controlled by this function.
    :return: None
    """

    iops = np.zeros_like(rtms)

    for i, r in enumerate(rtms):
        iops[i] = solve_cf(qt=qt, pev=pev, rtm=r, **kwargs)["iop"]

    iop_min = np.append(pev, iops[:-1])
    iop_max = iops
    rtm_min = np.append(0, rtms[:-1])
    rtm_max = rtms
    slope = (rtm_max - rtm_min) / (iop_max - iop_min)
    df = pd.DataFrame(data={"iop_min":iop_min, "iop_max":iop_max, "rtm_min":rtm_min, "rtm_max":rtm_max, "slope":slope})
    df.to_csv(f"{corr_name}.csv", index=False)
    df.to_json(f"{corr_name}.json", orient='table', index=False)


def calc_rtm(iop, corr_name):
    """
    Calculates the Rtm value necessary to achieve the specified baseline IOP, using the given correlation.
    :param iop: float.
        The desired baseline IOP.
    :param corr_name: string.
        Correlation file to use. Do not include file extension, requires CSV.
    :return: float.
        The Rtm required to achieve the desired baseline IOP.
    """
    rtm_cor = pd.read_csv(f"./{corr_name}.csv")

    over_rows = rtm_cor.loc[rtm_cor.iop_min < iop, :]
    row = over_rows.loc[over_rows.iop_max > iop, :]
    rtm = row.slope * (iop - row.iop_min) + row.rtm_min

    return rtm.values[0]


def lsqf(hs=np.arange(2.5, 3.6, 0.1), Etm=np.arange(10.0, 15.1, 0.5), **kwargs):
    """
    Uses a brute force least squares method to fit the parameters hs and Etm to the Brubaker PR curve. These simulations
    can be time consuming, so it is most efficient to use several iterations in order to zero in on the best hs and Etm
    values.

    Parameters
    ----------
    hs : array_like of float, optional
        The list of values to try for hs.
    Etm : array_like of float, optional
        The list of values to try for Etm.
    **kwargs :
        Any of the additional parameters that can be supplied to solve_cp can also be supplied here, excluding the
        parameters directly involved in the least squares fit, which are Etm, h0, and hs.
    """

    results_df = pd.DataFrame(columns=['hs', 'Etm', 'Ks', 'SE'])
    h0 = 20.0  # h0 should not be made variable in this function

    for h in hs:
        print("Testing septae height of " + str(h) + " um\n-----------------------------------\n")
        for tm in Etm:
            ks = tm * (1 - h / h0)
            r_10 = solve_cp(iop=10, etm=tm, hs=h, **kwargs)["resistance"]

           #  iops = brubaker_pr_pct10[1:, 0]
            # r_norm = np.zeros(iops.shape, dtype=md.dt)

            # for i, p in enumerate(iops):
            #     r = solve_cp(iop=p, etm=tm, hs=h, **kwargs)["resistance"]
            #     r_norm[i] = r / r_10

            # r_norm_brubaker = brubaker_pr_pct10[1:, 1]
            # se = np.sum((r_norm - r_norm_brubaker) ** 2)

            # results_df = results_df.append({"hs": h, "Etm": tm, "Ks": ks, "SE": se}, ignore_index=True)

    results_df.to_csv('../ComparisonData/BrubakerOpt15-50-Corrected.csv')
    print(results_df.iloc[results_df.SE.idxmin()])


if __name__ == '__main__':
    # sol = solve_cf(qt=2.0, variable_h0=True, h0=np.array([20.0 for _ in range(1200)]))
    # ccs = np.array([(0, 1.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 10.0), (240, 1.0), (280, 1.0),
    #                 (320, 1.0), (360, 1.0), (400, 10.0), (440, 1.0), (480, 1.0), (520, 10.0), (560, 1.0),
    #                 (600, 10.0), (640, 1.0), (680, 10.0), (720, 1.0), (760, 1.0), (800, 10.0), (840, 1.0),
    #                 (880, 1.0), (920, 1.0), (960, 1.0), (1000, 1.0), (1040, 1.0), (1080, 1.0), (1120, 1.0),
    #                 (1160, 1.0)])
    # #generate_rtm_cor(ccs=ccs, hs=3.3, etm=17.1)
    # #lsqf(hs=np.arange(2.9, 3.2, 0.1), Etm=np.arange(12.0, 14.1, 0.5))
    # plot_pr_curve(normalized=True, ccs=ccs)
    # plt.show()
    # sol = solve_cp(iop=7)
    #
    # # Rosenquist Simulations
    # iop = 7.0
    # max_error = 1e-4
    #
    # ccs = np.array([(0, 1.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 10.0), (240, 1.0), (280, 1.0),
    #                 (320, 1.0), (360, 1.0), (400, 10.0), (440, 1.0), (480, 1.0), (520, 10.0), (560, 1.0),
    #                 (600, 10.0), (640, 1.0), (680, 10.0), (720, 1.0), (760, 1.0), (800, 10.0), (840, 1.0),
    #                 (880, 1.0), (920, 1.0), (960, 1.0), (1000, 1.0), (1040, 1.0), (1080, 1.0), (1120, 1.0),
    #                 (1160, 1.0)])
    #
    # initial_resistance = solve_cp(iop=iop, unconventional=True, max_error=max_error, hs=3.23, etm=14.0)["resistance"]
    #
    # one_hour_locations = np.arange(0, 1100)
    # four_hour_locations = np.arange(0, 200)
    #
    # n_samples = 100
    # one_hour_results = np.zeros(n_samples)
    # four_hour_results = np.zeros(n_samples)

    # for i in range(n_samples):
    #     one_hour_loc = int(np.random.choice(one_hour_locations))
    #     four_hour_loc = int(np.random.choice(four_hour_locations))
    #     print(f"Sample {i + 1}\n1 Hour: {one_hour_loc}\n4x1 Hour: {four_hour_loc}\n")
    #
    #     one_hour_results[i] = solve_cp(iop=iop, unconventional=True, max_error=max_error, hs=3.23, etm=14.0,
    #                                    trabeculotomies=[(one_hour_loc, 100 + one_hour_loc)])["resistance"]
    #     four_hour_results[i] = solve_cp(iop=iop, unconventional=True, max_error=max_error, hs=3.23, etm=14.0,
    #                                     trabeculotomies=[(four_hour_loc, 100 + four_hour_loc),
    #                                                      (300 + four_hour_loc, 400 + four_hour_loc),
    #                                                      (600 + four_hour_loc, 700 + four_hour_loc),
    #                                                      (900 + four_hour_loc, 1000 + four_hour_loc)])["resistance"]

    # np.savetxt("resistancereduction_iop7_1.csv", one_hour_results, delimiter=",")
    # np.savetxt("resistancereduction_iop7_4.csv", four_hour_results, delimiter=",")
    # one_hour_results = np.genfromtxt("resistancereduction_iop7_1.csv", delimiter=",")
    # four_hour_results = np.genfromtxt("resistancereduction_iop7_4.csv", delimiter=",")
    # print(
    #     f"1 Hour: {100 * (initial_resistance - one_hour_results.mean()) / initial_resistance} +/- {100 * (one_hour_results.std()) / initial_resistance}%\n"
    #     f"4x1 Hour: {100 * (initial_resistance - four_hour_results.mean()) / initial_resistance} +/- {100 * (four_hour_results.std()) / initial_resistance}%")



    # iop = 25.0
    # max_error = 1e-4
    #
    # ccs = np.array([(0, 1.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 10.0), (240, 1.0), (280, 1.0),
    #                 (320, 1.0), (360, 1.0), (400, 10.0), (440, 1.0), (480, 1.0), (520, 10.0), (560, 1.0),
    #                 (600, 10.0), (640, 1.0), (680, 10.0), (720, 1.0), (760, 1.0), (800, 10.0), (840, 1.0),
    #                 (880, 1.0), (920, 1.0), (960, 1.0), (1000, 1.0), (1040, 1.0), (1080, 1.0), (1120, 1.0),
    #                 (1160, 1.0)])
    #
    # initial_resistance = solve_cp(iop=iop, unconventional=True, max_error=max_error, hs=3.23, etm=14.0)["resistance"]
    #
    # one_hour_locations = np.arange(0, 1100)
    # four_hour_locations = np.arange(0, 200)
    #
    # n_samples = 100
    # one_hour_results = np.zeros(n_samples)
    # four_hour_results = np.zeros(n_samples)
    #
    # for i in range(n_samples):
    #     one_hour_loc = int(np.random.choice(one_hour_locations))
    #     four_hour_loc = int(np.random.choice(four_hour_locations))
    #     print(f"Sample {i + 1}\n1 Hour: {one_hour_loc}\n4x1 Hour: {four_hour_loc}\n")
    #
    #     one_hour_results[i] = solve_cp(iop=iop, unconventional=True, max_error=max_error, hs=3.23, etm=14.0, trabeculotomies=[(one_hour_loc, 100 + one_hour_loc)])["resistance"]
    #     four_hour_results[i] = solve_cp(iop=iop, unconventional=True, max_error=max_error, hs=3.23, etm=14.0, trabeculotomies=[(four_hour_loc, 100 + four_hour_loc),
    #                                                                                                         (300 + four_hour_loc, 400 + four_hour_loc),
    #                                                                                                         (600 + four_hour_loc, 700 + four_hour_loc),
    #                                                                                                         (900 + four_hour_loc, 1000 + four_hour_loc)])["resistance"]
    # np.savetxt("resistancereduction_iop25_1.csv", one_hour_results, delimiter=",")
    # np.savetxt("resistancereduction_iop25_4.csv", four_hour_results, delimiter=",")
    # print(f"1 Hour: {100*(initial_resistance - one_hour_results.mean())/initial_resistance} +/- {100*(one_hour_results.std())/initial_resistance}%\n"
    #       f"4x1 Hour: {100*(initial_resistance - four_hour_results.mean())/initial_resistance} +/- {100*(four_hour_results.std())/initial_resistance}%")
    #
    # # Define stents
    # l_dil = 0
    # istent_g1_r1 = md.Stent(name='iStent (R)', length=1000.0, loc_inlet=0.0, w=120.0, hd=60.0, two_way=True, l_before=l_dil, l_after=l_dil)
    # solve_cf(qt=2.0, stents=[(0, istent_g1_r1)], pev=8.0)
    # istent_g1_r2 = md.Stent(name='iStent (R)', length=1000.0, loc_inlet=0.0, w=120.0, hd=60.0, two_way=True, l_before=l_dil, l_after=l_dil)
    istent_inject1 = md.Stent(name='iStent inject', length=145.0, loc_inlet=75.0, w=50.0, hd=50.0, h_after=150,
                              g_inlet=42.15134797, l_after=0, l_before=0)
    # istent_inject2 = md.Stent(name='iStent inject', length=145.0, loc_inlet=75.0, w=50.0, hd=50.0, h_after=150, l_after=0,
    #                           g_inlet=42.15134797, l_before=0)
    #
    # istent_inject_end = md.Stent(name='iStent inject', length=145.0, loc_inlet=75.0, w=50.0, hd=50.0, h_after=150,
    #                                l_after=1, g_inlet=42.15134797, l_before=1)
    # hydrus8 = md.Stent(name='8mm Hydrus Scaffold', length=7200.0, loc_inlet=0.0, w=292.0, n_windows=3, l_window=1100.0,
    #                    h_window=76.5, l_spine=900.0, h_spine=100.0, l_after=l_dil, l_before=0, two_way=False)
    #
    # # Modify Hydrus
    # g = hydrus8.g
    # window = g[31:67]
    # spine = g[1:31]
    # after = g[-l_dil:]
    # gsc_inlet = 1.0e-9 * np.pi * 292.0 * (130.1 ** 3) / (64 * md.u * md.dx)
    # g = np.concatenate((g[:1],
    #                     np.repeat([[gsc_inlet, 'spine']], 37, axis=0),
    #                     spine,
    #                     window,
    #                     spine,
    #                     window,
    #                     spine,
    #                     window,
    #                     spine[:5]), axis=0)
    # hydrus8.set_g(g)
    # hydrus8.h = np.concatenate((np.repeat(130.1, 38),
    #                             np.repeat(100.0, 30),
    #                             np.repeat(76.5, 36),
    #                             np.repeat(100.0, 30),
    #                             np.repeat(76.5, 36),
    #                             np.repeat(100.0, 30),
    #                             np.repeat(76.5, 36),
    #                             np.repeat(100.0, l_dil+5),))

    ccs_even = np.array([(0, 1.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 1.0), (240, 1.0), (280, 1.0),
                    (320, 1.0), (360, 1.0), (400, 1.0), (440, 1.0), (480, 1.0), (520, 1.0), (560, 1.0),
                    (600, 1.0), (640, 1.0), (680, 1.0), (720, 1.0), (760, 1.0), (800, 1.0), (840, 1.0),
                    (880, 1.0), (920, 1.0), (960, 1.0), (1000, 1.0), (1040, 1.0), (1080, 1.0), (1120, 1.0),
                    (1160, 1.0)])

    # ccs_even = np.array([(0, 1.0), (40, 1.0), (80, 4.0), (120, 4.0), (160, 4.0), (200, 4.0), (240, 1.0), (280, 1.0),
    #                 (320, 1.0), (360, 1.0), (400, 10.0), (440, 1.0), (480, 1.0), (520, 10.0), (560, 1.0),
    #                 (600, 10.0), (640, 1.0), (680, 10.0), (720, 1.0), (760, 0.01), (800, 0.01), (840, 0.01),
    #                 (880, 0.01), (920, 0.01), (960, 1.0), (1000, 0.01), (1040, 1.0), (1080, 1.0), (1120, 1.0),
    #                 (1160, 1.0)])

    #
    ccs_mouse = np.array([(1069, 1.0), (1091, 1.0), (1115, 1.0), (1150, 1.0), (1163, 1.0), (1189, 1.0), (3, 1.0), (13, 1.0),
                    (50, 1.0), (116, 1.0), (124, 10.0), (149, 1.0), (189, 1.0), (314, 1.0), (387, 1.0),
                    (411, 1.0), (445, 1.0), (471, 10.0), (496, 1.0), (505, 1.0), (533, 1.0), (555, 1.0),
                    (575, 1.0), (603, 1.0), (639, 1.0), (659, 1.0), (683, 1.0), (713, 1.0), (726, 1.0),
                    (762, 1.0), (798, 1.0), (853, 1.0), (922, 1.0), (947, 1.0)])

    #
    ccs_human = np.array([(1, 1.0), (46, 1.0), (95, 1.0), (170, 1.0), (264, 1.0), (348, 1.0), (374, 1.0), (383, 1.0),
                    (408, 1.0), (486, 1.0), (518, 10.0), (542, 1.0), (636, 1.0), (672, 1.0), (681, 1.0),
                    (709, 1.0), (717, 1.0), (763, 10.0), (779, 1.0), (812, 1.0), (822, 1.0), (830, 1.0),
                    (963, 1.0), (999, 1.0), (1081, 1.0), (1092, 1.0), (1100, 1.0), (1129, 1.0), (1144, 1.0)])
    cases = {
         "No Surgery (8mm Hydrus)": dict(qt=2.0, pev=8.0, rtm=5.42),
         "No Surgery (iStent inject2)": dict(qt=2.0, pev=8.0, rtm=4.83, ccs=ccs_even),
         "No Surgery (iStent inject3)": dict(qt=2.0, pev=8.0, rtm=5.558, ccs=ccs_mouse),
         "No Surgery (iStent inject4)": dict(qt=2.0, pev=8.0, rtm=5.226, ccs=ccs_human),
         "No Surgery (iStent)": dict(qt=2.0, pev=8.0, rtm=6.33),
         "No Surgery (iStent inject)": dict(qt=2.0, pev=8.0, rtm=6.71),
    #     #"No Surgery (8mm Hydrus)": dict(qt=2.0, pev=8.0, ccs=ccs, rtm=calc_rtm(iop=23.1, corr_name="iop-rtm-correlation-cc-distB")),
    #     #"No Surgery (iStent)": dict(qt=2.0, pev=8.0, ccs=ccs, rtm=calc_rtm(iop=25.0, corr_name="iop-rtm-correlation-cc-distB")),
    #     #"No Surgery (iStent inject)": dict(qt=2.0, pev=8.0, ccs=ccs, rtm=calc_rtm(iop=25.2, corr_name="iop-rtm-correlation-cc-distB")),
    #     "No Surgery (8mm Hydrus)": dict(qt=2.0, pev=8.0, rtm=6.52, unconventional=True),
    #     "No Surgery (iStent)": dict(qt=2.0, pev=8.0, rtm=7.49, unconventional=True),
    #     "No Surgery (iStent inject)": dict(qt=2.0, pev=8.0, rtm=7.6, unconventional=True),
        #"No Surgery (Trabectome)": dict(qt=2.0, pev=8.0, ccs=ccs, rtm=calc_rtm(iop=23.6, corr_name="iop-rtm-correlation-cc-distB")),
        #"No Surgery (GATT)": dict(qt=2.0, pev=8.0, ccs=ccs, rtm=calc_rtm(iop=25.6, corr_name="iop-rtm-correlation-cc-distB")),
        "No Surgery (Trabectome)": dict(qt=2.0, pev=8.0, rtm=6.76, unconventional=True),
        "No Surgery (GATT)": dict(qt=2.0, pev=8.0, rtm=7.8, unconventional=True),
        "No Surgery (TRAB360)": dict(qt=2.0, pev=8.0, rtm=6.81, unconventional=True),
        #"No Surgery (TRAB360)": dict(qt=2.0, pev=8.0, ccs=ccs, rtm=calc_rtm(iop=23.7, corr_name="iop-rtm-correlation-cc-distB"))
    }
    # solve_cf(**cases["No Surgery (iStent inject)"])["iop"]
    # solve_cf(**cases["No Surgery (iStent inject2)"])["iop"]
    # solve_cf(**cases["No Surgery (iStent inject3)"])["iop"]
    # solve_cf(**cases["No Surgery (iStent inject4)"])["iop"]
    solve_cf(**cases["No Surgery (iStent)"])["iop"]
    #
    #
    # for c in cases:
    #     print(c)
    #     solutions[c] = solve_cf(**cases[c])
    #
    # solutions["No Surgery (8mm Hydrus)"] = solve_cf(**cases["No Surgery (8mm Hydrus)"])
    # solutions["No Surgery (iStent)"] = solve_cf(**cases["No Surgery (iStent)"])
    # solutions["No Surgery (iStent inject)"] = solve_cf(**cases["No Surgery (iStent inject)"])
    #
    # # # iSent inject by separation
    # inject_seps = np.arange(100, 600)
    # # iop_inject_sep = np.zeros((len(inject_seps), 40), dtype=np.float64)
    # #
    # # for j in range(20):
    # #     for i, sep in enumerate(inject_seps):
    # #         print(f"Separation: {sep/100} clock hours")
    # #         sep = int(sep)
    # #         iop_inject_sep[i, j] = solve_cf(**cases["No Surgery (iStent inject)"], stents=[(400 + j, istent_inject1),
    # #                                                                                     (sep + j + 400, istent_inject1)])["iop"]
    #
    # # np.savetxt("iop_inject_sep.csv", iop_inject_sep[:,:10], delimiter=",")
    # iop_inject_sep = np.genfromtxt("iop_inject_sep.csv", delimiter=",")
    # plt.plot(inject_seps/100, iop_inject_sep[:,:20].mean(axis=1))
    # plt.show()

    #
    inject_pos = np.linspace(0, 1180, 60)
    # iop_inject_pos = np.zeros((len(inject_pos), 10), dtype=np.float64)
    # iop_inject_posmouse = np.zeros((len(inject_pos), 10), dtype=np.float64)
    # iop_inject_poshuman = np.zeros((len(inject_pos), 10), dtype=np.float64)
    # for j in range(10):
    #     for i, sep in enumerate(inject_pos):
    #         print(f"Clockpos: {sep/100} clock hours")
    #         sep = int(sep)
    #         iop_inject_pos[i, j] = solve_cf(**cases["No Surgery (iStent)"], stents=[(sep, istent_inject1)])["iop"]
            # iop_inject_posmouse[i, j] = solve_cf(**cases["No Surgery (iStent inject3)"], stents=[(sep, istent_inject1)])[
            #     "iop"]
            # iop_inject_poshuman[i, j] = solve_cf(**cases["No Surgery (iStent inject4)"], stents=[(sep, istent_inject1)])[
            #     "iop"]

    # np.savetxt("iop_inject_pos_human.csv", iop_inject_poshuman[:, :10], delimiter=",")
    # np.savetxt("iop_inject_pos_mouse.csv", iop_inject_posmouse[:, :10], delimiter=",")
    # np.savetxt("iop_inject_pos.csv", iop_inject_pos[:, :10], delimiter=",")
    # np.savetxt("iop_inject_poseven.csv", iop_inject_pos[:, :10], delimiter=",")
    # # iop_inject_pos = np.genfromtxt("iop_inject_pos2.csv", delimiter=",")
    iop_inject_pos = np.genfromtxt("iop_inject_pos_mouse.csv", delimiter=",")
    kernel_size = 3
    kernel = np.ones(kernel_size) / kernel_size
    iop = iop_inject_pos[:, :10].mean(axis=1)
    iop = np.insert(iop, 0, iop[-1])
    iop = np.append(iop, iop[1])
    data_convolved = np.convolve(iop, kernel, mode='valid')

    print(25-np.mean(data_convolved))
    print(np.max(data_convolved)-np.mean(data_convolved))
    print(np.mean(data_convolved)-np.min(data_convolved))


    plt.plot(inject_pos / 50*360/24, data_convolved)
    plt.xlim(-5,360)
    plt.ylim(10,30)

    plt.axhline(25, color='k')
    plt.axhline(18.04, color='g')

    plt.axvline(x=1069/50*360/24, ymin= 0, ymax= 0.1, color='r')
    plt.axvline(x=1091/50*360/24, ymin= 0, ymax= 0.1, color='r')
    plt.axvline(x=1115/50*360/24, ymin= 0, ymax= 0.1, color='r')
    plt.axvline(x=1163/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1189/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=3/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=13/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=411/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=445/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=471/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=496/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=505/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=533/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=555/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=575/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=603/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=639/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=659/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=683/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=713/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=726/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=762/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=798/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=853/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=922/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=947/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=50/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=116/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=124/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=149/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=189/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=314/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=387/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1150/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.legend(['Uneven Distribution', 'Baseline', 'Even Distribution', 'Collector Channel'])
    plt.xlabel("Degree (Stent Placement)", weight='bold')
    plt.ylabel("IOP (mmHg)", weight='bold')
    plt.show()


    iop_inject_pos = np.genfromtxt("iop_inject_pos_human.csv", delimiter=",")
    kernel_size = 3
    kernel = np.ones(kernel_size) / kernel_size
    iop = iop_inject_pos[:, :10].mean(axis=1)
    iop = np.insert(iop, 0, iop[-1])
    iop = np.append(iop, iop[1])
    data_convolved = np.convolve(iop, kernel, mode='valid')

    plt.xlim(-5,360)
    plt.ylim(10,30)


    plt.plot(inject_pos / 50*360/24, data_convolved)
    plt.axhline(25, color='k')
    plt.axhline(18.04, color='g')
    plt.axvline(x=1/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=46/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=95/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=170/50*360/24,ymin= 0, ymax= 0.1, color='r')
    plt.axvline(x=264/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=348/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=374/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=383/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=408/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=486/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=518/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=542/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=636/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=672/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=681/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=709/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=717/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=763/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=779/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=812/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=822/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=830/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=963/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=999/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1081/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1092/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1100/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1129/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.axvline(x=1144/50*360/24, ymin= 0, ymax= 0.1,color='r')
    plt.legend(['Uneven Distribution', 'Baseline', 'Even Distribution', 'Collector Channel'])
    plt.xlabel("Degree (Stent Placement)", weight='bold')
    plt.ylabel("IOP (mmHg)", weight='bold')
    plt.show()



    iop_inject_pos = np.genfromtxt("iop_inject_poseven.csv", delimiter=",")
    iop = iop_inject_pos[:, :10].mean(axis=1)
    iop = np.insert(iop, 0, iop[-1])
    iop = np.append(iop, iop[1])
    data_convolved = np.convolve(iop, kernel, mode='valid')
    plt.plot(inject_pos / 50 * 360 / 24, data_convolved)
    plt.axvline(x=0 / 50 * 360 / 24, color='r')
    plt.axvline(x=40 / 50 * 360 / 24, color='r')
    plt.axvline(x=80 / 50 * 360 / 24, color='r')
    plt.axvline(x=120 / 50 * 360 / 24, color='r')
    plt.axvline(x=160 / 50 * 360 / 24, color='r')
    plt.axvline(x=200 / 50 * 360 / 24, color='r')
    plt.axvline(x=240 / 50 * 360 / 24, color='r')
    plt.axvline(x=280 / 50 * 360 / 24, color='r')
    plt.axvline(x=320 / 50 * 360 / 24, color='r')
    plt.axvline(x=360 / 50 * 360 / 24, color='r')
    plt.axvline(x=400 / 50 * 360 / 24, color='r')
    plt.axvline(x=440 / 50 * 360 / 24, color='r')
    plt.axvline(x=480 / 50 * 360 / 24, color='r')
    plt.axvline(x=520 / 50 * 360 / 24, color='r')
    plt.axvline(x=560 / 50 * 360 / 24, color='r')
    plt.axvline(x=600 / 50 * 360 / 24, color='r')
    plt.axvline(x=640 / 50 * 360 / 24, color='r')
    plt.axvline(x=680 / 50 * 360 / 24, color='r')
    plt.axvline(x=720 / 50 * 360 / 24, color='r')
    plt.axvline(x=760 / 50 * 360 / 24, color='r')
    plt.axvline(x=800 / 50 * 360 / 24, color='r')
    plt.axvline(x=840 / 50 * 360 / 24, color='r')
    plt.axvline(x=880 / 50 * 360 / 24, color='r')
    plt.axvline(x=920 / 50 * 360 / 24, color='r')
    plt.axvline(x=960 / 50 * 360 / 24, color='r')
    plt.axvline(x=1000 / 50 * 360 / 24, color='r')
    plt.axvline(x=1040 / 50 * 360 / 24, color='r')
    plt.axvline(x=1080 / 50 * 360 / 24, color='r')
    plt.axvline(x=1120 / 50 * 360 / 24, color='r')
    plt.axvline(x=1160 / 50 * 360 / 24, color='r')
    plt.xlabel("Degree (Stent Placement)")
    plt.ylabel("IOP (mmHg)")
    plt.show()

    #
    # inject_pos = np.linspace(50, 250, 10)
    # iop_1stent = np.zeros((len(inject_pos), 2), dtype=np.float64)
    # iop_2stent = np.zeros((len(inject_pos), 2), dtype=np.float64)
    # iop_3stent = np.zeros((len(inject_pos), 2), dtype=np.float64)
    # iop_4stent = np.zeros((len(inject_pos), 2), dtype=np.float64)
    # for j in range(2):
    #     for i, sep in enumerate(inject_pos):
    #         print(f"Separation: {sep/100} clock hours")
    #         sep = int(sep)
    #         iop_1stent[i, j] = solve_cf(**cases["No Surgery (iStent inject)"], stents=[(sep, istent_inject1)])["iop"]
    #         iop_2stent[i, j] = solve_cf(**cases["No Surgery (iStent inject)"], stents=[(sep, istent_inject1),
    #                                                                                     (sep + 300, istent_inject1)])["iop"]
    #         iop_3stent[i, j] = solve_cf(**cases["No Surgery (iStent inject)"], stents=[(sep, istent_inject1),
    #                                                                                     (sep + 300, istent_inject1),
    #                                                                                    (sep + 600, istent_inject1)])["iop"]
    #         iop_4stent[i, j] = solve_cf(**cases["No Surgery (iStent inject)"], stents=[(sep, istent_inject1),
    #                                                                                     (sep + 300, istent_inject1),
    #                                                                                    (sep + 600, istent_inject1),
    #                                                                                    (sep + 900, istent_inject1)])["iop"]
    # np.savetxt("iop_istent_pos1.csv", iop_1stent, delimiter=",")
    # np.savetxt("iop_istent_pos2.csv", iop_2stent, delimiter=",")
    # np.savetxt("iop_istent_pos3.csv", iop_3stent, delimiter=",")
    # np.savetxt("iop_istent_pos4.csv", iop_4stent, delimiter=",")
    # sep_data = pd.DataFrame({"Separation":inject_seps/100, "IOP":iop_inject_sep[:,:20].mean(axis=1)})
    # sep_data.to_csv("inject_separation.csv")
    #
    # n_samples = 1000
    # # solutions["8mm Hydrus"] = np.zeros(n_samples)
    # # solutions["iStent G1 (R)"] = np.zeros(n_samples)
    # solutions["iStent inject"] = np.zeros(n_samples)
    # # n_injects = 4
    # hydrus_locs = np.arange(1, 1200 - len(hydrus8))
    # # hydrus_iops = st.norm.rvs(loc=23.1, scale=5.08, size=n_samples)
    # istent_locs = np.arange(1 + l_dil, 1200 - len(istent_g1_r1))
    # # istent_iops = st.norm.rvs(loc=25.0, scale=1.1, size=n_samples)
    # inject_sep = 600
    # inject_locs = np.arange(1, 1200 - 2 * len(istent_inject1) - inject_sep)
    # # # inject_iops = st.norm.rvs(loc=25.2, scale=1.4, size=n_samples)
    # # solutions["No Surgery (Trabectome)"] = solve_cf(**cases["No Surgery (Trabectome)"])
    # # solutions["Trabectome"] = np.zeros(n_samples)
    # # trabectome_lens = np.arange(300, 400)
    # # trabectome_locs = np.arange(1, 1200 - 400)
    # # solutions["Hemi-GATT"] = np.zeros(n_samples)
    # # hemigatt_length = 900
    # # hemigatt_locs = np.arange(0, 1200 - hemigatt_length)
    # # solutions["No Surgery (GATT)"] = solve_cf(**cases["No Surgery (GATT)"])
    # # solutions["GATT"] = np.array([solve_cf(**cases["No Surgery (GATT)"], trabeculotomies=[(0, 1199)])["iop"]])
    # # solutions["No Surgery (TRAB360)"] = solve_cf(**cases["No Surgery (TRAB360)"])
    # # solutions["TRAB360"] = np.array([solve_cf(**cases["No Surgery (TRAB360)"], trabeculotomies=[(0, 1199)])["iop"]])
    # sample = 1
    # for i in range(n_samples):
    #     inject_start = int(np.random.choice(inject_locs))
    #     hydrus_start = int(np.random.choice(hydrus_locs))
    #     istent_start = int(np.random.choice(istent_locs))
    #     # hemigatt_start = int(np.random.choice(hemigatt_locs))
    #     # trabectome_length = int(np.random.choice(trabectome_lens))
    #     # trabectome_start = int(np.random.choice(trabectome_locs))
    #     print(f"Sample #{sample}\nHydrus: {hydrus_start}\niStent: {istent_start}\niStent inject: {inject_start}\n")
    #     # print(f"Trabectome\nStart: {trabectome_start}\nLength: {trabectome_length}\n")
    #     # print(f"Sample #{sample}\nHemi-GATT: {hemigatt_start}\n")
    #     # solutions["8mm Hydrus"][i] = solve_cf(**cases["No Surgery (8mm Hydrus)"], stents=[(hydrus_start, hydrus8)])["iop"]
    #     # solutions["iStent G1 (R)"][i] = solve_cf(**cases["No Surgery (iStent)"], stents=[(istent_start, istent_g1_r1)])["iop"]
    #     solutions["iStent inject"][i] = solve_cf(**cases["No Surgery (iStent inject)"], stents=[(inject_start, istent_inject1),
    #                                                                                             (inject_start + inject_sep, istent_inject1)])["iop"]
    #     # solutions["Trabectome"][i] = solve_cf(**cases["No Surgery (Trabectome)"],
    #     #                                       trabeculotomies=[(trabectome_start,trabectome_start + trabectome_length)])["iop"]
    #     #                                                                                         (inject_start + 600, istent_inject1),
    #     #                                                                                         (inject_start + 900, istent_inject1)])["iop"]
    #     # solutions["Hemi-GATT"] = solve_cf(**cases["No Surgery (GATT)"], trabeculotomies=[(hemigatt_start, hemigatt_start + hemigatt_length)])["iop"]
    #     sample += 1
    #
    # iop_red_pred = {
    #     # "8mm Hydrus": [np.mean(solutions["8mm Hydrus"]),
    #     #                np.std(solutions["8mm Hydrus"])],
    #     # "iStent G1 (R)": [np.mean(solutions["iStent G1 (R)"]),
    #     #                   np.std(solutions["iStent G1 (R)"])],
    #     "iStent inject": [np.mean(solutions["iStent inject"]),
    #                       np.std(solutions["iStent inject"])],
    #     # "Trabectome": [np.mean(solutions["Trabectome"]),
    #     #                np.std(solutions["Trabectome"])],
    #     # "GATT": [np.mean(solutions["GATT"]), 0],
    #     # "Hemi-GATT": [(np.mean(solutions["Hemi-GATT"])),
    #     #               np.std(solutions["Hemi-GATT"])],
    #     # "TRAB360": [np.mean(solutions["TRAB360"]), 0]
    # }
    # #
    # iop_red_clinical = {
    #     # "8mm Hydrus": [16.5, 2.4],
    #     # "iStent G1 (R)": [9.4, 3.6],
    #     "iStent inject": [11.6, 4.9],
    #     # "Trabectome": [16.1, 4.0],
    #     # "GATT": [15.7, 6.1],
    #     # "Hemi-GATT": [15.7, 6.1],
    #     # "TRAB360": [16.4, 6.7]
    # }
    #
    # plt.figure("IOP Reduction")
    # pred = 0
    # clinical = 0
    # i = 0
    # for case in iop_red_pred:
    #     plt.bar([i], [iop_red_pred[case][0]], yerr=[iop_red_pred[case][1]], color='C0')
    #     plt.text(i + 0.05, iop_red_pred[case][0] + 1, str(round(iop_red_pred[case][0], 2)) + r"$\pm$" + str(round(iop_red_pred[case][1], 2)) + "%", fontsize='small')
    #     i += 1
    #     plt.bar([i], [iop_red_clinical[case][0]], yerr=[iop_red_clinical[case][1]], color='C1')
    #     plt.text(i + 0.05, iop_red_clinical[case][0] + 1, str(iop_red_clinical[case][0]) + r"$\pm$" + str(iop_red_clinical[case][1]) + "%", fontsize='small')
    #     i += 1
    #
    # plt.title("IOP Reduction")
    # plt.legend([plt.findobj()[3], plt.findobj()[4]], ["Model Prediction", "12 Month Clinical"])
    # # plt.grid(b=True, axis='both', xdata=[0, 1, 2, 3])
    # plt.ylabel(r"$\%{\Delta}IOP=\frac{IOP_{No\ Surgery}-IOP_{Surgery}}{IOP_{No\ Surgery}}$")
    # plt.xticks(np.arange(0.5, 2*(len(iop_red_clinical) - 1) + 0.6, 2), [x for x in iop_red_clinical])
    # # plt.xticks([0.5, 2.5], ["Trabectome", "GATT"])
    # plt.ylim((0, 60))
    # plt.show()
