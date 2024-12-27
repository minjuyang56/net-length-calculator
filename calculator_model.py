import json
from xpedition_manager import XpeditionManager

class Net:
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

    def _net_type_cm(self):
        net_type_cm = self.cm.ObjectType
        if net_type_cm == 47:  # OT_ElectricalNet (그냥 넷의 부모)
            return "OT_ElectricalNet"
        elif net_type_cm == 49:  # OT_Net
            return "OT_Net"
        elif net_type_cm == 26:  # OT_ConstraintClass (일렉넷의 부모)
            return "OT_ConstraintClass"
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

    def set_props(self, net_com, design_cm, pcb_doc):  
        self.name = net_com.Name
        self.com = net_com
        self.cm = design_cm.GetNets(15).Item(self.com.Name)
        self.type = self._net_type_cm()
        if self.type == "OT_ElectricalNet":  # 일렉넷이면 한번 더 가서 그냥 네트로 바꿔줌
            self.cm = self.cm.Objects.Item(1)
            self.type = self._net_type_cm()
        self.trace_length = self.get_trace_length()

        if self.trace_length:
            self.trace_extremas = self.get_trace_extrema()
            layer_stackup = LayerStackup()
            layer_stackup.set_props(pcb_doc)
            self.layer_gaps = layer_stackup.compute_layer_gap_between_traces([self.com])
        else:
            self.trace_length = 0
            self.layer_gaps = 0
        self.trace_per_layer = self.get_trace_per_layer()
        self.length = self.trace_length + self.layer_gaps
        # self.from_to = self.net_com.from_to
        # self.extent = (net_com.Extrema.MaxX, net_com.Extrema.MaxY), (net_com.Extrema.MinX, net_com.Extrema.MinY)

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
            layer_stackup = LayerStackup()
            layer_stackup.set_props(pcb_doc)
            self.elect_net.layer_gaps = layer_stackup.compute_layer_gap_between_traces(
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
    
class FromTO:
    def __init__(self):
        pass

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
        selected_nets = []

        for net_com in selected_nets_com:
            net = Net()
            net.set_props(net_com, self.design, self.pcb_doc)
            net.new_elect_net()
            net.set_elect_net_props(self.design, self.pcb_doc)
            selected_nets.append(net)
        self._unload_design_cm()
        return selected_nets

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
    

if __name__ == "__main__":
    main()