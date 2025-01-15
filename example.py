import os
import win32com.client

# 로그 파일 경로 및 열기
log_file_path = "logfile.txt"
log_file = open(log_file_path, "w")

# COM 객체 초기화
app = win32com.client.Dispatch("Your.Application.Name")
tky_layers = app.Layers  # 레이어 컬렉션
nets_coll = app.Nets  # 네트 컬렉션

# 초기화
tky_layers_array = {}
pf_copper_layers_array = {}

# 1. 레이어 두께 저장
for i in range(tky_layers.Count - 1, 1, -1):
    tky_layer = tky_layers.Item(i)
    if tky_layer.Type == 3:  # Insulation
        tky_layers_array[(i - 1) // 2] = tky_layer.LayerProperties.Thickness
    elif tky_layer.Type == 0:  # Conductor
        pf_copper_layers_array[i // 2] = tky_layer.LayerProperties.Thickness

# 2. 각 네트에 대해 처리
for net in nets_coll:
    total_seg_length = 0  # 초기화
    net_name = net.Name
    net_vias = net.Vias  # 비아 컬렉션
    seg_coll = net.Traces  # 트레이스 컬렉션

    seg_coll_count = seg_coll.Count
    via_count = net_vias.Count

    log_file.write(f"Net: {net_name}   Segments: {seg_coll_count}   Vias: {via_count}\n")

    # 비아 스팬 카운트
    dict_via_spans = {}
    for net_via in net_vias:
        str_viaspan = f"{net_via.StartLayer}-{net_via.EndLayer}"
        dict_via_spans[str_viaspan] = dict_via_spans.get(str_viaspan, 0) + 1

    # 비아 스팬 기록
    for str_viaspan, count in dict_via_spans.items():
        log_file.write(f"Via: {str_viaspan} ; Count: {count}\n")
    log_file.write("\n")

    # 트레이스 길이 및 비아 처리
    tky_flag = 0
    tky_layer_change = 0
    sum_seg_len = 0
    tky_trace_no_vias = total_seg_length

    for seg in seg_coll:
        seg_len = seg.Length
        tky_seg_layer = seg.Layer

        if tky_flag == 1:
            # 레이어 변환 처리 (비아 두께 계산)
            if tky_seg_layer != tky_seg_layer_prev:
                log_file.write("       Vias: ")
                via_length = 0
                vias_spans = 0

                if tky_seg_layer < tky_seg_layer_prev:
                    layer_range = range(tky_seg_layer, tky_seg_layer_prev)
                else:
                    layer_range = range(tky_seg_layer - 1, tky_seg_layer_prev - 1, -1)

                for i in layer_range:
                    vias_spans += 1
                    via_length += tky_layers_array.get(i, 0)
                    if vias_spans > 1:
                        via_length += pf_copper_layers_array.get(i, 0)

                if vias_spans > 1:
                    log_file.write(f"[ {via_length} ] with {vias_spans - 1} Conductor layers\n")
                else:
                    log_file.write(f"[ {via_length} ] , no Conductor layers\n")

                tky_layer_change += 1

        tky_seg_layer_prev = tky_seg_layer
        tky_flag = 1
        sum_seg_len += seg_len
        log_file.write(f" Segment Layer: {tky_seg_layer}   Segment Length: {seg_len:.2f} [ {sum_seg_len:.2f} ]\n")

    # 총 비아 길이 계산
    tky_vias_length = total_seg_length - tky_trace_no_vias
    log_file.write(f"   Trace length (no vias): {tky_trace_no_vias:.2f}   "
                   f"Trace length (incl vias): {total_seg_length:.2f}   "
                   f"Vias length: {tky_vias_length:.2f}\n\n")

# 로그 파일 닫기
log_file.close()