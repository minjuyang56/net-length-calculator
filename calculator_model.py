import json
from xpedition_manager import XpeditionManager

class Net:
    def __init__(self):
        self.name = None
        self.com = None
        self.cm = None
        self.type = None
        self.elect_net = None
        self.trace_length = None  # list
        self.trace_per_layer = []
        self.trace_extremas = []
        self.layer_gaps = None
        self.length = None
        self.connected_comps = []

    def _net_type_cm(self):
        net_type_cm = self.cm.ObjectType
        if net_type_cm == 47:  # OT_ElectricalNet (그냥 넷의 부모)
            return "OT_ElectricalNet"
        elif net_type_cm == 49:  # OT_Net
            return "OT_Net"
        elif net_type_cm == 26:  # OT_ConstraintClass (일렉넷의 부모)
            return "OT_ConstraintClass"
        elif net_type_cm == 50:
            return "OT_FromTo"
        elif net_type_cm == 48:
            return "OT_PinPair"
        else:
            return net_type_cm

    def get_trace_per_layer(self):
        trace_per_layer = []
        for trace in self.com.Traces:
            trace_per_layer.append(("Layer " + str(trace.Layer), trace.Length))
        return trace_per_layer

    def get_trace_length(self):  
        trace_length = 0
        for trace in self.com.Traces:
            trace_length += trace.Length
        return trace_length
    
    def get_trace_extrema(self):
        trace_extremas = []
        for trace in self.com.Traces:
            trace_extrema = trace.Extrema
            trace_extremas.append(((trace_extrema.MinX, trace_extrema.MinY), (trace_extrema.MaxX, trace_extrema.MaxY)))
        return trace_extremas

    def get_passing_components(self):
        passing_comps = []
        for connection in self.com.Connections:
            print(connection)

    def get_connected_comps(self):
        connected_comps = []
        for pin in self.com.Pins:
            comp = pin.Parent
            connected_comps.append(comp)
        return connected_comps

    def set_props(self, net_com, design_cm, pcb_doc):  
        self.name = net_com.Name
        self.com = net_com
        self.cm = design_cm.GetNets(15).Item(self.com.Name)
        self.type = self._net_type_cm()
        self.connected_comps = self.get_connected_comps()
        
        if self.type == "OT_ElectricalNet":  # 일렉넷이면 한번 더 가서 그냥 네트로 바꿔줌
            self.cm = self.cm.Objects.Item(1)
            self.type = self._net_type_cm()
        self.trace_length = self.get_trace_length()

        if self.trace_length:
            self.trace_extremas = self.get_trace_extrema()
            self.layer_stackup = LayerStackup()
            self.layer_stackup.set_props(pcb_doc)
            self.layer_gaps = self.layer_stackup.compute_layer_gap_between_traces([self.com])
        else:
            self.trace_length = 0
            self.layer_gaps = 0
        self.trace_per_layer = self.get_trace_per_layer()
        self.length = self.trace_length + self.layer_gaps
       
    def new_elect_net(self):  
        self.elect_net = ElecNet()

    def set_elect_net_props(self, design_cm, pcb_doc):  
        self.elect_net.cm = self.cm.Parent
        self.elect_net.name = self.elect_net.cm.Name
        self.elect_net.type = self.elect_net._net_type_cm()
        self.elect_net.child_nets = self.elect_net.get_child_nets(design_cm, pcb_doc)
        self.elect_net.com = self.elect_net.get_com(pcb_doc)
        self.elect_net.trace_length = self.elect_net.get_trace_length()

        if self.trace_length:
            self.layer_stackup = LayerStackup()
            self.layer_stackup.set_props(pcb_doc)
            self.elect_net.layer_gaps = self.layer_stackup.compute_layer_gap_between_traces(
                self.elect_net.com
            )
        else:
            self.elect_net.trace_length = 0
            self.elect_net.layer_gaps = 0
        self.elect_net.trace_per_layer = self.elect_net.get_trace_per_layer()
        self.elect_net.length = self.elect_net.trace_length + self.elect_net.layer_gaps

    def to_dict(self):
        return {
            "net name": self.name,
            "type": self.type,
            "full length": f"{self.length}",
            "layer gap": self.layer_gaps if self.layer_gaps else 0,
            "trace layer": [
                f"{layer}" " : " f"{length}" for layer, length in self.trace_per_layer
            ],
            "electrical net": self.elect_net.to_dict()
        }
    
class ElecNet(Net):
    def __init__(self):
        super().__init__()
        self.child_nets = []
        self.trace_length = None
        self.layer_gaps = None
        self.length = None

    def get_child_nets(self, design_cm, pcb_doc):  
        child_nets = []
        for child_net_cm in self.cm.GetObjects():
            if child_net_cm.ObjectType == 49:
                child_net = ChildNet()
                child_net.set_props(
                    pcb_doc.GetNets(sNetName=child_net_cm.Name).Item(1), design_cm, pcb_doc
                )
                child_nets.append(child_net)
        return child_nets

    def get_trace_length(self):  
        length = 0
        for child_net in self.child_nets:
            length += child_net.trace_length
        return length

    def get_layer_gap(self): 
        gaps = 0
        for child_net in self.child_nets:
            gaps += child_net.layer_gaps
        return gaps

    def get_elect_net(self, net):  
        if net.type == "OT_ElectricalNet":
            return net.com
        elif net.type == "OT_Net":
            parent_net = net.cm.Parent
            return parent_net

    def get_com(self, pcb_doc):
        child_nets_com = []
        for child_net in self.child_nets:
            child_nets_com.append(pcb_doc.GetNets(sNetName=child_net.name).Item(1))
        return child_nets_com

    def get_trace_per_layer(self):
        trace_per_layer = []
        for child_net in self.child_nets:
            trace_per_layer.extend(child_net.trace_per_layer)
        return trace_per_layer
    
    def find_minimum_tolerance(self, net_name, match_group_mask):
        oTolerance = (2 ** 15) - 1  # 최대 정수값 32767로 초기화

        # 매치 그룹 순회
        for oMatchGroup in self.MatchGroups(match_group_mask):
            oConstraint = oMatchGroup.Constraints.FindItem("CT_MatchGroupTolerance")
            if oConstraint is not None:
                if oTolerance > oConstraint.Value:
                    oTolerance = oConstraint.Value

        return oTolerance

    def to_dict(self):
        return {
                "net name": self.name,
                "type": self.type,
                "full length": f"{self.length}",
                "layer gap": self.layer_gaps if self.layer_gaps else 0,
                "trace layer": [f"{layer}" " : " f"{length}" for layer, length in self.trace_per_layer],
                "child nets":  {child_net.name: child_net.to_dict() for child_net in self.child_nets},
            }
    

class ChildNet(Net):
    def __init__(self):
        super().__init__()
    
    def to_dict(self):
        return {
                "net name": self.name,
                "type": self.type,
                "full length": f"{self.length}",
                "layer gap": self.layer_gaps if self.layer_gaps else 0,
                "trace layer": [f"{layer}" " : " f"{length}" for layer, length in self.trace_per_layer],
            }


class LayerStackup:
    def __init__(self):
        self.signal_stackup_pcb = None
        self.whole_stackup_pcb = None
        self.whole_stackup_name = None
        self.thicknesses = []

    def set_props(self, pcb_doc):  
        self.signal_stackup_pcb = pcb_doc.GetLayerStack(0)
        self.whole_stackup_pcb = pcb_doc.GetLayerStack()
        self.whole_stackup_pcb_names = self.get_whole_stackup_names()
        self.thicknesses = self._get_thickness(pcb_doc)

    def get_whole_stackup_names(self):
        whole_stackup_names = []
        for layer_pcb in self.whole_stackup_pcb:
            whole_stackup_names.append(layer_pcb.LayerProperties.StackupLayerName)
        return whole_stackup_names

    def _get_thickness(self, pcb_doc):
        thicknesses = []
        for layer_pcb in pcb_doc.GetLayerStack():
            thicknesses.append(layer_pcb.LayerProperties.Thickness)
        return thicknesses

    def _get_net_layers_list(
        self, nets_com: list
    ):  # 리턴값 ['SIGNAL_1', 'SIGNAL_1', 'SIGNAL_2', 'SIGNAL_3', 'SIGNAL_2', 'SIGNAL_1']
        net_layers_names = []
        for net_com in nets_com:  # 일렉넷 안의 각각의 네트들
            for trace in net_com.Traces:  # 한 네트의 트레이스들
                layer_trace = trace.Layer
                layer_pcb = self.signal_stackup_pcb.Item(
                    layer_trace
                )  # layer1 -> signal1 로 변환
                net_layers_names.append(layer_pcb.LayerProperties.StackupLayerName)
        return net_layers_names

    def compute_layer_gap_between_traces(self, nets_com):
        trace_layers_names = self._get_net_layers_list(
            nets_com
        )  # ex) ['SIGNAL_1', 'SIGNAL_2', 'SIGNAL_3', 'SIGNAL_2']
        layer_gap_sum = 0
        if len(trace_layers_names):
            prelayer = trace_layers_names[0]
        for i in range(1, len(trace_layers_names)):
            if prelayer != trace_layers_names[i]:
                if self.whole_stackup_pcb_names.index(
                    prelayer
                ) < self.whole_stackup_pcb_names.index(trace_layers_names[i]):
                    layer_gap_sum += sum(
                        self.thicknesses[
                            self.whole_stackup_pcb_names.index(prelayer)
                            + 1 : self.whole_stackup_pcb_names.index(
                                trace_layers_names[i]
                            )
                        ]
                    )
                else:
                    layer_gap_sum += sum(
                        self.thicknesses[
                            self.whole_stackup_pcb_names.index(trace_layers_names[i])
                            + 1 : self.whole_stackup_pcb_names.index(prelayer)
                        ]
                    )
            prelayer = trace_layers_names[i]
        return layer_gap_sum
    
    def _get_net_layers_list_objs(self, objs):
        net_layers_names = []
        for obj in objs:  # 한 네트의 트레이스들
            if not obj:
                return 
            layer_obj = obj.Layer # 레이어가 0이 나올수도 있음????
            layer_pcb = self.signal_stackup_pcb.Item(
                layer_obj
            )  # layer1 -> signal1 로 변환
            if layer_pcb:
                net_layers_names.append(layer_pcb.LayerProperties.StackupLayerName)

        layer_gap_sum = 0
        if len(net_layers_names):
            prelayer = net_layers_names[0]
        for i in range(1, len(net_layers_names)):
            if prelayer != net_layers_names[i]:
                if self.whole_stackup_pcb_names.index(
                    prelayer
                ) < self.whole_stackup_pcb_names.index(net_layers_names[i]):
                    layer_gap_sum += sum(
                        self.thicknesses[
                            self.whole_stackup_pcb_names.index(prelayer)
                            + 1 : self.whole_stackup_pcb_names.index(
                                net_layers_names[i]
                            )
                        ]
                    )
                else:
                    layer_gap_sum += sum(
                        self.thicknesses[
                            self.whole_stackup_pcb_names.index(net_layers_names[i])
                            + 1 : self.whole_stackup_pcb_names.index(prelayer)
                        ]
                    )
            prelayer = net_layers_names[i]

        return layer_gap_sum
    
class Component:
    def __init__(
        self,
        name=None,
        com=None,
        obj_type=None,
        net_cm=None,
        trace_length: list = None,
        layer_gaps=None,
        length=None,
        from_to = None
    ):
        self.name = name
        self.com = com
        self.cm = net_cm
        self.type = obj_type
        self.elect_net = None
        self.trace_length = trace_length  # list
        self.trace_per_layer = []
        self.trace_extremas = []
        self.layer_gaps = layer_gaps
        self.length = length
        self.from_to = from_to

import math
from collections import Counter, defaultdict

class ComponentConnectionCalculator:
    def __init__(self):
        self.net = None
        self.ref_comp = None
        self.ref_pin = None
        self.comp_set = []
        self.comp_pin_pair = []

    def _get_pin(self, comp): # 그니까 컴포넌트, 네트 정해진 상태에서 핀 찾기  그 핀중에서 parent가 comp set인 것 찾으면 될듯듯
        for pin in self.net.com.Pins:
            if pin.Parent.Name == comp.Name:
                return comp.FindPin(pin.Name)
     
    def get_comp_pin_pair(self): # 컴포넌트를 정했으면 그 컴포넌트가 어느 핀과 (이미 선택한) 네트와 연결되는지 그 핀을 찾는 알고리즘 
        comp_pin_pair = []

        for comp in self.comp_set: 
            comp_pin_pair.append((comp, self._get_pin(comp)))
        return comp_pin_pair
    
    def get_comp_set(self, comp_set_txt, pcb_doc): # 사용자가 고른 comp_set 텍스트 받아서 
        comp_set = []
        for comp_txt in comp_set_txt:
            comp = pcb_doc.FindComponent(comp_txt)
            comp_set.append(comp)
        return comp_set
    
    def get_ref_comp(self, ref_comp_txt, pcb_doc):
        ref_comp = pcb_doc.FindComponent(ref_comp_txt)
        return ref_comp
    
    def get_ref_pin(self): # ref 컴포넌트의 선택한 net랑 연결되는 핀을 찾아야됨 
        for pin in self.net.com.Pins:
            if pin.Parent.Name == self.ref_comp.Name:
                return pin
        
    def trace_length(self, pin1, pin2, precision, pcb_doc):
        length = '-' # 해당 컴포넌트와 선택한 네트가 연결된게 없을 때
        via_spans_sum = 0
        to_see_objs = [] # 핀1, 트레이스, 핀2가 들어감 (나중에 레이어 번호를 기록하기 위해서 사용함)
        cnt = 0
        # 두 핀 사이의 객체들을 가져옵니다.
        if pin1 and pin2:
            to_see_objs.append(pin1)
            to_see_objs.append(pin2)
            objs = pcb_doc.ObjectsInBetween(pin1, pin2)
            cnt = objs.Count
            
        # 컬렉션이 비어 있으면 두 핀 사이에 물리적인 연결이 없음을 의미합니다.
        if cnt > 0:
            length = 0.0
            # 두 핀 사이의 모든 객체를 순회하며 길이를 합산합니다.
            for i in range(1, objs.Count + 1):  # VBScript의 1-based index를 고려
                obj = objs.Item(i)
                # 도체 층에 있는 객체인지 확인
                if obj.ObjectClass == 2:
                    # 객체가 트레이스인지 확인
                    if obj.Type == 524288:
                        to_see_objs.insert(-1, obj)
                        length += float(f"{obj.Length:.{precision+1}f}")
                        length = float(f"{length:.{precision+1}f}")
            via_spans_sum = self.net.layer_stackup._get_net_layers_list_objs(to_see_objs)
            
        if via_spans_sum:
            length += round(via_spans_sum, precision)

        if length != '-':
            length = round(length, precision)     
        return length  
        
    def set_props(self, net, ref_comp_txt, comp_set_txt, pcb_doc):
        self.net = net
        self.comp_set = self.get_comp_set(comp_set_txt, pcb_doc) # 아마도 얘네 둘 순서도 맞을거임 
        self.ref_comp = self.get_ref_comp(ref_comp_txt, pcb_doc)
        self.ref_pin = self.get_ref_pin()
        self.comp_pin_pair = self.get_comp_pin_pair()

    def set_comp_pin_pair(self, net):
        self.net = net
        self.ref_pin = self.get_ref_pin()
        self.comp_pin_pair = self.get_comp_pin_pair()

from pcb_event_handler import PCBEventHandler
from PyQt5.QtCore import QObject, pyqtSignal

class NetLengthCalculator(XpeditionManager, QObject):
    signal_to_gui = pyqtSignal() # pcb object -> GUI

    def __init__(self):
        # 부모 클래스 초기화
        XpeditionManager.__init__(self)  # XpeditionManager 초기화
        QObject.__init__(self)  # QObject 초기화

        self.initialize_pcb()
        self.set_event_handler(self.pcb_doc, PCBEventHandler)
        self.pcb_dispatched_event_com.signal_from_event_handler.connect(self.emit_to_gui) # event_handler -> pcb object
        self.comp_connection_cal = ComponentConnectionCalculator()

    def emit_to_gui(self):
        # PCB 앱 -> GUI에 전파
        self.signal_to_gui.emit()

    def _load_design_cm(self):
        self.design = self.constraints_auto.Design
        design_params = self.design.CreateDesignParams()
        design_params.ProjectFile = self.pcb_doc.Environment.ProjectFileFullName
        design_params.DesignContext = 2  # DC_Layout
        self.design.Load(design_params)

    def _unload_design_cm(self):
        self.design.UnLoad()

    def get_selected_nets(self):
        self._load_design_cm()
        selected_nets_com = self.pcb_doc.GetNets(1)
        if not selected_nets_com:
            print('please select nets')
        selected_nets = []

        for net_com in selected_nets_com:
            net = Net()
            net.set_props(net_com, self.design, self.pcb_doc)
            net.new_elect_net()
            net.set_elect_net_props(self.design, self.pcb_doc)
            selected_nets.append(net)
        self._unload_design_cm()
        return selected_nets
    
    def get_net_by_name(self, net_name):
        selected_nets = self.get_selected_nets()
        for net in selected_nets:
            if net_name == net.name:
                return net
    
    def get_connection_table(self): # 특정 넷 하나에 대해서만 한 줄 채우는 것
        temp = defaultdict(dict)
        for comp, pin in self.comp_connection_cal.comp_pin_pair:
            temp[comp.Name] = self.comp_connection_cal.trace_length(self.comp_connection_cal.ref_pin, pin, self.get_current_precision(), self.pcb_doc)
        temp = dict(temp)
        return temp

    def get_component_connection_length(self, net_name, component):
        connection_table = self.get_connection_table()
        return connection_table[net_name][component.Name]    

    def get_current_unit(self):
        current_unit = self.pcb_doc.CurrentUnit
        if current_unit == 2:
            return "mils"
        elif current_unit == 3:
            return "inch"
        elif current_unit == 4:
            return "mm"
        elif current_unit == 5:
            return "um"
    
    def get_current_precision(self):
        current_precision = self.pcb_doc.GetDimensionScheme().Precision
        return current_precision
        
    def get_nets_dic(self):
        selected_nets = self.get_selected_nets()
        nets_list = [net.to_dict() for net in selected_nets]
        return nets_list

    def get_nets_json(self):
        nets_list = self.get_nets_dic()
        return json.dumps(nets_list, indent=4, ensure_ascii=False)

def main():
    NetLengthCalculatorModel = NetLengthCalculator()
    result = NetLengthCalculatorModel.get_selected_nets()
    print(NetLengthCalculatorModel.get_nets_json())

def test():
    NetLengthCalculatorModel = NetLengthCalculator()
    selected_nets = NetLengthCalculatorModel.get_selected_nets()
    lengths = []
    print(NetLengthCalculatorModel.get_connection_table(selected_nets[0].name))

if __name__ == "__main__":
    # main()
    test()