from calculator_model import NetLengthCalculator
from calculator_view import NetViewer
from Scripts.Python_Automation.xpedition_layout.pcb_event_handler import *

'''
logic - calculator_model.py
GUI - calculator_view.py
event - event_handler.py
'''
eventHandler = win32.DispatchWithEvents(pcbDoc, PCBEventHandler)

