# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 강지수
- 리뷰어 : 김시온


# PRT(Peer Review Template)
- [x]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - 문제에서 요구하는 최종 결과물이 첨부되었는지 확인
        - 중요! 해당 조건을 만족하는 부분을 캡쳐해 근거로 첨부

문제에서 요구하는 조건은 다음과 같다.

(1) 번역기 모델 학습에 필요한 텍스트 데이터 전처리가 한국어 포함하여 잘 이루어졌다.

(2) Attentional Seq2seq 모델이 정상적으로 구동된다.

(3) 테스트 결과 의미가 통하는 수준의 번역문이 생성되었다.


(1) 충족되었다.
<img width="457" height="345" alt="image" src="https://github.com/user-attachments/assets/3a0d30a5-adec-4388-ace4-391b9a99943f" />

(2) Training Loss가 안정적으로 감소하면서 학습이 되었음을 알 수 있다.
<img width="773" height="482" alt="image" src="https://github.com/user-attachments/assets/c5000819-670e-4b60-98e0-851fd88e5753" />


(3) 충족되었다.
<img width="768" height="260" alt="image" src="https://github.com/user-attachments/assets/7d16cea0-de59-492d-ab53-13b670914cb2" />


    
- [x]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    - 해당 코드 블럭을 왜 핵심적이라고 생각하는지 확인
    - 해당 코드 블럭에 doc string/annotation이 달려 있는지 확인
    - 해당 코드의 기능, 존재 이유, 작동 원리 등을 기술했는지 확인
    - 주석을 보고 코드 이해가 잘 되었는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
     
-> 사진과 같은 doc string을 작성하여 이해하는 것에 도움이 될 수 있도록 작성이 되어있다.

<img width="455" height="738" alt="image" src="https://github.com/user-attachments/assets/fa9acff8-65c7-4d3a-8dc1-0f77c43daf02" />

        
- [x]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
    - 문제 원인 및 해결 과정을 잘 기록하였는지 확인
    - 프로젝트 평가 기준에 더해 추가적으로 수행한 나만의 시도, 
    실험이 기록되어 있는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
     
-> 사진과 같은 텍스트로 코딩 과정 중간에 생긴 문제와 원인분석이 잘 작성되어있고 사진에는 나외있지 않지만 수정에 관해서도 잘 작성되어있고 충분한 추가실험을 수행하여 결과의 정확도에 신뢰성을 부여하였다.

<img width="505" height="273" alt="image" src="https://github.com/user-attachments/assets/9941bdc8-fe4c-4ead-858a-fb96c3595ba0" />


        
- [x]  **4. 회고를 잘 작성했나요?**
    - 주어진 문제를 해결하는 완성된 코드 내지 프로젝트 결과물에 대해
    배운점과 아쉬운점, 느낀점 등이 기록되어 있는지 확인
    - 전체 코드 실행 플로우를 그래프로 그려서 이해를 돕고 있는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부

-> 프로젝트 결과물에 대해 잘 정리해놓았고, 한계와 앞으로 해야할 일을 덧붙이면서 회고가 잘 작성되어있다.

<img width="775" height="305" alt="image" src="https://github.com/user-attachments/assets/9f4be80a-cebc-461a-8ca0-f753e09242cd" />

        
- [x]  **5. 코드가 간결하고 효율적인가요?**
    - 파이썬 스타일 가이드 (PEP8) 를 준수하였는지 확인
    - 코드 중복을 최소화하고 범용적으로 사용할 수 있도록 함수화/모듈화했는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부

-> 사진과 같이 함수로 간결하고 효율적이게 작성을 해놓았다고 본다.

<img width="236" height="232" alt="image" src="https://github.com/user-attachments/assets/2ebae637-b781-4fb8-a6c5-708e80527713" />


# 회고(참고 링크 및 코드 개선)
```
# 리뷰어의 회고를 작성합니다.
# 코드 리뷰 시 참고한 링크가 있다면 링크와 간략한 설명을 첨부합니다.
# 코드 리뷰를 통해 개선한 코드가 있다면 코드와 간략한 설명을 첨부합니다.
```
김시온 : 모든 조건에 만족하는 코드였다.
