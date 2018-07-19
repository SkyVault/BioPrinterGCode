"""
    This library gives a user level control over 
    the linuxcnc powered device
"""

import sys
import linuxcnc

class LinuxCncMachine():
    def __init__(self):
        self.data = {}
        self.command = linuxcnc.command()
        self.xflipper = -1

    def poll(self):
        try:
            conn = linuxcnc.stat()
            conn.poll()
        except linuxcnc.error, detail:
            print("Error: ", detail)
            return

        for item in dir(conn):
            if not item.startswith('_'):
                self.data[item] = getattr(conn, item)
                # print(item, getattr(conn, item))

        # print(self.data)

    def getVelocity(self):
        if self.data['current_vel'] == None:
            return 0.0
        return float(self.data['current_vel'])

    def getPosition(self):
        if self.data['actual_position'] == None:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return self.data['actual_position']

    def moveSpindleDown(self):
        self.command.spindle(linuxcnc.SPINDLE_FORWARD)

        self.command.jog(linuxcnc.JOG_INCREMENT, 1, 2.0 * self.xflipper, 2.0)
            
        self.xflipper *= -1

    def resetSpindle(self):
        self.command.brake(1)
