import socket

import win32serviceutil

import servicemanager
import win32event
import win32service
import tkinter

import time
from pathlib import Path


class PyService(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'pythonService'
    _svc_display_name_ = 'Python Service'
    _svc_description_ = 'Python Service Description'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        self.running = True
        self.main()
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        self.running = False 
        pass

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        for i in range(3):
            Path(f"C:\\Users\\Kevin\\Desktop\\test{i}.txt").touch()
            time.sleep(3)
        pass

# entry point of the module: copy and paste into the new module
# ensuring you are calling the "parse_command_line" of the new created class
if __name__ == '__main__':
    PyService.parse_command_line()