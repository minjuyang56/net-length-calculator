import math
from collections import Counter
# 이거는 특정 네트와 그 네트가 지나가는 컴포넌트들의 연결 정보를를 계산하는 클래스
# 기준 컴포넌트 ~ 컴포넌트1 길이
# 기준 컴포넌트 ~ 컴포넌트2 길이
# 기준 컴포넌트 ~ 컴포넌트3 길이
# 기준 컴포넌트 ~ 컴포넌트4 길이
# 이런것 계산해줌

# 속성은 딱 5개 
# 네트, 기준 컴포넌트, 기준 핀, 컴포넌트 세트, 컴포넌트세트-핀(페어), 

class ComponentConnectionCalculator:
    def __init__(self):
        self.net = None
        self.ref_comp = None
        self.ref_pin = None
        self.comp_set = []
        self.comp_pin_pair = []

    def _get_pin_str(self):
        if not self.comp_set:
            return 
        
        counter = Counter([pin.Name for pin in self.net.com.Pins])

        # comp_set의 개수와 일치하는 개수의 핀을 찾기
        pin_str = [key for key, value in counter.items() if value == len(self.comp_set)]
        try:
            return pin_str[0]
        except Exception as e:
            print('invalid Topology, you have to chose Daysy chain shape')
            return None

    def get_comp_pin_pair(self):
        comp_pin_pair = []
        for comp in self.comp_set:
            comp_pin_pair.append((comp, comp.FindPin(self._get_pin_str())))
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
        
    def trace_length(self, pin1, pin2, pcb_doc):
        length = 0.0
        # 두 핀 사이의 객체들을 가져옵니다.
        objs = pcb_doc.ObjectsInBetween(pin1, pin2)
        # 컬렉션이 비어 있으면 두 핀 사이에 물리적인 연결이 없음을 의미합니다.
        if objs.Count > 0:
            # 두 핀 사이의 모든 객체를 순회하며 길이를 합산합니다.
            for i in range(1, objs.Count + 1):  # VBScript의 1-based index를 고려
                obj = objs.Item(i)
                # 도체 층에 있는 객체인지 확인
                if obj.ObjectClass == 2:
                    # 객체가 트레이스인지 확인
                    if obj.Type == 524288:
                        length += round(obj.Length, 2)
        return length

        
    def set_props(self, net, ref_comp_txt, comp_set_txt, pcb_doc):
        self.net = net
        self.comp_set = self.get_comp_set(comp_set_txt, pcb_doc) # 아마도 얘네 둘 순서도 맞을거임 
        self.ref_comp = self.get_ref_comp(ref_comp_txt, pcb_doc)
        self.comp_pin_pair = self.get_comp_pin_pair()
        self.ref_pin = self.get_ref_pin()