import krpc
import time
import sys


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
    Print the strucure of active vessel.
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

    conn.close()


def Launch(sec: int):
    '''
    Launch active vessel after seconds.
    '''
    conn = krpc.connect(name='Launch')
    vessel = conn.space_center.active_vessel
    ctrl = vessel.control
    if not sec:
        sec = 1
    time.sleep(sec)
    printTime('Launch Countdown')
    time.sleep(1)

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


def jettisonFairing(vessel):
    '''
    Jettison all fairings. Something is wrong with part.fairing.jettisoned, it always returns true if revert to launch
    '''

    # jF = vessel.parts.fairings
    # for i in jF:
    #     i.fairing.jettison()
    # printTime(' ' + vessel.name + ' fairings jettisoned')

    for fairing in vessel.parts.fairings:
        for module in fairing.part.modules:
            if 'Fairing' in module.name:
                #Switch here if not a Chinese version KSP
                #module.trigger_event('Deploy')
                module.trigger_event('抛整流罩')


def CoM_adj(vessel):
    '''
    Calculates the center of mass adjustment of the given vessel. Returns a float of distance between the CoM of the vessel and the first engine in part tree.
    '''
    eng = vessel.parts.engines
    box = eng[0].bounding_box(vessel.reference_frame)
    dist = abs(box[0][1])
    return dist