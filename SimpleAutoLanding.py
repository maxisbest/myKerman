import krpc

import AutoLanding

from basic import printStructure

conn = krpc.connect(name='AutoLanding')
vessel = conn.space_center.active_vessel

printStructure()

AutoLanding.AutoLanding(vessel, vessel.name)