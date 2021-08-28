import krpc
import time
import threading

import AutoLanding

from basic import Launch


conn = krpc.connect(name='test_0')
vessel_0 = conn.space_center.active_vessel
ap = vessel_0.auto_pilot

ctrl = vessel_0.control
Launch(1)

srf_altitude = conn.add_stream(getattr, vessel_0.flight(), 'surface_altitude')
ap.target_pitch_and_heading = (90, 90)
ap.engage()

while True:
    time.sleep(0.5)
    if srf_altitude() > 4000:
        break

ctrl.throttle = 0
ctrl.rcs = False
time.sleep(1)

thread = threading.Thread(target = AutoLanding.DAL(vessel_0, 4))
thread.start()

AutoLanding.AutoLanding(vessel_0, 'Decoupler')