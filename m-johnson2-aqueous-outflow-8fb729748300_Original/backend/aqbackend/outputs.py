# Imports
from aqbackend import solver as md
import numpy as np


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
        Each element is of the form (index, relative conductance ratio), where 'index' is the location
        of a collector channel and relative conductance ratio is the conductance ration relative to the
        other collector channels. Default is [] for a uniform distribution of collector channels.
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

    if ccs is None:
        ccs = np.array([(loc, 1.0) for loc in range(0, md.N * md.M, md.M)])
    else:
        ccs = np.array(ccs)

    qt = 0.0

    # Any surgical intervention that directly alters the calculation for CC flow must have its own loop that tells the
    # program what nodes are affected and adds any additional flow not accounted for in the CCs. The general format that
    # should be used is any SC flow should be added directly in the loop and then create a boolean vector that runs
    # parallel to the pressure vector to be used in the CCs loop.
    has_stent = np.zeros(md.N * md.M, dtype=np.bool)
    if stents is not None:
        for loc, stent in stents:
            has_stent[range(loc, loc + len(stent))] = True

    no_ow = np.zeros(md.N * md.M, dtype=np.bool)
    if sinusotomies is not None:
        for start, end in sinusotomies:
            qt += np.sum((iop - pressure[start:end + 1]) * md.Rtm[start:end + 1])
            qt += (pressure[start - 1] - pressure[start]) * md.get_gsc(pressure, start - 1, iop)
            qt += (pressure[end + 1] - pressure[end]) * md.get_gsc(pressure, end, iop)
            no_ow[start:end + 1] = True

    # CC Loop
    cc_flow = []
    i = 0
    for loc, g_ratio in ccs:
        # Add to this if statement for each boolean vector
        if not has_stent[int(loc)] and not no_ow[int(loc)]:
            cc_flow += [
                {'loc': loc, 'jcc': (pressure[int(loc)] - Pev) * g_ratio / (np.sum(ccs[:, 1]) * md.get_rcc(iop))}]
            qt += (pressure[int(loc)] - Pev) * g_ratio / (np.sum(ccs[:, 1]) * md.get_rcc(iop))
        elif not no_ow[int(loc)]:
            cc_flow += [{'loc': loc,
                         'jcc': beta * (pressure[int(loc)] - Pev) * g_ratio / (np.sum(ccs[:, 1]) * md.get_rcc(iop))}]
            qt += beta * (pressure[int(loc)] - Pev) * g_ratio / (np.sum(ccs[:, 1]) * md.get_rcc(iop))

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

    return dict(pressure=pressure.tolist(), iop=iop, flowrate=qt, resistance=rt, facility=ct, jcc=cc_flow)


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
        Each element is of the form (index, relative conductance ratio), where 'index' is the location
        of a collector channel and relative conductance ratio is the conductance ration relative to the
        other collector channels. Default is [] for a uniform distribution of collector channels.
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
        ccs = np.array([(loc, 1.0) for loc in range(0, md.N * md.M, md.M)])
    else:
        ccs = np.array(ccs)

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
    rt = (iop - Pev) / qt
    ct = qt / (iop - Pev)
    if unconventional:
        rt = 1 / (Qu / iop + qt / (iop - Pev))
        ct += Qu / iop

    # Same rules apply here as the corresponding loop in solve_cp(), however it only affects the CC flow plot, not the
    # facility or total flow calculations, so it is less important.
    has_stent = np.zeros(md.N * md.M, dtype=np.bool)
    if stents is not None:
        for loc, stent in stents:
            has_stent[range(loc, loc + len(stent))] = True

    no_ow = np.zeros(md.N * md.M, dtype=np.bool)
    if sinusotomies is not None:
        for start, end in sinusotomies:
            no_ow[start:end + 1] = True

    cc_flow = []
    i = 0
    for loc, g_ratio in ccs:
        # Add to this if statement for each boolean vector
        if not has_stent[int(loc)] and not no_ow[int(loc)]:
            cc_flow += [{'loc': loc,
                         'jcc': (pressure[int(loc)] - Pev) * g_ratio / (np.sum(ccs[:, 1]) * md.get_rcc(iop))}]
        elif not no_ow[int(loc)]:
            cc_flow += [{'loc': loc,
                         'jcc': beta * (pressure[int(loc)] - Pev) * g_ratio / (np.sum(ccs[:, 1]) * md.get_rcc(iop))}]

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

    return dict(pressure=pressure.tolist(), flowrate=qt, iop=iop, resistance=rt, facility=ct, jcc=cc_flow)


if __name__ == '__main__':
    sol = solve_cp(iop=7)
