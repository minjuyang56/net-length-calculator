Flow
![image](https://github.com/user-attachments/assets/98a0e445-0ce0-44cc-ba4c-cd381581066b)

main.py 실행시 아래와 같음 
![image](https://github.com/user-attachments/assets/ab0d0ab4-6ca4-427b-9602-6072ddef332d)

네트 객체 더블 클릭시 아래와 같음
![image](https://github.com/user-attachments/assets/3c35639f-6f1b-4e77-bf74-166956277615)

net_length_calculator/
├── calculator_model.py
├── calculator_view.py
├── pcb_event_handler.py
├── main.py
├── readme.md
└── sample.json


1217 화
-> GUI 토글 형태로 전부 구현 
-> Child net 클래스 따로 뺌, net 데이터 딕셔너리 형태 수정 (비즈니스 로직 수정)  
1218 수
-> extent 속성 구현 (트레이스의 좌표 나타내는 것)
-> Xpedition 앱이랑 연동해서 앱에서 네트 선택할 때 마다 재실행 없이 파이큐티에도 선택이 반영되도록 인터렉티브하게 구현
1220 금
-> 기준 네트와의 차이 길이를 드래그앤드랍으로 리포트하는 형식으로 GUI 구현함 
1227 금
-> cross probing 기능구현, 동시에 GUI 에서도 이벤트 받을 수 있음
