'''
Automatically launches active vessel into given orbit.
'''
import math
import time
import krpc
import threading

import AutoLanding
from basic import printTime, printStructure, Launch, jettisonFairing


def LaunchintoOrbit(tgt_altitude: float, first_stage_altitude: float, first_stage_dec: int, second_stage_dec: int = 1):
    '''
    Automatically launches active vessel into given orbit. Try using a 3-stage rocket with controlling part on every stage.

    Almost all codes are copied directly from the kRPC Documentation Tutorial: https://krpc.github.io/krpc/tutorials/launch-into-orbit.html

    Parameters:

        tgt_altitude - Target Altitude of the orbit

        first_stage_altitude - altitude for the first decoupling

        first_stage_dec - number of decouplers in the first stage

        second_stage_dec - number of decouplers in the second stage
    '''
    conn = krpc.connect(name='LaunchintoOrbit')
    vessel = conn.space_center.active_vessel
    ctrl = vessel.control
    ap = vessel.auto_pilot

    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    g = conn.add_stream(getattr,vessel.orbit.body,'surface_gravity')

    atm = vessel.orbit.body.atmosphere_depth
    if tgt_altitude < atm:
        tgt_altitude = atm + 1000
    turn_start_altitude = first_stage_altitude
    turn_end_altitude = atm

    printStructure()

    Launch(1)

    turn_angle = 0
    first_stage = False
    while True:

        time.sleep(0.1)
        if not first_stage:
            if srf_altitude() > first_stage_altitude:

                #decouple now
                first_stage = True

                #shut the engine otherwise the decoupled parts will explode
                ctrl.throttle = 0.0
                time.sleep(0.2)
                thread = threading.Thread(target = AutoLanding.DAL(vessel, first_stage_dec))
                thread.start()

                #Uncomment here if needed
                #ctrl.activate_next_stage()
                #eng = vessel.parts.engines
                #eng[-1].active = True

                time.sleep(0.1)
                ctrl.throttle = 0.5
                time.sleep(3)
                ctrl.throttle = 1.0
                ap.engage()

        if srf_altitude() > turn_start_altitude and srf_altitude() < turn_end_altitude:
            frac = ((srf_altitude() - turn_start_altitude) /
                    (turn_end_altitude - turn_start_altitude))
            new_turn_angle = frac * 90
            if abs(new_turn_angle - turn_angle) > 0.5:
                turn_angle = new_turn_angle
                ap.target_pitch_and_heading(90-turn_angle, 90)

        if apoapsis() > tgt_altitude*0.9:
            printTime('Approaching target apoapsis')
            break

    ctrl.throttle = 0.25
    while apoapsis() < tgt_altitude:
        pass

    printTime('Target apoapsis reached')
    jettisonFairing(vessel)
    ctrl.throttle = 0.0

    thread = threading.Thread(target = AutoLanding.DAL(vessel, second_stage_dec))
    thread.start()
    ap.engage()

    ctrl.activate_next_stage()
    time.sleep(0.2)
    printTime('Coasting out of atmosphere')
    while srf_altitude() < atm:
        pass

    printTime('Planning circularization burn')
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu*((2./r) - (1./a1)))
    v2 = math.sqrt(mu*((2./r) - (1./a2)))
    delta_v = v2 - v1
    node = ctrl.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde = delta_v)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse*g()
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v/Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    printTime('Orientating vessel for circularization burn')
    ap.reference_frame = node.reference_frame
    ap.target_direction = (0, 1, 0)
    ap.wait()

    printTime('Waiting until circularization burn')
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
    lead_time = 5
    conn.space_center.warp_to(burn_ut - lead_time)

    printTime('Ready to execute burn')
    time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    while time_to_apoapsis() - (burn_time/2.) > 0:
        pass

    printTime('Executing burn')
    ctrl.throttle = 1.0
    time.sleep(burn_time - 0.1)

    printTime('Fine tuning')
    ctrl.throttle = 0.05
    remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
    while remaining_burn()[1] > 0:
        pass
    ctrl.throttle = 0.0
    node.remove()

    printTime('Launch complete')
