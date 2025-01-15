from collections import defaultdict
import sys
from calculator_model import NetLengthCalculator
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QDialogButtonBox,
    QListWidget, QTableWidget, QTableWidgetItem, QSplitter, QDialog, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtGui import QDrag
from PySide6.QtCore import Qt, QMimeData, Slot

class ComponentSettingDialog(QDialog):
    def __init__(self, component_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Component Setting")
        self.setGeometry(200, 200, 400, 300)
        self.selected_components = []

        self.layout = QVBoxLayout(self)

        # Ref Component
        self.ref_component_label = QLabel("Ref Component:")
        self.ref_component_combo = QComboBox()
        self.ref_component_combo.addItems(component_list)
        self.layout.addWidget(self.ref_component_label)
        self.layout.addWidget(self.ref_component_combo)

        # Component Set
        self.component_set_label = QLabel("Component Set:")
        self.component_set_list = QListWidget()
        self.component_set_list.addItems(component_list)
        self.component_set_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.component_set_label)
        self.layout.addWidget(self.component_set_list)

        # Confirm and Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_selection(self): # ok를 눌러야지 실행됨
        ref_component = self.ref_component_combo.currentText()
        selected_items = self.component_set_list.selectedItems()
        component_set = [item.text() for item in selected_items]
        return ref_component, component_set
    
class NetDetailsDialog(QDialog):
    def __init__(self, net):
        super().__init__()
        self.setWindowTitle(f"Net Details - {net['net name']}")
        self.setGeometry(150, 150, 700, 500)
        self.layout = QVBoxLayout(self)

        self.details_widget = QTreeWidget()
        self.details_widget.setHeaderLabels(["Property", "Value"])
        self.layout.addWidget(self.details_widget)

        self._populate_details(net)
    
    def _populate_details(self, net, parent_item=None):
        if parent_item is None:
            parent_item = QTreeWidgetItem(self.details_widget)
            parent_item.setText(0, net["net name"])

        for key, value in net.items():
            if key == "trace layer":
                trace_item = QTreeWidgetItem(parent_item)
                trace_item.setText(0, "trace Layers")
                for layer in value:
                    prop_item = QTreeWidgetItem(trace_item)
                    prop_item.setText(0, layer.split(':')[0]) 
                    prop_item.setText(1, layer.split(':')[1])
            elif isinstance(value, dict):
                dict_info_item = QTreeWidgetItem(parent_item)
                dict_info_item.setText(0, key)
                self._populate_details(value, dict_info_item)
            elif not isinstance(value, list):
                prop_item = QTreeWidgetItem(parent_item)
                prop_item.setText(0, key)
                prop_item.setText(1, str(value))

class RefNet(QLabel):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.parent = parent 

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            self.setStyleSheet('background-color: yellow;')
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, e):
        self.setStyleSheet('background-color: none;')  # 배경색 초기화
        self.setText('Ref Net: ' + e.mimeData().text())
        self.parent.update_net_length_diff()

class NetViewer(QWidget):
    def __init__(self, cal):
        super().__init__()
        self.net_calculator = cal
        self.net_calculator.signal_to_gui.connect(self.change_net_dic_slot)
        self.net_dic = self.net_calculator.get_nets_dic()

        self.unit_label = QLabel(f"Unit: {self.net_calculator.get_current_unit()}") 
        self.nets_list_widget = QListWidget()
        self.clear_button = QPushButton("Clear")
        self.sort_ascending_button = QPushButton("↗")  # 오름차순 버튼
        self.sort_descending_button = QPushButton("↘")  # 내림차순 버튼
        self.component_setting_button = QPushButton("Component Setting")
        self.nets_table_widget = QTableWidget()
        self.ref_net_button = RefNet('Drop Ref Net here.', self)
        self.left_widget = QWidget()
        self.right_widget = QWidget()
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout = QHBoxLayout(self)  
        
        self.initial_setting()
        self.set_props()

        self.selected_items = None
        self.connection_table = defaultdict(dict)

    @Slot()
    def change_net_dic_slot(self):
        # self.clear_table()
        self.nets_list_widget.clearSelection()
        self.nets_list_widget.clear()
        self.net_dic = self.net_calculator.get_nets_dic()
        self.populate_net_list()

    def initial_setting(self):
        self.setWindowTitle("Net Viewer GUI")
        self.setGeometry(100, 100, 1200, 600)

    def set_props(self):
        self._set_nets_table_widget()
        self._set_nets_list_widget()
        self._set_clear_button()
        self._set_ref_net()

        self._set_left_widget()
        self._set_right_widget()

        self._set_splitter()

        self._set_layout()  

        self.populate_net_list()

        self._set_top_buttons()

    def _set_layout(self):
        self.layout.addWidget(self.splitter)

    def _set_splitter(self):
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([400, 900])  

    def _set_nets_list_widget(self):
        self.nets_list_widget.setSelectionMode(QListWidget.MultiSelection)  
        self.nets_list_widget.itemSelectionChanged.connect(self.update_table)

    def update_table(self):
        self.nets_table_widget.setColumnCount(3)
        self.nets_table_widget.setHorizontalHeaderLabels(["Net Name", "Net Length", "Difference"])
        self.selected_items = self.nets_list_widget.selectedItems()
        if not self.selected_items:
            return           

        self.nets_table_widget.setRowCount(0)  
        for item in self.selected_items:
            net_name = item.text()
            net = self.get_net_by_name(net_name) # net 딕셔너리에서 net_name으로 찾기 
            if net:
                row_position = self.nets_table_widget.rowCount()
                self.nets_table_widget.insertRow(row_position)
                
                net_name_item = QTableWidgetItem(net_name)
                length_item = QTableWidgetItem(str(net["electrical net"]["full length"]))
                diff_item = QTableWidgetItem("-")  
                
                self.nets_table_widget.setItem(row_position, 0, net_name_item)
                self.nets_table_widget.setItem(row_position, 1, length_item)
                self.nets_table_widget.setItem(row_position, 2, diff_item)

    def _set_clear_button(self):
        self.clear_button.clicked.connect(self.clear_table)

    def clear_table(self):
        self.nets_table_widget.setRowCount(0) 

    def _set_left_widget(self):
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.unit_label)
        left_layout.addWidget(self.nets_list_widget)
        left_layout.addWidget(self.clear_button)

        self.left_widget.setLayout(left_layout)

    def _set_nets_table_widget(self):
        self.nets_table_widget.setColumnCount(3)
        self.nets_table_widget.setHorizontalHeaderLabels(["Net Name", "Net Length", "Difference"])

        self.nets_table_widget.setDragEnabled(True)
        self.nets_table_widget.setAcceptDrops(True)
        self.nets_table_widget.setDragDropMode(QTableWidget.DragDrop)  # InternalMove → DragDrop
        self.nets_table_widget.setDefaultDropAction(Qt.MoveAction)  # 기본 드롭 액션

        self.nets_table_widget.cellPressed.connect(self.start_drag)

        self.nets_table_widget.cellDoubleClicked.connect(self.show_net_details)
    
    def start_drag(self, row, column):
        """셀을 드래그할 때 호출됩니다."""
        item = self.nets_table_widget.item(row, column)
        if not item:
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(item.text())
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    def dropEvent(self, e):
        if e.mimeData().hasText():
            text = e.mimeData().text()
            print(f"Dropped text: {text}")
            e.accept()
        else:
            e.ignore()

    def _set_ref_net(self):
        self.ref_net_button.move(130, 15)

    def _set_right_widget(self):
        right_layout = QVBoxLayout()

        # 수평 레이아웃에 버튼 추가
        top_button_layout = QHBoxLayout()
        top_button_layout.addWidget(self.ref_net_button)
        top_button_layout.addWidget(self.sort_ascending_button)
        top_button_layout.addWidget(self.sort_descending_button)
        top_button_layout.addWidget(self.component_setting_button)


        # 정렬 버튼 크기 설정 (작은 정사각형으로)
        self.sort_ascending_button.setFixedSize(30, 30)
        self.sort_descending_button.setFixedSize(30, 30)

        right_layout.addLayout(top_button_layout)  # 수평 레이아웃 추가
        right_layout.addWidget(self.nets_table_widget)
        self.right_widget.setLayout(right_layout)
        
    def show_net_details(self, row, column):
        if row < 0:  
            return
        
        net_name = self.nets_table_widget.item(row, 0).text()
        net = self.get_net_by_name(net_name)
        if net:
            details_dialog = NetDetailsDialog(net)
            details_dialog.exec_()
    
    def populate_net_list(self):
        for net in self.net_dic:
            self.nets_list_widget.addItem(net["net name"])
    
    def get_net_by_name(self, name):
        for net in self.net_dic:
            if net["net name"] == name:
                return net
        return None

    def _set_top_buttons(self): # set_props에서 호출됨
        self.sort_ascending_button.clicked.connect(self.sort_ascending)  # 오름차순 정렬 함수 연결
        self.sort_descending_button.clicked.connect(self.sort_descending)  # 내림차순 정렬 함수 연결
        self.component_setting_button.clicked.connect(self.open_component_setting)

    def sort_ascending(self):
        self.nets_table_widget.sortItems(0, Qt.AscendingOrder)

    def sort_descending(self):
        self.nets_table_widget.sortItems(0, Qt.DescendingOrder)
    
    def open_component_setting(self):
        component_list = ["U21", "U26", "U27", "U28", "U29"]  # 예제용 컴포넌트 리스트
        dialog = ComponentSettingDialog(component_list, self)
        if dialog.exec_() == QDialog.Accepted:
            ref_component, component_set = dialog.get_selection() # U21 ['U27', 'U26', 'U28', 'U29'] str list
            # selected_items = self.nets_list_widget.selectedItems()  
            # print('selected_item', selected_items)     

            # 여기 반복문에서 시간이 너무 오래걸림...
            for item in self.selected_items:
                net_name = item.text()
                net = self.net_calculator.get_net_by_name(net_name)
                # 테이블 행 한줄 결정
                self.net_calculator.comp_connection_cal.set_props(net, ref_component, component_set, self.net_calculator.pcb_doc) # 여기서 핀 페어 완성해줌
                self.connection_table[net_name] = self.net_calculator.get_connection_table()
   
            self.update_connection_table()

    def update_connection_table(self):
        # selected_items = self.nets_list_widget.selectedItems()
        if not self.selected_items:
            return           

        self.nets_table_widget.setRowCount(0)  
        for item in self.selected_items:
            net_name = item.text()
            net = self.get_net_by_name(net_name) # net 딕셔너리에서 net_name으로 찾기 
            if net:
                row_position = self.nets_table_widget.rowCount()
                self.nets_table_widget.insertRow(row_position)
                
                net_name_item = QTableWidgetItem(net_name)
                self.nets_table_widget.setItem(row_position, 0, net_name_item)

                comp_set = self.net_calculator.comp_connection_cal.comp_set
                headers = ["Net Name"]
                headers.extend([comp.Name for comp in comp_set])
                self.nets_table_widget.setColumnCount(len(headers))  # 컬럼 개수 설정
                self.nets_table_widget.setHorizontalHeaderLabels(headers)
                self.nets_table_widget.horizontalHeader().setSectionsMovable(True)
                for i, comp in enumerate(comp_set, start=1): # 컴포넌트 세트의 갯수만큼 돌림림
                    length_item = QTableWidgetItem(str(self.connection_table[net_name][comp.Name]))
                    self.nets_table_widget.setItem(row_position, i, length_item)

    def update_net_length_diff(self):
        if 'Ref Net: ' in self.ref_net_button.text():
            ref_net_name = self.ref_net_button.text().replace('Ref Net: ', '').strip()
            ref_net = self.get_net_by_name(ref_net_name)
            
            if ref_net:
                ref_net_length = float(ref_net["electrical net"]["full length"].replace('mm', '').strip())
                
                for row in range(self.nets_table_widget.rowCount()):
                    net_name_item = self.nets_table_widget.item(row, 0)
                    if net_name_item:
                        net_name = net_name_item.text()
                        net = self.get_net_by_name(net_name)
                        
                        if net:
                            net_length = float(net["electrical net"]["full length"].replace('mm', '').strip())
                            
                            # Net Length의 차이를 계산
                            length_diff = ref_net_length - net_length

                            # 차이 값을 테이블에 업데이트
                            length_item = self.nets_table_widget.item(row, 2)
                            if length_item:
                                if not length_diff:
                                    length_item.setText(f"0")
                                else:
                                    length_item.setText(f"{length_diff:.6f}")
                                    

if __name__ == "__main__":

    app = QApplication(sys.argv)
    viewer = NetViewer()
    viewer.show()
    
    sys.exit(app.exec_())
