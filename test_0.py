import krpc
import time
import threading

import AutoLanding

from basic import printStructure, Launch


conn = krpc.connect(name='test_0')
vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot
ap.reference_frame = vessel.surface_reference_frame

srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')

ctrl = vessel.control

printStructure()
Launch(1)

ap.target_direction = (1, 0, 0)
ap.engage()

while True:
    time.sleep(0.5)
    if srf_altitude() > 4000:
        break

ctrl.throttle = 0
ctrl.rcs = False
time.sleep(1)

thread = threading.Thread(target = AutoLanding.DAL(vessel, 4))
thread.start()

AutoLanding.AutoLanding(vessel, 'Decoupler')

# 2021-08-29 10:48:15 Mission begins
# Structure of test_0:
#  RC-001S远程控制单元
#   高级头锥 - A型
#   FL-T800燃料箱
#    LV-T45“转轮”液体燃料引擎
#    歧管液压分离器
#     FL-T800燃料箱
#      LV-T45“转轮”液体燃料引擎
#      RC-001S远程控制单元
#       高级头锥 - A型
#    歧管液压分离器
#     FL-T800燃料箱
#      LV-T45“转轮”液体燃料引擎
#      RC-001S远程控制单元
#       高级头锥 - A型
#    歧管液压分离器
#     FL-T800燃料箱
#      LV-T45“转轮”液体燃料引擎
#      RC-001S远程控制单元
#       高级头锥 - A型
#    歧管液压分离器
#     FL-T800燃料箱
#      LV-T45“转轮”液体燃料引擎
#      RC-001S远程控制单元
#       高级头锥 - A型
# No experiment on this vessel
# 2021-08-29 10:48:18 Launch Countdown
# 2021-08-29 10:48:22 Launch!
# 2021-08-29 10:48:59 decoupled_test_0 探测器 AutoLanding ready. Coefficient of tolerance set to 1.1000
# 2021-08-29 10:48:59 decoupled_test_0 探测器 AutoLanding ready. Coefficient of tolerance set to 1.1000
# 2021-08-29 10:49:00 decoupled_test_0 探测器 AutoLanding ready. Coefficient of tolerance set to 1.1000
# 2021-08-29 10:49:00 decoupled_test_0 探测器 AutoLanding ready. Coefficient of tolerance set to 1.1000
# 2021-08-29 10:49:00 Decoupler AutoLanding ready. Coefficient of tolerance set to 1.1000
# 2021-08-29 10:49:39 decoupled_test_0 探测器 Initiate auto landing at height of 8233.79 with vertical speed of -11.16 and horizonal speed of 11.15
# 2021-08-29 10:49:39 decoupled_test_0 探测器 Initiate auto landing at height of 8203.25 with vertical speed of -14.51 and horizonal speed of 7.69
# 2021-08-29 10:49:39 decoupled_test_0 探测器 Initiate auto landing at height of 8160.51 with vertical speed of -15.23 and horizonal speed of 8.87
# 2021-08-29 10:49:39 decoupled_test_0 探测器 Initiate auto landing at height of 8337.32 with vertical speed of -8.35 and horizonal speed of 13.59
# 2021-08-29 10:49:41 Decoupler Initiate auto landing at height of 8905.93 with vertical speed of -2.49 and horizonal speed of 19.09
# 2021-08-29 10:50:39 decoupled_test_0 探测器 Decelerating at height of 1883.48 with vertical speed of -294.05 and horizonal speed of 6.77
# 2021-08-29 10:50:39 decoupled_test_0 探测器 Decelerating at height of 1844.80 with vertical speed of -294.09 and horizonal speed of 5.82
# 2021-08-29 10:50:40 decoupled_test_0 探测器 Decelerating at height of 1877.73 with vertical speed of -294.74 and horizonal speed of 4.89
# 2021-08-29 10:50:41 decoupled_test_0 探测器 Decelerating at height of 1911.91 with vertical speed of -295.80 and horizonal speed of 7.01
# 2021-08-29 10:50:48 Decoupler Decelerating at height of 1853.65 with vertical speed of -309.39 and horizonal speed of 13.59
# 2021-08-29 10:51:02 decoupled_test_0 探测器 Auto landing completed
# 2021-08-29 10:51:03 decoupled_test_0 探测器 Auto landing completed
# 2021-08-29 10:51:03 decoupled_test_0 探测器 Auto landing completed
# 2021-08-29 10:51:03 decoupled_test_0 探测器 Auto landing completed
# 2021-08-29 10:51:07 Decoupler Auto landing completed