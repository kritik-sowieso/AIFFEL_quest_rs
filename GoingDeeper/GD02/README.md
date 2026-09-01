# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 강지수
- 리뷰어 : 김나연


# PRT(Peer Review Template)
- [X]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - KITTI 데이터셋 구조와 내용을 파악하고 이를 토대로 필요한 데이터셋 가공을 정상 진행하였다.
        - <img width="1057" height="180" alt="image" src="https://github.com/user-attachments/assets/ab642d5d-6081-4ba7-b902-a247ec62f2aa" />

    - 바운딩박스가 정확히 표시된 시각화된 이미지를 생성하였다.
        - <img width="1561" height="517" alt="image" src="https://github.com/user-attachments/assets/731e6166-ab4f-4ba5-85b5-84a11016accc" />

    - 테스트 수행결과 90% 이상의 정확도를 보였다.
        - <img width="730" height="427" alt="image" src="https://github.com/user-attachments/assets/1d388310-ca95-4288-82b6-7e5734a50c82" />

- [X]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    - 중간 중간 작성 해두신 코드의 흐름이 이해를 잘 돕고 있다.
        - <img width="1860" height="732" alt="image" src="https://github.com/user-attachments/assets/8cbdcd2a-aabf-40e1-b67e-789333058809" />
        - <img width="1013" height="375" alt="image" src="https://github.com/user-attachments/assets/0fbeaf19-3ad4-40e7-99fd-04863de61657" />
        - <img width="1446" height="227" alt="image" src="https://github.com/user-attachments/assets/d41942ca-9f67-40d3-aff1-593afc32c4ab" />

- [X]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
    - 1 Epoch로는 충분한 학습이 이루어지지 않았다는 판단과 함께 2 Epoch을 추가로 학습 시키는 해결 과정이 드러나있다.
        - <img width="1427" height="742" alt="image" src="https://github.com/user-attachments/assets/730372b3-5ed2-4d17-a054-a0a897533c82" />
        - <img width="1686" height="295" alt="image" src="https://github.com/user-attachments/assets/0bf2550e-0b38-480f-a9ef-d86236cc4e3d" />

- [X]  **4. 회고를 잘 작성했나요?**
    - 프로젝트의 결과를 분석하고 한계점을 파악하고 명시하였다.
        - <img width="1636" height="202" alt="image" src="https://github.com/user-attachments/assets/a6497677-49d2-4f3a-9915-bd94478de547" />

- [X]  **5. 코드가 간결하고 효율적인가요?**
    - 모델 학습을 위한 코드들을 함수와 클래스로 간결하고 효율적이게 작성하였다. 이 덕분에 training 코드가 간결해졌다.
        - <img width="538" height="751" alt="image" src="https://github.com/user-attachments/assets/463388be-8dbb-451e-96de-76aa877cac26" />

# 회고(참고 링크 및 코드 개선)
```
데이터를 확인하고 Go/Stop 기준을 그에 맞는 새로운 기준으로 세우신 점이 특별하게 다가왔습니다.

바운딩 박스를 검정색 말고 밝은 계열의 색상으로 표시하면 더 잘 보일 것 같습니다!
```
