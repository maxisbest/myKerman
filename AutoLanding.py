'''
Automatically lands the active vessel with a tolerance coef.
'''
import krpc
import time
import math
import threading

from basic import printTime, CoM_adj

def AutoLanding(vessel, Name: str, tolerance_coef: float = 1.1):
    '''
    Automatically lands the active vessel with a tolerance coef.

    Parameters:

    vessel - vessel

    Name - enter a name for the connection

    tolerance_coef - tolerance of systemic deviation
    '''
    
    printTime(Name + ' AutoLanding ready. Coefficient of tolerance set to {:.4f}'.format(tolerance_coef))

    conn = krpc.connect(name=Name)
    ctrl = vessel.control
    ap = vessel.auto_pilot
    ap.reference_frame = vessel.orbit.body.reference_frame

    ctrl.sas = False
    ctrl.rcs = False
    ctrl.throttle = 0

    srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    ver_speed = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'vertical_speed')
    hor_speed = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'horizontal_speed')
    vel = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'velocity')
    g = conn.add_stream(getattr,vessel.orbit.body,'surface_gravity')
    alpha = conn.add_stream(getattr, vessel.flight(), 'angle_of_attack')
    beta = conn.add_stream(getattr, vessel.flight(), 'sideslip_angle')
    drag = conn.add_stream(getattr, vessel.flight(), 'drag')

    tgt_h_1 = 20000
    tgt_h_2 = 5000
    hor_mod = 1 #for the cosine

    ap.engage()

    while True:
        ap.target_direction = (0, -vel()[1], -vel()[2])
        if srf_altitude() < tgt_h_1*tolerance_coef and ver_speed() < -1:
            break
        time.sleep(1)

    printTime(Name + ' Initiate auto landing at height of {:.2f} with vertical speed of {:.2f} and horizonal speed of {:.2f}'.format(srf_altitude(), ver_speed(), hor_speed()))

    while True:
        if hor_speed() < 30:
            break
        time.sleep(0.1)
        ap.target_direction = (0, -vel()[1], -vel()[2])
        throttle = (math.sqrt(hor_speed()) - 5)/math.sqrt(hor_speed())
        if throttle > 1:
            throttle = 1
        elif throttle < 0:
            throttle = 0
        ctrl.throttle = throttle

    #Find a proper height to start vertical deceleration
    while True:
        vessel_height = CoM_adj(vessel)
        tgt_h_2 = (ver_speed()**2)*tolerance_coef/(2*vessel.available_thrust/vessel.mass-2*g()) + vessel_height
        ap.target_direction = (-vel()[0], -vel()[1], -vel()[2])
        if srf_altitude() < tgt_h_2:
            break
        time.sleep(0.2)

    printTime(Name + ' Decelerating at height of {:.2f} with vertical speed of {:.2f} and horizonal speed of {:.2f}'.format(srf_altitude(), ver_speed(), hor_speed()))

    while True:
        liq_fuel = vessel.resources.amount('LiquidFuel')
        vessel_height = CoM_adj(vessel)
        hor_mod = math.cos(math.radians(alpha()))*math.cos(math.radians(beta()))
        ap.target_direction = (-vel()[0], -vel()[1], -vel()[2])
        #Uncomment if you need gears
        # if srf_altitude() < vessel_height + 30*tolerance_coef:
        #     ctrl.gear = True
        if srf_altitude() < vessel_height + 0.1/tolerance_coef:
            ctrl.throttle = 0
            break
        if ver_speed() > 0:
            throttle = 0
        elif liq_fuel < 10:
            throttle = 0
            if srf_altitude() > vessel_height + 5*tolerance_coef:
                printTime(Name + ' Insufficient fuel')
                break
        else:
            #simple physics
            throttle = ((vessel.mass/hor_mod)*(ver_speed()**2/(2*(srf_altitude() - vessel_height)) + g()) - math.sqrt(drag()[0]**2 + drag()[1]**2 + drag()[2]**2))/vessel.available_thrust
        if throttle < 0:
            throttle = 0
        elif throttle > 1:
            throttle = 1
        ctrl.throttle = throttle
        time.sleep(0.01)

    ap.disengage()
    printTime(Name + ' Auto landing completed')

    conn.close()
    return


def DAL(vessel, num: int = 1):
    '''
    DECOUPLE & AUTO LANDING: Fire a number of decouplers and automatically lands all decoupled inactive vessels. Current active vessel not included. Auto pilot disengaged. You can start another thread to land this active vessel.

    Parameters:

    vessel - vessel

    num - the number of decouplers to fire (searched in a reversed order on the parts tree)
    '''
    vessel.auto_pilot.disengage()
    dec = vessel.parts.decouplers
    dec = dec[-num:]
    new_vessel = []
    try:
        for i in dec:
            new_vessel.append(i.decouple())
        for i in new_vessel:
            thread = threading.Thread(target=AutoLanding, args=(i, 'decoupled_' + i.name, 1.1))
            thread.start()
    except Exception as e:
        print(e.args)
    return