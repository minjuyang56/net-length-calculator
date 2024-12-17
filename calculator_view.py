import sys
import json
from calculator_model import NetLengthCalculator
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt5.QtCore import Qt

class NetViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.net_calculator = NetLengthCalculator()
        self.net_dic = self.net_calculator.get_nets_dic()
        self.setWindowTitle("Net Viewer GUI")
        self.setGeometry(100, 100, 1000, 600)

        self.layout = QHBoxLayout(self)  # Main layout        
        
        self._set_left_widget()
        self._set_right_widget()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([400, 900])  # You can adjust these numbers as needed

        self.layout.addWidget(splitter)

        self.populate_net_list()
    
    def _set_left_widget(self):
        self.left_layout = QVBoxLayout()

        self.unit_label = QLabel(f"Unit: {self.net_calculator.get_current_unit()}") 
        self.left_layout.addWidget(self.unit_label)

        self.net_list = QListWidget()
        self.net_list.setSelectionMode(QListWidget.MultiSelection)  # 다중 선택 가능
        self.net_list.itemSelectionChanged.connect(self.update_net_details)
        self.left_layout.addWidget(self.net_list)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_net_info)
        self.left_layout.addWidget(self.clear_button)

        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_layout)

    def _set_right_widget(self):
        self.right_widget = QTreeWidget()
        self.right_widget.setHeaderLabels(["Property", "Value"])

        self.right_widget.setColumnWidth(0, 300)  # Property column (3 parts)
        self.right_widget.setColumnWidth(1, 400)  # Value column (7 parts)

    def clear_net_info(self):
        self.right_widget.clear()
        self.net_list.clearSelection()  # 선택된 항목 모두 해제

    def populate_net_list(self):
        for net in self.net_dic:
            self.net_list.addItem(net["net name"])
    
    def update_net_details(self):
        selected_items = self.net_list.selectedItems()
        
        self.right_widget.clear()  # 기존 정보 지우기
        for item in selected_items:
            net_name = item.text()
            net = self.get_net_by_name(net_name)
            if net:
                self.add_net_info_to_tree(net)
    
    def get_net_by_name(self, name):
        for net in self.net_dic:
            if net["net name"] == name:
                return net
        return None
    
    def add_net_info_to_tree(self, net, parent_item=None):
        if parent_item is None:
            parent_item = QTreeWidgetItem(self.right_widget)
            parent_item.setText(0, net["net name"])
        
        for key, value in net.items():
            if key == "trace layer":  # trace layer의 경우 딕셔너리가 아니기 때문에 따로 처리
                trace_item = QTreeWidgetItem(parent_item)
                trace_item.setText(0, "trace Layers")
                for layer in value:
                    prop_item = QTreeWidgetItem(trace_item)
                    prop_item.setText(0, layer.split(':')[0]) # Layer3 이런거
                    prop_item.setText(1, layer.split(':')[1]) 
            elif isinstance(value, dict):
                dict_info_item = QTreeWidgetItem(parent_item)
                dict_info_item.setText(0, key)
                self.add_net_info_to_tree(value, dict_info_item)
            elif not isinstance(value, list):  # 단일 값 속성 추가
                prop_item = QTreeWidgetItem(parent_item)
                prop_item.setText(0, key)
                prop_item.setText(1, str(value))

if __name__ == "__main__":
    app = QApplication(sys.argv) # 얘는 이벤트 감시자 어떤 이벤트든 감시
    viewer = NetViewer() # 얘는 
    viewer.show()
    sys.exit(app.exec_())
