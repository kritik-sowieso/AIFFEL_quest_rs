# STAMPlus — Multimodal Learning Poster

**MM(Multimodal)을 공부하기 위한 학습용 Poster**입니다. AIFFEL 리서처과정 19기에서 지금까지 학습한 **LLaVA, ViT, DETR, CLIP, SAM**을 연결하고, STAMPlus 논문의 핵심 원리와 실험을 figure·ablation study 중심으로 이해하기 위해 제작했습니다. 논문 저자와 독립적인 리뷰이며, 본 저장소에서 모델을 학습하거나 논문의 실험을 재현했다는 의미가 아닙니다.

시작 자료는 [첫 번째 포스터의 1페이지](https://docs.google.com/presentation/d/1uvqGAsxQ_BHBHBox1BRu7TvU0DsJp9fPcHiuwH_3Akk/edit?slide=id.p1#slide=id.p1)와 사용자가 제공한 `STAMPlus.pdf`입니다. 첫 포스터의 문제 설정·두 단계 파이프라인·손실함수·12개 범주 지연시간을 이어받고, 미완성 결과/논의 부분을 논문의 Figure 7, Tables VII–XI 등으로 보완했습니다. 파일에 포함된 편집용 문구는 사실 자료로 취급하지 않았습니다.

정확한 모델 표기는 **STAMPlus**입니다.

> **Define targets first. Predict their masks together.**
>
> 먼저 대상의 ID를 정하고, 모든 마스크를 함께 예측한다.

## 실행

정적 HTML/CSS/JavaScript 페이지입니다. 브라우저에서 `index.html`을 직접 열거나, 저장소 루트에서 아래 서버를 실행합니다. 브라우저 열람에는 Python 패키지 설치가 필요하지 않습니다.

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory Poster
```

[로컬 슬라이드 열기](http://127.0.0.1:8000)

서버를 끝내려면 `Ctrl+C`를 누릅니다. `Poster/` 전체를 일반 정적 호스팅의 공개 디렉터리에 복사해도 동작합니다. 저장소에 폴더를 추가하는 것만으로 GitHub Pages가 활성화되지는 않습니다. 이 변경은 Pages 설정이나 별도 호스팅을 자동으로 변경하지 않습니다.

- `←` / `→`, PageUp / PageDown: 이전·다음 슬라이드
- `Home` / `End`: 처음·끝으로 이동
- `O`: 목차 / `N`: 발표 노트 / `F`: 전체 화면
- `Esc`: 목차·그림 확대 닫기
- 모바일: 하단 이동 버튼 또는 좌우 스와이프. 내용이 긴 장은 세로 스크롤
- `#10`처럼 URL fragment로 특정 장을 바로 열기
- 모든 영상은 직접 재생합니다. 자동 재생·외부 폰트·CDN·분석 스크립트가 없습니다.

## 슬라이드 구성

| 장 | 내용 | 핵심 자료 |
| --- | --- | --- |
| 1 | 대상을 정의하고 함께 분할하기 | 첫 포스터 p.1, Abstract, Fig. 3/9 |
| 2 | 정확도·대화 능력·속도의 trilemma | Fig. 1–2, Table I |
| 3 | STAMP binary mask → STAMPlus ID map | Fig. 3 |
| 4 | 자기회귀 텍스트 + 병렬 mask prediction | Manim 영상, Fig. 2/4, §III-A |
| 5 | Single target / category / instance | Fig. 5 |
| 6 | 지시문별 ID 매핑 인터랙션 | 학습용 그리드, Manim 영상 |
| 7 | Text loss + mask loss | Eqs. (1)–(8) |
| 8 | 작은 대상·열린 어휘·인스턴스 예시 | Fig. 7 |
| 9 | Semantic / MUSE 정량 비교 | Table VII(a/b) |
| 10 | 구성요소 제거·해상도·모델 크기 비교 | **STAMP** Table X |
| 11 | 입력 해상도와 token budget 공동 확대 | **STAMPlus** Table XI |
| 12 | 다중 대상 추론 지연시간 | Abstract, Fig. 9 |
| 13 | Target cue, look-twice, 일반 VQA | Tables VIII–IX |
| 14 | ViT·CLIP·LLaVA·DETR·SAM 학습 연결 | 각 모델 원 논문 |
| 15 | 기여·한계·다음 질문·참고자료 | §III-B/IV-E 및 원 논문 |

## 논문의 주요 내용

**서지 정보:** Jiazhen Liu, Mingkuan Feng, Long Chen. *Better, Stronger, Faster, and Broader: Structured All-Mask Prediction for MLLM-Based Segmentation*. HKUST, [arXiv:2608.02791v1](https://arxiv.org/abs/2608.02791v1), 2026-08-03. 사용한 PDF는 18페이지 버전입니다. 원고의 `SUBMISSION` 표기를 그대로 존중하며 이 확장 논문의 게재 확정을 주장하지 않습니다. 원고는 STAMP 선행 연구가 CVPR 2026에 발표되었다고 설명합니다.

### 1. All-Mask Prediction

Phase 1에서 MLLM이 이미지와 질문을 보고 텍스트를 자기회귀적으로 생성합니다. 일반 vocabulary에 속한 `<SEG>` 토큰이 나오면 Phase 2로 전환합니다. 각 이미지 패치에 대응하는 `[MASK]` 토큰에 시각 특징과 위치 정보를 결합하고, Phase 1의 KV cache를 재사용합니다. 대화 영역은 causal attention, 마스크 영역은 bidirectional attention을 사용해 모든 패치 label을 한 번의 non-autoregressive forward pass로 예측합니다.

### 2. STAMP에서 STAMPlus로

STAMP는 binary foreground/background mask를 만듭니다. STAMPlus는 먼저 `{"cls": ID, "label": object}` 형태의 구조화된 대상 목록을 생성하고, 필요할 때 `bbox`를 추가합니다. 이 ID를 shared multi-class mask의 출력 채널 의미에 연결합니다. 0은 배경이며, 양수 ID의 의미는 해당 이미지와 지시문에 따라 동적으로 정해집니다.

동일 이름의 인스턴스도 별도 ID로 구분할 수 있습니다. 구현상 head 용량은 배경 포함 200개입니다. 199개보다 많은 target entry를 가진 샘플은 전처리에서 제외하거나 절단하며, 평가 샘플은 이 용량을 넘지 않았다고 보고합니다. 고정된 200개 의미 범주를 분류하는 모델이라는 뜻은 아닙니다.

### 3. 학습 목적함수

두 모델의 공통 목적함수는 `L = L_text + L_mask`입니다.

- STAMP: `L_mask = BCE + Dice`.
- STAMPlus: `L_mask = multi-class CE + class-wise Dice`.
- 대상 목록은 기존 text loss로 학습하며 별도의 ID 생성 loss를 추가하지 않습니다.
- 학습에서는 GT 대상 목록의 ID를, 추론에서는 모델이 생성한 ID를 패치 label에 연결합니다.

### 4. 핵심 실험과 해석

| 근거 | 저자 보고 수치 | 해석의 범위 |
| --- | --- | --- |
| Table X | STAMP-2B 기준 cIoU 79.1 / 1.3s; w/o A_hyb 76.2; w/o E_mask 73.3 | 공유 All-Mask 기반에 대한 **STAMP** ablation. 각각 −2.9, −5.8점 |
| Table X | w/o SAM 75.3 / 0.9s | 기본 마스크는 외부 decoder 없이 생성 가능. 선택적 SAM 정제는 정확도와 시간을 함께 바꿈 |
| Table X | 726²: 78.6 / 1.1s; 504²: 77.1 / 0.9s; 7B/896²: 80.7 / 2.4s | 해상도·모델 크기와 정확도/지연시간의 관계. 단일 A800 측정 |
| Table XI | RRSIS-D gIoU 58.1→63.6; EarthReason gIoU 69.4→74.3 | 동일 STAMPlus-2B checkpoint·평가 이미지에서 **입력 해상도와 token budget을 함께** 증가 |
| Table VII(a) | STAMPlus-7B 평균 mIoU 63.7 | 세 데이터셋 평균은 표에서 최고. PAS-20은 SAN 94.0이 STAMPlus 92.1보다 높음 |
| Table VII(b) | STAMPlus-7B MUSE 평균 63.5; Text4Seg++ 63.8 | Test gIoU/cIoU는 STAMPlus가 높지만 전체 평균에서는 앞서지 않음 |
| Abstract / Fig. 9 | 12 categories: repeated STAMP 13.50s → STAMPlus 5.16s | 단일 H800, 동일 해상도·image buckets. 보고값 계산 시 약 2.62배 속도비, 61.8% 시간 감소 |
| Table VIII(a) | STAMPlus-2B 평균 cIoU 77.4→89.1 | **사람이 target box를 추가 제공**한 조건. 완전 자동 성능 향상으로 해석하지 않음 |
| Table VIII(b) | Look-twice 평균: Qwen2-VL-2B 68.5, STAMPlus-2B 71.1 | 동일 추론 모드 비교에서 +2.6점. STAMPlus 자체 Direct 66.9 대비는 +4.2점 |
| Table IX | VQA 유지·개선 및 일부 하락 | 일반 대화 능력 보존은 해당 benchmark 범위의 근거이며 모든 능력/지표의 향상을 의미하지 않음 |

`O(1)`은 대상 수에 대한 **Phase 2 마스크 생성 패스 수**를 뜻합니다. Phase 1은 대상 목록을 순차 생성하므로 전체 실행시간은 여전히 늘어납니다. 고해상도 입력도 계산량·메모리 비용을 늘립니다. Fig. 9의 H800 측정과 Table X의 A800 측정을 같은 조건처럼 합치지 않습니다.

gIoU는 샘플별 IoU를 평균하고, cIoU는 전체 교집합과 합집합을 합산합니다. mIoU는 클래스별 IoU의 평균입니다. 서로 다른 평균 정의와 데이터셋을 하나의 지표처럼 비교하지 않습니다.

## 지금까지의 학습과 연결

이 표는 **학습 개념의 연결**입니다. 다섯 모델이 모두 STAMPlus의 내부 모듈이라는 뜻은 아닙니다.

| 학습 모델 | 핵심 개념 | STAMPlus를 읽는 질문 |
| --- | --- | --- |
| [ViT](https://arxiv.org/abs/2010.11929) | 이미지 패치를 Transformer 토큰으로 표현 | 작은 대상이 적은 패치로 표현되면 무엇을 잃을까? |
| [CLIP](https://arxiv.org/abs/2103.00020) | 이미지–텍스트 대조 학습과 의미 정렬 | 무엇인지 아는 것과 경계까지 아는 것은 어떻게 다른가? |
| [LLaVA](https://arxiv.org/abs/2304.08485) | Vision encoder와 LLM 연결, visual instruction tuning | 이미지 대화 능력을 유지하며 dense output을 추가할 수 있을까? |
| [DETR](https://arxiv.org/abs/2005.12872) | Object query, set prediction, bipartite matching | 객체 단위 query와 패치 단위 mask token의 차이는 무엇인가? |
| [SAM](https://arxiv.org/abs/2304.02643) | Promptable segmentation, 점·box에서 mask 생성 | 자체 mask 생성과 선택적 외부 정제는 어떻게 구별되는가? |

주력 backbone은 Qwen2-VL입니다. LLaVA(Vicuna-7B)로 옮긴 실험은 Table II에서 평균 RefCOCO-family cIoU 77.0을 보고합니다. DETR의 matching loss를 사용한다고 설명하지 않으며, CLIP 자체를 pixel-mask 생성기로 설명하지 않습니다.

## Manim 영상 재생성

브라우저는 이미 렌더링한 MP4를 재생합니다. **[Manim Community](https://github.com/ManimCommunity/manim)**는 Python 기반 영상 제작에 실제로 사용했으며 HTML 안에서 직접 Python을 실행하지 않습니다.

```bash
cd Poster
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/render_animations.py
```

Manim 0.19.0과 Python 3.12에서 렌더링을 확인했습니다. 환경에 따라 Cairo/Pango 등 native 라이브러리와 `ffmpeg`가 필요합니다. 설치 방법은 [공식 문서](https://docs.manim.community/en/stable/installation.html)를 참고하세요. `Text`를 사용하므로 이 두 장면은 LaTeX 설치가 필요하지 않습니다.

- `AllMaskPrediction`: 순차적 mask token 생성과 All-Mask 병렬 예측의 개념 비교.
- `StructuredIDs`: 대상 목록의 ID가 shared label map으로 연결되는 과정.
- 결과: `assets/videos/*.mp4`와 포스터 이미지 `*.jpg`, 1280×720 / 30fps.
- 영상 속 속도·패치 수·공간 배치는 학습용 예시입니다. 실제 모델 출력이나 benchmark 영상이 아닙니다.

## Figure·데이터 출처와 재생성

`assets/figures/`는 제공된 원본 논문에서 추출한 Fig. 3, 5, 7, 9 및 Fig. 3의 결과 부분입니다. 각 figure의 출처·저자 권리는 원 논문에 귀속됩니다. 원본 PDF 전체와 Google Slides 파일은 저장소에 복사하지 않았습니다. 이 자료는 비평·설명을 위한 학습용이며 원저자의 endorsement를 의미하지 않습니다.

```bash
# Poppler(pdftoppm)와 Pillow 필요
python scripts/extract_figures.py /path/to/STAMPlus.pdf
```

추출 좌표는 원본 18페이지 v1을 기준으로 스크립트에 기록했습니다. 다른 버전은 그림 위치가 달라질 수 있습니다. 원본 figure는 크기와 crop만 조정했고, 수치와 예측 결과를 재작성하지 않았습니다. Table VII–XI의 선택 수치는 `data/results.js`에 출처와 함께 전사했습니다. 각 표 아래에 데이터셋·split·metric·하드웨어 조건을 표시합니다. Fig. 9 중간 점을 임의로 수치화하지 않았습니다.

## 파일 구조

```text
Poster/
├── index.html                 # 한국어 슬라이드 15장
├── styles.css                 # 데스크톱·모바일·인쇄 스타일
├── app.js                     # 탐색·목차·확대·표·설명용 그리드
├── data/results.js            # 논문 표의 수치
├── assets/figures/            # 출처를 표시한 논문 figure
├── assets/videos/             # 실제 Manim 렌더링 영상 + poster JPG
├── manim_scenes/stamplus.py   # 재현 가능한 Manim 장면
├── scripts/extract_figures.py
├── scripts/render_animations.py
├── scripts/check_assets.py   # 로컬 리소스·구조 검사
└── requirements.txt
```

```bash
python3 Poster/scripts/check_assets.py
node --check Poster/app.js
node --check Poster/data/results.js
```

## 다음 학습 질문

1. Phase 1이 대상을 누락하거나 ID를 잘못 지정하면 Phase 2는 어떻게 영향을 받을까?
2. 사람이 제공하는 box 없이도 target cue 품질을 높이는 방법은 무엇일까?
3. 해상도·mask token 수·latency·메모리를 같은 조건에서 비교하면 어떤 trade-off가 보일까?
4. DETR의 객체 집합 예측과 STAMPlus의 패치 label 예측은 오류의 형태가 어떻게 다를까?
5. “decoder-free”라는 구조적 설명과 최종 보고 수치의 SAM 후처리 설정을 어떻게 함께 기록할까?
