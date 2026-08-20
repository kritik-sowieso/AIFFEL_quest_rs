# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 강지수
- 리뷰어 : 조영근 


# PRT(Peer Review Template)
- [x]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - 한국어 문장 전처리, 중복·결측 정제, Train/Validation 분리, SentencePiece BPE 학습, 토큰화 및 패딩, PyTorch Dataset/DataLoader 구성, Teacher Forcing, Transformer 직접 구현, loss 계산, backward 및 optimizer step 점검, epoch 학습, validation, checkpoint 저장, 학습곡선 시각화, best checkpoint 로드, 한국어 응답 생성, 정성 평가까지 전체 실행 흐름이 포함되어 있다.
    - <img width="472" height="411" alt="image" src="https://github.com/user-attachments/assets/446b0078-d674-4025-9280-1f8b6de01a67" />
    - <img width="469" height="497" alt="image" src="https://github.com/user-attachments/assets/d4c54723-0fc6-463a-813a-de91d787e385" />

    
- [x]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    - 직접 구현한 Transformer와 Teacher Forcing을 이용한 학습부이다.
    - 해당 코드에는 Positional Encoding, Scaled Dot-Product Attention, Multi-Head Attention, Encoder Layer, Decoder Layer 등 구성요소별 구분 주석이 있고, 텐서 shape 변환을 [B,S,D] → [B,H,S,depth]와 같은 형태로 설명한다.
    - 또한 Teacher Forcing에서는 tgt_full[:, :-1]을 decoder 입력으로, tgt_full[:, 1:]을 label로 사용하는 과정을 별도 셀에서 출력하여 확인한다.
    - <img width="477" height="673" alt="image" src="https://github.com/user-attachments/assets/b5024834-0db7-429d-a856-37b7f73a5992" />

        
- [x]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
    - 학습이 실제로 가능한지 확인하기 위한 단계별 sanity check와 추가 분석이 충분히 수행되었다.
    - 먼저 token length 통계를 계산하여 MAX_LEN=20은 약 0.13%의 문장을 손실할 수 있고, MAX_LEN=32는 학습 문장을 모두 보존한다는 근거를 제시했다.
    - 또한 실제 한국어 batch에 대한 forward pass, logits shape 확인, Loss finite=True 확인, backward 후 gradient 개수·norm·finite 여부 확인, optimizer step 후 파라미터 변화량 확인을 차례로 수행했다.
    - <img width="467" height="532" alt="image" src="https://github.com/user-attachments/assets/48d704f1-7892-4dbe-a34f-fdbc7a59e111" />

        
- [x]  **4. 회고를 잘 작성했나요?**
    - 전처리에서 시작하여 SentencePiece, token IDs, padding, Teacher Forcing, encoder, decoder, vocabulary logits, loss 계산으로 이어지는 실행 플로우가 텍스트 흐름도로 정리되어 있다.
    - 또한 self-attention [64, 8, 31, 31]과 cross-attention [64, 8, 31, 32]의 각 차원이 무엇을 의미하는지 해석하여, 구현 결과를 단순 출력값이 아니라 모델 내부 동작과 연결했다.
    - 회고에서는 직접 Transformer를 구현하면서 Q/K/V projection, attention, mask, padding loss 처리를 이해하게 된 점을 설명하고, token accuracy가 완성 문장의 의미적 품질과 같지 않다는 한계도 명시한다.
    - 실제 validation 생성 결과에서 일부 응답은 자연스럽지만 일부는 질문과 관계가 약하거나 어색하다는 점도 확인할 수 있다.
    - 
    - <img width="765" height="385" alt="image" src="https://github.com/user-attachments/assets/211e7146-83b1-48bc-bc05-f8bc8c0d2b3f" />

        
- [x]  **5. 코드가 간결하고 효율적인가요?**
    - 전처리, 인코딩·패딩, Dataset, 학습, validation, 응답 생성이 함수로 분리되어 있으며, 학습과 validation에서 공통으로 사용되는 모델·criterion·DataLoader 구조가 명확하다.
    - ignore_index=PAD_ID, non_blocking=True, gradient clipping, best checkpoint 저장을 사용하여 불필요한 PAD loss와 gradient 폭주를 줄이려는 설계도 확인된다.
    - 학습과 평가에서 attention trace를 더 이상 사용하지 않을 때 del trace로 참조를 해제하는 점도 메모리 측면의 고려로 볼 수 있다.
    - <img width="482" height="683" alt="image" src="https://github.com/user-attachments/assets/ab3f8d20-7388-42b6-9ef1-26b38d4ac292" />



# 회고(참고 링크 및 코드 개선)
```
# 데이터 전처리부터 최종 응답 생성까지의 전체 pipeline을 단계별 출력과 함께 검증했다는 점
```
