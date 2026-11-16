"""Create a pipeline diagram and illustrative cases from saved results.

Cases are selected after evaluation from a completed run. The caller specifies
the baseline previously selected on the development set.
"""
import argparse,csv,json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from .data import reduce_label


def intervals(path):
 with Path(path).open() as f:
  return [(float(r['start']),float(r['end']),reduce_label(r['label'])) for r in csv.DictReader(f)]


def pipeline(output):
 # One-column layout; labels retain the report's existing terminology.
 fig,ax=plt.subplots(figsize=(3.4,2.2),layout='constrained')
 ax.set(xlim=(0,4),ylim=(0,5.1));ax.axis('off')
 boxes=[(.25,4.35,3.5,.55,'Audio: mono, 22.05 kHz'),
        (.05,3.15,1.8,.75,'Short STFT\n2,048 samples'),
        (2.15,3.15,1.8,.75,'Long STFT\n8,192 samples'),
        (.4,2.15,3.2,.55,'Chroma fusion: fixed or adaptive'),
        (.4,1.15,3.2,.55,'24 triad scores and N rule'),
        (.85,.15,2.3,.55,'Shared Viterbi decoder')]
 for x,y,w,h,label in boxes:
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02',facecolor='#edf3f8',edgecolor='#486579',linewidth=.7))
  ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=8)
 arrows=[((1.3,4.33),(.95,3.92)),((2.7,4.33),(3.05,3.92)),
         ((.95,3.13),(1.3,2.72)),((3.05,3.13),(2.7,2.72)),
         ((2,2.13),(2,1.72)),((2,1.13),(2,.72))]
 for a,b in arrows:
  ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':.7,'color':'#334455'})
 for ext in ['pdf','png']:
  fig.savefig(output/f'pipeline.{ext}',dpi=200)
  fig.savefig(output/f'pipeline_column.{ext}',dpi=200)
 plt.close(fig)


def cases(run,output,baseline):
 rows=list(csv.DictReader((run/'per_recording.csv').open()))
 by={}
 for r in rows:
  if r['decoder']=='viterbi' and r['method'] in [baseline,'adaptive']:
   by.setdefault(r['recording'],{})[r['method']]=r
 pairs=[]
 excluded=[]
 for name,metrics in by.items():
  if baseline in metrics and 'adaptive' in metrics:
   a,b=metrics['adaptive'],metrics[baseline]
   scoreable=[float(r['scoreable_seconds']) for r in [a,b]]
   if min(scoreable)<=0:
    excluded.append({'recording':name,'reason':'No scoreable reference duration; omitted only from illustrative case selection.','scoreable_seconds':scoreable})
    continue
   if not a['duration_accuracy'].strip() or not b['duration_accuracy'].strip():
    raise ValueError(f'Missing accuracy despite positive scoreable duration: {name}')
   pairs.append((float(a['duration_accuracy'])-float(b['duration_accuracy']),name,a,b))
 if not pairs:raise ValueError('No comparable saved recording results')
 pairs.sort(key=lambda v:(v[0],v[1]))
 selected=[('Largest increase',pairs[-1]),('Largest decrease',pairs[0])]
 if pairs[-1][0]<=0:selected[0]=('Smallest decrease',pairs[-1])
 if pairs[0][0]>=0:selected[1]=('Smallest increase',pairs[0])
 fig,axes=plt.subplots(2,1,figsize=(7.1,2.9),layout='constrained')
 roots=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
 cmap=plt.get_cmap('tab20')
 evidence=[]
 for ax,(title,(delta,name,a,b)) in zip(axes,selected):
  folder=run/'predictions'/name
  tracks=[('Reference',intervals(folder/'reference.csv')),(baseline,intervals(folder/f'{baseline}_viterbi.csv')),('Adaptive',intervals(folder/'adaptive_viterbi.csv'))]
  duration=float(a['audio_seconds'])
  for y,(track,values) in enumerate(tracks):
   for start,end,label in values:
    if label is None or label=='N':color='#eee';hatch='xx' if label is None else None
    else:
     color=cmap(roots.index(label.split(':')[0])/12)
     hatch='//' if label.endswith(':min') else None
    ax.broken_barh([(start,end-start)],(y-.35,.7),facecolors=color,edgecolors='#555',linewidth=.25,hatch=hatch)
    if end-start>duration/15:
     text='X' if label is None else label.replace(':maj','').replace(':min','m')
     ax.text((start+end)/2,y,text,fontsize=6,ha='center',va='center')
  ax.set_yticks(range(3),[t[0] for t in tracks],fontsize=7)
  ax.invert_yaxis();ax.set_xlim(0,duration);ax.tick_params(axis='x',labelsize=7)
  ax.set_title(f'{title}: {name}; adaptive − {baseline} = {100*delta:+.1f} pp',fontsize=8,loc='left')
  ax.set_xlabel('Time (s)',fontsize=7)
  evidence.append({'label':title,'recording':name,'split':a['split'],'adaptive_accuracy':float(a['duration_accuracy']),'baseline_accuracy':float(b['duration_accuracy']),'delta':delta,'coverage':float(a['coverage'])})
 for ext in ['pdf','png']:fig.savefig(output/f'error_cases.{ext}',dpi=200)
 plt.close(fig)
 (output/'error_case_selection.json').write_text(json.dumps({'source_run':str(run.resolve()),'baseline':baseline,'rule':'Post-hoc illustrations: largest and smallest per-recording adaptive-minus-baseline duration accuracy differences; lexical tie break. Not representative random examples and not used to change the model.','comparable_recordings':len(pairs),'excluded_from_case_selection':excluded,'cases':evidence},indent=2)+'\n')
 print(json.dumps(evidence,indent=2))


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--run',type=Path)
 parser.add_argument('--baseline',choices=['short','long','cqt','equal','fixed'])
 args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 pipeline(args.output)
 if args.run:
  if args.baseline is None:parser.error('--baseline must be selected on development data')
  cases(args.run,args.output,args.baseline)
