import sys
from PyQt5.QtWidgets import QApplication
from calculator_view_elect_net import NetViewer
from calculator_view_daisy_chain import DaisyNetViewer
from calculator_model import NetLengthCalculator


'''
logic - calculator_model.py
GUI - calculator_view.py
event - pcb_event_handler.py
'''
def main():
    app = QApplication(sys.argv)

    cal = NetLengthCalculator()
    viewer = DaisyNetViewer(cal)

    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()