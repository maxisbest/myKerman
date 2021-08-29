import krpc
import time

import LaunchintoOrbit
import AutoLanding

LaunchintoOrbit.LaunchintoOrbit(200000, 25000, 4, 1)

conn = krpc.connect(name='test_1')
vessel = conn.space_center.active_vessel
ctrl = vessel.control
ap = vessel.auto_pilot
ap.engage()

vel = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'velocity')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

ap.reference_frame = vessel.orbit.body.reference_frame
ap.target_direction = (-vel()[0], -vel()[1], -vel()[2])
ap.wait()

ctrl.throttle = 1.0

atm = vessel.orbit.body.atmosphere_depth

while True:
    time.sleep(0.1)
    ap.target_direction = (-vel()[0], -vel()[1], -vel()[2])
    if periapsis() < atm*0.9:
        ctrl.throttle = 0.0
        break

AutoLanding.AutoLanding(vessel, 'test_1_main_vessel')