from collections import defaultdict
import sys
from calculator_model import NetLengthCalculator
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QDialogButtonBox,
    QListWidget, QTableWidget, QTableWidgetItem, QToolButton, QDialog, QTreeWidget, QTreeWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon

class ComponentSettingDialog(QDialog):
    def __init__(self, component_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Component Setting")
        self.setGeometry(200, 200, 400, 300)
        self.selected_components = []

        self.layout = QVBoxLayout(self)

        # Ref Component
        self.ref_component_label = QLabel("Ref Component: ")
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

class DaisyNetViewer(QWidget):
    def __init__(self, cal):
        super().__init__()

        self.setWindowIcon(QIcon("asset/pcb.png"))

        # cal 모델 객체 선언
        self.net_calculator = cal
        self.net_calculator.signal_to_gui.connect(self.event_occured_in_pcb_app) # selection change 있을 때 (나중에) 실행됨
        
        # 프로퍼티 설정
        self.table_nets = []
        self.table_fromto = defaultdict(dict) # table[net_name][comp]
        self.ref_net_location = None

        # 버튼
        self.ref_net_label = QLabel('Ref Net: Double click a net in the table.')
        self.ref_comp_label = QLabel('Ref Comp:')
        self.component_setting_button = QPushButton("Component Setting")
        self.sort_button = QPushButton()
        self.sort_button.setIcon(QIcon("asset/sort.png")) 
        self.is_ascending = None  # None은 초기 상태
        self.fix_toggle = QToolButton()
        self.fix_toggle.setText("Fix Nets")
        self.fix_toggle.setCheckable(True)  # 토글 가능한 상태로 설정
        self.fix_toggle.setChecked(False)   # 초기 상태는 비활성화
        self.fix_toggle.setStyleSheet("font-size: 12px;")  # 텍스트 크기 설정
        self.difference_button = QPushButton("Difference")
        self.difference_button.setCheckable(True)  # 토글 가능하도록 설정
        self.update_button = QPushButton("Update")
        self.update_button.setFixedSize(80, 30)  # 버튼 크기 설정
        self.unit_label = QLabel(f"Unit: {self.net_calculator.get_current_unit()}") 
        self._connect_logic_to_buttons()
        
        # 테이블
        self.nets_table_widget = QTableWidget()
        self.nets_table_widget.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.widget = QWidget()
        self.layout = QHBoxLayout(self)  
        
        self.initial_setting()
        self.set_props()

    @Slot()
    def event_occured_in_pcb_app(self):
        if not self.fix_toggle.isChecked():  # fix_toggle은 fix 토글을 나타내는 QWidget
            self._set_table_nets()
            self.ref_net_location = None
            self.ref_net_label.setText('Ref Net: Double click a net in the table.')
            self.ref_comp_label.setText('Ref Comp:')
        # 넷 길이 수정중...
    
    def initial_setting(self):
        self.setWindowTitle("Net Viewer GUI")
        self.setGeometry(100, 100, 1200, 600)

    def set_props(self):
        self._set_initial_nets_table_widget()
        self._set_layout()  

        self._set_table_nets() # 처음 한번만 딱 실행 
        self._set_table_fromto()

    def _set_initial_nets_table_widget(self):
        self.nets_table_widget.setColumnCount(1)
        self.nets_table_widget.setHorizontalHeaderLabels(["Net Name"])
    
    def _set_layout(self):
        layout = QVBoxLayout() # 세로 3칸

        # ref 결정하는 세로 레이아웃
        ref_layout = QVBoxLayout()
        ref_layout.addWidget(self.ref_net_label)
        ref_comp_layout = QHBoxLayout()
        ref_comp_layout.addWidget(self.ref_comp_label)
        ref_comp_layout.addWidget(self.component_setting_button)
        ref_comp_layout.addStretch()
        ref_layout.addLayout(ref_comp_layout)

        # 수평 레이아웃에 버튼 추가
        top_button_layout = QHBoxLayout() # 버튼 가로 4칸
        top_button_layout.addLayout(ref_layout)
        top_button_layout.addStretch()
        top_button_layout.addWidget(self.fix_toggle)  
        top_button_layout.addWidget(self.sort_button)

        # 업데이트 버튼
        update_layout = QHBoxLayout()
        update_layout.addStretch()  # 왼쪽에 여백 추가
        update_layout.addWidget(self.difference_button)
        update_layout.addWidget(self.update_button)

        bottom_button_layout = QHBoxLayout() 
        bottom_button_layout.addWidget(self.unit_label)
        bottom_button_layout.addLayout(update_layout) 

        layout.addLayout(top_button_layout)  # 수평 레이아웃 추가
        layout.addWidget(self.nets_table_widget)
        layout.addLayout(bottom_button_layout) # 리프레시는 초기상태 그 fromto 길이로 리프레시시
        self.widget.setLayout(layout)

        self.layout.addWidget(self.widget)

    def _set_table_nets(self): # self.table_nets 내용을 Gui에 뿌려주는 것 
        self.nets_table_widget.setColumnCount(1)
        self.nets_table_widget.setRowCount(0) 
        if self.net_calculator.get_selected_nets():
            self.table_nets = self.net_calculator.get_selected_nets()
        row_position = self.nets_table_widget.rowCount()
        
        for i, net in enumerate(self.table_nets):
            self.nets_table_widget.insertRow(row_position + i)
            item = QTableWidgetItem(net.name)
            item.setTextAlignment(Qt.AlignCenter) 
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.nets_table_widget.setItem(row_position + i, 0, item)

    def _set_table_fromto(self): # 얘는 처음 한번만 실행되고, 데이터 가져오는건 추상화되어있어야됨됨
        # 컬럼 세팅
        comp_set = self.net_calculator.comp_connection_cal.comp_set
        headers = [comp.Name for comp in comp_set]
        self.nets_table_widget.setColumnCount(len(headers)+1)
        for i, header in enumerate(headers):
            self.nets_table_widget.setHorizontalHeaderItem(1+i, QTableWidgetItem(header))
        self.nets_table_widget.horizontalHeader().setSectionsMovable(True)

        # 표 length 데이터 세팅
        for i in range(self.nets_table_widget.rowCount()):
            net_name = self.nets_table_widget.item(i,0).text()
            for net_candidate in self.table_nets:
                if net_candidate.name == net_name:
                    net = net_candidate
            for j, comp in enumerate(comp_set, start=1): # 컴포넌트 세트의 갯수만큼 돌림               
                length_item = QTableWidgetItem(str(self.table_fromto[net.name][comp.Name]))
                length_item.setTextAlignment(Qt.AlignCenter) 
                self.nets_table_widget.setItem(i, j, length_item)
        
        self.change_background(self.ref_net_location)

    def show_warning(self, message):
            """
            경고창을 띄우는 함수
            :param message: 경고창에 표시할 메시지 내용
            """
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warning")
            msg.setText(message)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def on_cell_double_clicked(self, row, column):                
        self.ref_net_location = (row, column)
        self.ref_net_label.setText('Ref Net' + ': ' + self.nets_table_widget.item(row, 0).text())
        self.change_background((row, column))

    def change_background(self, ref_net_location):
        if not ref_net_location:
            return 
        
        for i in range(self.nets_table_widget.rowCount()):
            for j in range(self.nets_table_widget.columnCount()):
                item = self.nets_table_widget.item(i, j)
                if item:
                    item.setBackground(Qt.white)  # Reset all cells to white

        for j in range(self.nets_table_widget.columnCount()):
            item = self.nets_table_widget.item(ref_net_location[0], j)
            if item:
                item.setBackground(Qt.yellow)  # Highlight the row

    def _connect_logic_to_buttons(self): # set_props에서 호출됨됨
        self.component_setting_button.clicked.connect(self.open_component_setting)
        self.difference_button.toggled.connect(self.toggle_difference)
        self.update_button.clicked.connect(self.update_data)
        self.sort_button.clicked.connect(self.toggle_sort_order)
    
    def toggle_sort_order(self):
        # 상태 변경
        if self.is_ascending is None:
            self.is_ascending = True  # 처음 클릭은 오름차순
        else:
            self.is_ascending = not self.is_ascending  # 상태 토글

        # 상태에 따른 버튼 업데이트
        if self.is_ascending:
            self.sort_button.setIcon(QIcon("asset/asc.png"))  # 오름차순
            self.nets_table_widget.sortItems(0, Qt.AscendingOrder)
        else:
            self.sort_button.setIcon(QIcon("asset/desc.png"))  # 내림차순
            self.nets_table_widget.sortItems(0, Qt.DescendingOrder)
    
    def toggle_difference(self, checked):
        if checked:
            self.update_net_length_diff()
            ref_net_name = self.ref_net_label.text().replace('Ref Net: ', '').strip()
            for row in range(self.nets_table_widget.rowCount()):
                item = self.nets_table_widget.item(row, 0)  # 첫 번째 컬럼 (Net name)
                if item and item.text() == ref_net_name:
                    column = self.ref_net_location[1]  # 원래의 column 위치를 가져옵니다.
                    self.ref_net_location = (row, column)
            self.change_background(self.ref_net_location)
        else:
            self._set_table_fromto()
            self.change_background(self.ref_net_location)
    
    def open_component_setting(self):
        try:
            component_name_list = []
            for net in self.table_nets:
                component_name_list.extend([comp.Name for comp in net.get_connected_comps()])
            component_name_list = sorted(list(set(component_name_list)))

            dialog = ComponentSettingDialog(component_name_list, self)
            if dialog.exec_() == QDialog.Accepted:
                ref_component, component_set = dialog.get_selection() # U21 ['U27', 'U26', 'U28', 'U29'] str list
                for net in self.table_nets:
                    self.net_calculator.comp_connection_cal.set_props(net, ref_component, component_set, self.net_calculator.pcb_doc) # 여기서 핀 페어 완성해줌
                    self.table_fromto[net.name] = self.net_calculator.get_connection_table()
                self.ref_net_location = None
                self._set_table_fromto() # 무조건 여기서만 등장
                self.ref_comp_label.setText('Ref Comp: ' + ref_component)
                self.ref_net_label.setText('Ref Net: Double click a net in the table.')
        except IndexError:
            # IndexError 발생 시 경고창 표시
            self.show_warning("No nets are selected. Please select a net first.")
        except Exception as e:
            # 기타 예상치 못한 오류 처리
            self.show_warning(f"An unexpected error occurred: {str(e)}")
    
    def update_data(self): 
        if self.table_fromto:
            for net in self.table_nets:
                self.net_calculator.comp_connection_cal.set_comp_pin_pair(net)
                self.table_fromto[net.name] = self.net_calculator.get_connection_table()

                # 표 length 데이터 세팅
                comp_set = self.net_calculator.comp_connection_cal.comp_set
                if not comp_set:
                    self.show_warning('Set component first.')
                else:
                    for i in range(self.nets_table_widget.rowCount()):
                        net_name = self.nets_table_widget.item(i,0).text()
                        for net_candidate in self.table_nets:
                            if net_candidate.name == net_name:
                                net = net_candidate
                        for j, comp in enumerate(comp_set, start=1): # 컴포넌트 세트의 갯수만큼 돌림               
                            length_item = QTableWidgetItem(str(self.table_fromto[net.name][comp.Name]))
                            length_item.setTextAlignment(Qt.AlignCenter) 
                            self.nets_table_widget.setItem(i, j, length_item)
                    self.change_background(self.ref_net_location)
                    
                    if self.difference_button.isChecked():
                        self.update_net_length_diff()
                        self.change_background(self.ref_net_location)
        else:
            self.show_warning('Set components first.')

    def get_net_by_name(self, name):
        for net in self.table_nets:
            if net.name == name:
                return net
        return None  
    
    def update_net_length_diff(self):
        if 'Ref Net: ' in self.ref_net_label.text():
            ref_net_name = self.ref_net_label.text().replace('Ref Net: ', '').strip()
            ref_net = self.get_net_by_name(ref_net_name)
            
            if ref_net:
                # 기준행 위치 찾기
                row_count = self.nets_table_widget.rowCount()
                for row in range(row_count):
                    item = self.nets_table_widget.item(row, 0)  # 첫 번째 컬럼 (0번 컬럼)
                    if item and item.text() == ref_net_name:
                        ref_net_row = row
                
                # 기준행 데이터 저장
                ref_row_data = [
                        float(self.nets_table_widget.item(ref_net_row, col).text()) 
                        if self.nets_table_widget.item(ref_net_row, col).text() != '-' else '-'
                        for col in range(1, self.nets_table_widget.columnCount())
                    ]
                comp_set = self.net_calculator.comp_connection_cal.comp_set
                # 표 length 데이터 세팅
                for i in range(self.nets_table_widget.rowCount()):
                    net_name = self.nets_table_widget.item(i,0).text()
                    for net_candidate in self.table_nets:
                        if net_candidate.name == net_name:
                            net = net_candidate
                    for j, comp in enumerate(comp_set, start=1): # 컴포넌트 세트의 갯수만큼 돌림
                        difference = '-'
                        ref_item = ref_row_data[j-1]
                        dest_item = self.nets_table_widget.item(i, j).text()
                        if ref_item != '-' and dest_item != '-':
                            difference = round(float(dest_item) - ref_item, self.net_calculator.get_current_precision())  
                            difference = str(difference)        
                        length_item = QTableWidgetItem(difference)
                        length_item.setTextAlignment(Qt.AlignCenter)
                        self.nets_table_widget.setItem(i, j, length_item)  
    
    def print_table(self):
        row_count = self.nets_table_widget.rowCount()
        col_count = self.nets_table_widget.columnCount()

        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.nets_table_widget.item(row, col)
                text = item.text() if item is not None else ''
                row_data.append(text)
            
            print("\t".join(row_data))

                
                                   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DaisyNetViewer()
    viewer.show()
    
    sys.exit(app.exec_())