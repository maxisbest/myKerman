import krpc
import time
import sys
import math


# conn = krpc.connect(name='')
# vessel = conn.space_center.active_vessel
# ctrl = vessel.control
# ap = vessel.auto_pilot


def printTime(str):
    '''
    Print str to both console and ./missionLog.txt with current time.
    '''
    logFile = open('./missionLog.txt', 'a+', encoding='utf-8')
    logConsole = sys.stdout
    sys.stdout = logFile
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' +str)
    sys.stdout = logConsole
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' +str)


def printStructure():
    '''
    Print the strucure of this vessel.
    '''
    conn = krpc.connect(name='_temp_')
    vessel = conn.space_center.active_vessel
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

    vessel_height = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    print('Height of the vessel \'s center of mass:')
    print('{:.2f}'.format(vessel_height()))

    conn.close()


def Launch(sec):
    '''
    Launch this vessel after seconds.
    '''
    conn = krpc.connect(name='Launch')
    vessel = conn.space_center.active_vessel
    ctrl = vessel.control
    if not sec:
        sec = 1
    time.sleep(sec)
    printTime('Launch Countdown')
    time.sleep(3)

    ctrl.sas = False
    ctrl.rcs = False
    ctrl.throttle = 1.0

    print('3...')
    time.sleep(1)
    print('2...')
    time.sleep(1)
    print('1...')
    time.sleep(1)
    printTime('Launch!')

    vessel.control.activate_next_stage()

    conn.close()

def CoM_adj(vessel):
    '''
    Calculates the center of mass adjustment of the given vessel. Returns a float of distance between the CoM of the vessel and the bottom of stage 0 part.
    '''
    bottom = vessel.parts.in_stage(0)[0]
    box = bottom.bounding_box(vessel.reference_frame)
    dist = abs(box[0][1])
    return dist