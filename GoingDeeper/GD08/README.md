# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 강지수
- 리뷰어 : 조영근


# PRT(Peer Review Template)
- [x]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - 문제 해결에 필요한 주요 단계가 노트북 안에 연결되어 있다.
    - 데이터셋을 정제하고 결과를 JSON으로 저장하며, SFT 모델을 학습하고, Reward Model의 ranking 데이터를 검증한 뒤, PPO를 시도하고 생성 결과와 평가 지표를 비교한다.
    - 따라서 특정 코드 조각만 제출된 것이 아니라 프로젝트 전체 흐름이 제출되어 있다.
    - <img width="469" height="457" alt="image" src="https://github.com/user-attachments/assets/5a7dd855-4d00-43d5-8184-4b6f44cd2d37" />
    <img width="486" height="465" alt="image" src="https://github.com/user-attachments/assets/4675611a-8b0c-4bd2-adea-cf32c4d8b1f5" />
    
- [x]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    - 핵심 로직에 함수화와 설명이 함께 적용되어 있다. 특히 데이터 품질 지표와 PPO의 정책·가치 함수 계산처럼 결과에 직접 영향을 주는 부분에 주석 또는 docstring이 있다.
    - <img width="475" height="498" alt="image" src="https://github.com/user-attachments/assets/bf8e9425-622b-4bee-b408-ea5e3b89fae9" />

- [x]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
    - 단순히 최종 결과만 제시하지 않고, 지표의 문제와 학습 불안정성을 발견한 뒤 원인을 추적하고 대안을 시도했다.
    - <img width="483" height="429" alt="image" src="https://github.com/user-attachments/assets/91fd923a-406b-4a84-886e-8432b0adc763" />
  
- [x]  **4. 회고를 잘 작성했나요?**
    - 회고가 단순 감상에 그치지 않고, 데이터 품질과 모델 품질을 구분하고, 각 실험 결과가 다음 실험에 어떻게 연결되었는지를 설명한다.
    - <img width="776" height="388" alt="image" src="https://github.com/user-attachments/assets/9c18d0b6-bc27-4d1c-99a6-77229a296cc3" />
    - 또한 전체 실행 플로우를 이해하는 데 도움이 되는 텍스트 기반 흐름도가 포함되어 있다.
    - <img width="754" height="547" alt="image" src="https://github.com/user-attachments/assets/6a5f5548-b31e-47ef-8f86-b5f0574296e8" />
    
- [x]  **5. 코드가 간결하고 효율적인가요?**
    - 코드 수준에서는 함수화와 방어적 검증이 잘 되어 있다.
    - <img width="538" height="366" alt="image" src="https://github.com/user-attachments/assets/4abe5c87-e792-45f2-a9ba-ee21467adc71" />

# 회고(참고 링크 및 코드 개선)
```
# 이번 리뷰에서 가장 인상적인 점은 실패한 PPO 실험을 결과에서 제거하지 않고, KL 폭주와 Value loss 발산을 수치로 남긴 부분이다.
# 모델 성능을 단일 지표로 판단하지 않고 AI 상투 응답 수, 한글 비율, 응답 길이, ROUGE-L, BLEU, chrF를 함께 비교한 점도 좋다.
# 특히 M2c를 선택하면서 BLEU와 chrF의 하락을 함께 기록한 것은 결과를 과장하지 않는 분석이다.
# 가장 큰 개선 포인트는 **최종 제출본의 압축과 구조화**다.
# 현재 노트북은 실험 과정이 풍부한 대신, 성공한 파이프라인과 실패한 탐색 과정이 한 파일 안에 연속적으로 쌓여 있다.
# 다음 버전에서는 첫 부분에 최종 실행 순서와 핵심 결과를 요약하고, 실패한 PPO 실험은 “디버깅 부록”으로 이동하면 평가자가 더 쉽게 프로젝트의 기여와 결론을 확인할 수 있다.
```
