# Net Length Calculator

## 프로젝트 개요

이 프로젝트는 PCB 설계에서 네트(Trace)의 길이를 계산하고 시각화하는 도구입니다. `main.py`를 실행하여 GUI 환경에서 트레이스의 길이를 측정하고 비교할 수 있으며, Xpedition 앱과의 연동을 통해 실시간으로 네트를 선택하고 반영할 수 있습니다.
\n
## 프로젝트 구조
<img src="https://github.com/user-attachments/assets/76bb436c-2e2e-46cd-a7d5-413be9c67d21"  width="200" height="400"/>

### 1. 프로젝트 실행 흐름
<img src="https://github.com/user-attachments/assets/98a0e445-0ce0-44cc-ba4c-cd381581066b" width="600" height="400"/>

### 2. `main.py` 실행 시 화면
<img src="https://github.com/user-attachments/assets/ab0d0ab4-6ca4-427b-9602-6072ddef332d" width="500" height="300"/>

### 3. 네트 객체 더블 클릭 시 화면
<img src="https://github.com/user-attachments/assets/3c35639f-6f1b-4e77-bf74-166956277615" width="400" height="200"/>

## 사용 방법

1. `main.py`를 실행하여 GUI를 엽니다.
2. Xpedition에서 네트를 선택하면, 해당 네트가 파이큐티에도 반영됩니다.
3. 네트를 더블 클릭하여 상세 정보를 확인하고, 필요한 길이 정보를 계산할 수 있습니다.
4. 계산된 길이와 차이를 리포트 형식으로 제공하여, 사용자에게 직관적인 결과를 제공합니다.

## 참고 사항

- 이 프로젝트는 **Python 3.x** 환경에서 실행됩니다.
- **Xpedition** 앱과 연동되므로, 해당 앱이 설치되어 있어야 정상적으로 동작합니다.



### Etc...

 12월 17일 (화요일)
- **GUI 토글 형태 구현**: 전체 GUI 구조를 토글 형식으로 구현하여 사용자가 쉽게 조작할 수 있도록 개선.
- **Child Net 클래스 분리**: 기존 네트 데이터를 딕셔너리 형태로 수정하고, `Child Net` 클래스를 별도로 분리하여 코드의 가독성과 유지보수성을 향상시킴.

 12월 18일 (수요일)
- **Extent 속성 구현**: 트레이스의 좌표를 나타내는 `extent` 속성을 추가하여, 네트의 위치 및 범위를 시각적으로 확인할 수 있도록 함.
- **Xpedition 앱과의 연동**: Xpedition에서 네트를 선택할 때마다 PyQt에서도 선택된 네트가 즉시 반영되도록 하여, 실시간 인터렉티브한 상호작용을 구현.

 12월 20일 (금요일)
- **기준 네트와의 차이 길이 리포트**: 드래그 앤 드랍 형식으로 GUI에 리포트 기능을 구현하여, 기준 네트와의 차이를 직관적으로 비교하고 확인할 수 있도록 함.

 12월 27일 (금요일)
- **Cross Probing 기능 구현**: Xpedition과 PyQt 간에 크로스 프로빙 기능을 추가하여, 실시간으로 데이터를 교차 확인할 수 있도록 함. GUI에서도 동시에 이벤트를 받을 수 있게 하여, 상호작용의 효율성을 높임.
