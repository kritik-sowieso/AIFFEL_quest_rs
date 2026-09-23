"""검수된 추가 실험 집계만 사용해 논문용 정적 그림을 만든다."""
import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--report',default='extension_v2/report/results.json')
    p.add_argument('--out',default='extension_v2/report/figures')
    a=p.parse_args()
    r=json.loads(Path(a.report).read_text())
    if r['status']['status']!='completed':raise ValueError('완료된 실측 결과가 필요합니다.')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors={'D':'#788c54','B':'#387b9c','C':'#b65a42','A':'#8795a1'}
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(8.2,3.1),layout='constrained')
    for c in ['D','B','C']:
        log=r['training'][c]['log']
        axes[0].plot([x['epoch'] for x in log],[x['main_loss'] for x in log],label=c,color=colors[c],marker='o',markersize=3)
        info=r['conditions'][c]
        axes[1].plot([5,10],[info[str(e)]['test']['overall']['coordinate_f1']*100 for e in [5,10]],label=c,color=colors[c],marker='o')
    axes[0].set(xlabel='Training epoch',ylabel='Conversion token loss',xticks=[1,5,10])
    axes[1].set(xlabel='Fixed checkpoint epoch',ylabel='Character-coordinate micro F1 (%)',xticks=[5,10],ylim=(0,100))
    for ax in axes:
        ax.legend(title='Condition',frameon=False)
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.2)
    fig.savefig(out/'training_and_layout.png',dpi=220)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(5.8,3.0),layout='constrained')
    labels=['A','D','B','C']
    info=[r['baseline_A_reused']['test']['overall']]+[r['conditions'][c]['10']['test']['overall'] for c in ['D','B','C']]
    for offset,key,label,color in [(-.18,'inventory_f1','Character inventory','#6c97aa'),(.18,'coordinate_f1','Character + coordinate','#c98768')]:
        ax.bar([i+offset for i in range(4)],[x[key]*100 for x in info],width=.36,label=label,color=color)
    ax.set(xticks=range(4),xticklabels=labels,ylabel='Micro F1 (%)',ylim=(0,100))
    ax.legend(frameon=False,fontsize=8)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(out/'ablation_f1.png',dpi=220)
    plt.close(fig)
    print('실측 결과 그림 저장:',out)

if __name__=='__main__':main()
