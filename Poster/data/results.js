/* Transcribed from the supplied STAMPlus PDF, arXiv:2608.02791v1.
   Values are author-reported, not reproduced experiments. */
window.PAPER_DATA = {
  semantic: {
    source: 'Table VII(a), p.14',
    columns: ['방법 / backbone', 'ADE-150', 'PC-59', 'PAS-20', '평균'],
    rows: [
      ['ClearCLIP',16.7,35.9,80.9,44.5],['ProxyCLIP',24.2,39.6,83.3,49.0],
      ['MaskCLIP',23.7,45.9,null,null],['GroupViT',9.2,23.4,79.7,37.4],
      ['OVSeg',24.8,53.3,92.6,56.9],['SAN',27.5,53.8,94.0,58.4],
      ['LaSagnA / Vicuna-7B',14.3,46.1,69.8,43.4],['Text4Seg / Vicuna-7B',16.5,52.5,76.5,48.5],
      ['STAMPlus / Qwen2-2B',41.0,55.4,87.6,61.3],['STAMPlus / Qwen2-7B',42.2,56.9,92.1,63.7]
    ]
  },
  muse: {
    source: 'Table VII(b), p.14',
    columns: ['방법 / backbone', 'Val gIoU', 'Val cIoU', 'Test gIoU', 'Test cIoU', '평균'],
    rows: [
      ['LISA / Vicuna-7B',17.2,28.8,24.4,36.5,26.7],['GSVA / Vicuna-7B',38.9,40.9,44.3,54.1,44.6],
      ['PixelLM / Vicuna-7B',41.9,48.9,44.0,57.8,48.2],['POPEN / Vicuna-7B',45.4,55.2,46.4,62.9,52.5],
      ['Text4Seg++ / Qwen2-7B',70.4,57.7,63.2,63.8,63.8],
      ['STAMPlus / Qwen2-2B',59.1,58.6,63.4,64.1,61.3],['STAMPlus / Qwen2-7B',61.0,60.4,65.8,66.9,63.5]
    ]
  },
  ablation: [
    {name:'STAMP-2B · 기준',size:'896 × 896',iou:79.1,time:1.3,note:'시각 특징 융합, hybrid attention, SAM 후처리를 포함한 기준 설정.'},
    {name:'w/o A_hyb',size:'896 × 896',iou:76.2,time:1.3,note:'Hybrid attention을 제거하면 2.9점 하락. 마스크 토큰 사이의 양방향 상호작용이 중요하다.'},
    {name:'w/o E_mask',size:'896 × 896',iou:73.3,time:1.3,note:'시각적으로 강화된 마스크 임베딩을 제거하면 5.8점 하락. 각 패치의 시각 정보가 핵심 단서다.'},
    {name:'w/o SAM',size:'896 × 896',iou:75.3,time:0.9,note:'선택적 SAM 정제를 빼면 3.8점 하락하고 0.4초 단축. 마스크 자체는 SAM 없이 생성된다.'},
    {name:'STAMP-2B · 중간 해상도',size:'726 × 726',iou:78.6,time:1.1,note:'기준보다 cIoU 0.5점 낮고 0.2초 빠르다. 같은 모델의 입력 해상도를 낮춘 실험이다.'},
    {name:'STAMP-2B · 낮은 해상도',size:'504 × 504',iou:77.1,time:0.9,note:'기준보다 cIoU 2.0점 낮고 0.4초 빠르다. 속도와 정확도 사이의 선택을 보여준다.'},
    {name:'STAMP-7B',size:'896 × 896',iou:80.7,time:2.4,note:'모델 크기도 바뀌는 비교다. 2B 기준보다 1.6점 높지만 1.1초 더 걸린다.'}
  ],
  resolution: {
    source:'Table XI, p.16',
    columns:['마스크 토큰 수','RRSIS-D Acc@0.5','RRSIS-D gIoU','RRSIS-D cIoU','EarthReason gIoU','EarthReason cIoU'],
    rows:[['1024–1280',63.2,58.1,76.5,69.4,70.7],['2560–3200',71.0,63.6,81.5,74.3,71.2]]
  },
  reasoning: {
    source:'Table VIII(b), p.14',columns:['모델 / 모드','TextVQA','InfoVQA','POPE','DocVQA','평균'],
    rows:[['Qwen2-VL-2B / Direct',70.7,38.9,85.2,70.9,66.4],['STAMPlus-2B / Direct',70.6,40.2,85.4,71.3,66.9],['Qwen2-VL-2B / Look-twice',74.0,41.3,87.2,71.6,68.5],['STAMPlus-2B / Look-twice',74.7,46.3,87.5,75.7,71.1]]
  },
  dialogue: {
    source:'Table IX, p.15 · 발췌',columns:['모델 / 학습','MMMU','MMBench','MMStar','ScienceQA','TextVQA','VizWiz'],
    rows:[['Qwen2-VL-2B / VQA',38.3,66.5,42.1,70.2,70.7,60.3],['STAMP-2B / Mix',37.8,68.7,42.4,72.6,69.7,59.9],['STAMPlus-2B / Mix',39.3,68.9,42.9,74.4,70.6,59.2]]
  }
};
