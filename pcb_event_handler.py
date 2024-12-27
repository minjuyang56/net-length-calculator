from PyQt5.QtCore import pyqtSignal, QObject

class PCBEventHandler(QObject):
    signal_from_event_handler = pyqtSignal() # pcb App -> Pcb object

    def __init__(self):
        super().__init__()

    def OnSelectionChange(self, *args):
        self.signal_from_event_handler.emit() # pcb App -> Pcb object
        print('Selection change event triggered.')

    def OnClick(self, *args):
        print('Print X, Y position')

    
def main():
    from xpedition_manager import XpeditionManager

    xm = XpeditionManager()
    xm.initialize_pcb()

    xm.set_event_handler(xm.pcb_doc, PCBEventHandler)
    xm.run_message_loop()

    
if __name__ == '__main__':
    main()

