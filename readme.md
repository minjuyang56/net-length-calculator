# Net Length Calculator

## 프로젝트 개요

이 프로젝트는 PCB 설계에서 기준 컴포넌트에서 특정 컴포넌트까지의 네트(Trace)의 길이를 계산하고 시각화하는 도구입니다. 
`daisy_chain_length_main.py`를 실행하여 GUI 환경에서 트레이스의 길이를 측정하고 비교할 수 있으며, Xpedition 앱과의 연동을 통해 실시간으로 네트를 선택하고 반영할 수 있습니다.

## 프로젝트 구조
<img src="https://github.com/user-attachments/assets/76bb436c-2e2e-46cd-a7d5-413be9c67d21"  width="200"/>

### 1. 프로젝트 실행 흐름
<img src="https://github.com/user-attachments/assets/98a0e445-0ce0-44cc-ba4c-cd381581066b" width="500" />

### 2. `daisy_chain_length_main.py` 실행 시 화면
<img src="https://github.com/user-attachments/assets/71d4afc8-7670-4704-ac07-74fb477e74cf" width="500" />

### 3. Component Setting 버튼 실행 시 화면
<img src="https://github.com/user-attachments/assets/6da82628-f87b-4fee-8fef-c9a3eea40527" width="500" />

### 4. 네트 객체 더블 클릭 시 Ref Net 결정 화면
<img src="https://github.com/user-attachments/assets/9b7c913f-4ba5-4c2c-adbd-fe5c8b2aa07e" width="500"/>

### 5. Difference 토글 활성화 시 화면
<img src="https://github.com/user-attachments/assets/126edd82-8477-4aa1-a778-efd88f524166" width="500" />

## 사용 방법

1. `daisy_chain_length_main.py`를 실행하여 GUI를 엽니다.
2. Xpedition에서 네트를 선택하면, 해당 네트가 파이큐티에도 반영됩니다.
3. 확인할 Net들이 결정되었다면 Fix Net 토글을 활성화합니다. 
4. Component Setting 버튼을 클릭하여 Ref Component와 목적지 Component Set를 지정합니다.
5. 네트를 더블클릭하여 Ref Net을 지정합니다.   
6. Difference 토글을 활성화하여 기준네트 대비 다른 네트들의 구간 별 difference를 알 수 있습니다.
7. PCB 앱에서 네트 length 수정후 Viewer의 Update 버튼을 눌러, 수정 내용을 반영합니다.
8. 계산된 길이와 차이를 리포트 형식으로 제공하여, 사용자에게 직관적인 결과를 제공합니다.

## 참고 사항

- 이 프로젝트는 **Python 3.x** 환경에서 실행됩니다.
- **Xpedition** 앱과 연동되므로, 해당 앱이 설치되어 있어야 정상적으로 동작합니다.
