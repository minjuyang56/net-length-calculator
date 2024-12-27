import sys
from PyQt5.QtWidgets import QApplication
from calculator_view_copy import NetViewer
from calculator_model import NetLengthCalculator

'''
logic - calculator_model.py
GUI - calculator_view.py
event - pcb_event_handler.py
'''
def main():
    app = QApplication(sys.argv)

    cal = NetLengthCalculator()
    viewer = NetViewer(cal) 

    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()






# 예시로 직접 이벤트 호출
# viewer.net_calculator.event_handler.OnSelectionChange()  # "Selection change event triggered." 출력
# cal.event_handler.selection_change_signal.emit()  # 슬롯에서 처리 가능
# viewer.net_calculator.event_handler = PCBEventHandler
# viewer.net_calculator.event_dispatch = DispatchWithEvents(viewer.net_calculator.pcb_doc, viewer.net_calculator.event_handler)
# viewer.net_calculator.event_handler.selection_change_signal.connect(viewer.change_net_dic_slot)
        