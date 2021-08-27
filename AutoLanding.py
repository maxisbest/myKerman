import krpc
import time
import sys
import math

logFile = open('./missionLog.txt', 'a+', encoding='utf-8')
logConsole = sys.stdout

def printTime(str):
    sys.stdout = logFile
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' +str)
    sys.stdout = logConsole
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' +str)

conn = krpc.connect(name='AutoLanding')
vessel = conn.space_center.active_vessel
ctrl = vessel.control
ap = vessel.auto_pilot
ap.reference_frame = vessel.orbit.body.reference_frame

srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
ver_speed = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'vertical_speed')
hor_speed = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'horizontal_speed')
vel = conn.add_stream(getattr,vessel.flight(vessel.orbit.body.reference_frame),'velocity')
g = conn.add_stream(getattr,vessel.orbit.body,'surface_gravity')
alpha = conn.add_stream(getattr, vessel.flight(), 'angle_of_attack')
beta = conn.add_stream(getattr, vessel.flight(), 'sideslip_angle')
drag = conn.add_stream(getattr, vessel.flight(), 'drag')

tgt_h_1 = 12000
tgt_h_2 = 5000
tgt_hor_speed = 10
tolerance_coef = 1.1
vessel_height = srf_altitude() #DO NOT IGNITE BEFORE THIS LINE
hor_mod = 1 #for the cosine

root = vessel.parts.root
stack = [(root, 0)]
experiment_parts = []
printTime('Mission begins')
print('Structure of ' + vessel.name + ':')
while stack:
    part, depth = stack.pop()
    if part.experiment:
        experiment_parts.append(part)
    print(' '*depth, part.title)
    for child in part.children:
        stack.append((child, depth+1))
if experiment_parts == []:
    print('No experiment on this vessel')
else:
    print('Experiment parts on this vessel:')
    for i in experiment_parts:
        print(i.name)
print('Height of the vessel \'s center:')
print(vessel_height)

while True:
    if srf_altitude() < tgt_h_1 and ver_speed() < -1:
        break
    time.sleep(2)

printTime('Initiate auto landing at height of {:.2f} with vertical speed of {:.2f} and horizonal speed of {:.2f}'.format(srf_altitude(), ver_speed(), hor_speed()))

ctrl.sas = False
ctrl.rcs = True
ap.engage()

#First do some horizonal deceleration
while True:
    ap.target_direction = (0, -vel()[1], -vel()[2])
    throttle = (math.sqrt(hor_speed()) - math.sqrt(tgt_hor_speed))/math.sqrt(hor_speed())
    if throttle < 0:
        throttle = 0
    ctrl.throttle = throttle
    if hor_speed() < tgt_hor_speed*tolerance_coef:
        ctrl.throttle = 0
        break
    time.sleep(0.1)

printTime('Horizonal deceleration finished at height of {:.2f} with vertical speed of {:.2f} and horizonal speed of {:.2f}'.format(srf_altitude(), ver_speed(), hor_speed()))

#Find a proper height to start vertical deceleration
while True:
    tgt_h_2 = (ver_speed()**2)*tolerance_coef/(2*vessel.available_thrust/vessel.mass-2*g()) + vessel_height
    ap.target_direction = (-vel()[0], -vel()[1], -vel()[2])
    if srf_altitude() < tgt_h_2:
        break
    time.sleep(0.2)

printTime('Decelerating at height of {:.2f} with vertical speed of {:.2f} and horizonal speed of {:.2f}'.format(srf_altitude(), ver_speed(), hor_speed()))

while True:
    hor_mod = math.cos(math.radians(alpha()))*math.cos(math.radians(beta()))
    ap.target_direction = (-vel()[0], -vel()[1], -vel()[2])
    if ver_speed() > 0:
        throttle = 0
    else:
        #simple physics
        throttle = ((vessel.mass/hor_mod)*(ver_speed()**2/(2*(srf_altitude() - vessel_height)) + g()) - math.sqrt(drag()[0]**2 + drag()[1]**2 + drag()[2]**2))/vessel.available_thrust
    if throttle < 0:
        throttle = 0
    elif throttle > 1:
        throttle = 1
    ctrl.throttle = throttle
    if srf_altitude() < vessel_height + 20:
        ctrl.gear = True
    if srf_altitude() < vessel_height + 0.1:
        ctrl.throttle = 0
        break
    time.sleep(0.01)

printTime('Prepare to land at height of {:.2f} with vertical speed of {:.2f} and horizonal speed of {:.2f}'.format(srf_altitude() - vessel_height, ver_speed(), hor_speed()))

ap.disengage()
printTime('Auto landing completed')