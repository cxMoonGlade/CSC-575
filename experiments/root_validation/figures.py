"""Plot post-evaluation projection examples from saved interval predictions."""
import argparse, csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from chordrec.data import reduce_label

def intervals(path):
    with Path(path).open() as stream:
        values = [(float(r["start"]), float(r["end"]), reduce_label(r["label"])) for r in csv.DictReader(stream)]
    merged = []
    for start, end, label in values:
        if merged and merged[-1][2] == label and abs(merged[-1][1] - start) < 1e-9:
            merged[-1] = (merged[-1][0], end, label)
        else:
            merged.append((start, end, label))
    return merged

def cases(run,output,baseline):
 rows=list(csv.DictReader((run/'per_recording.csv').open()))
 by={}
 for r in rows:
  if r['decoder']=='viterbi' and r['method'] in [baseline,'projection']:
   by.setdefault(r['recording'],{})[r['method']]=r
 pairs=[]
 excluded=[]
 for name,metrics in by.items():
  if baseline in metrics and 'projection' in metrics:
   a,b=metrics['projection'],metrics[baseline]
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
  tracks=[('Reference',intervals(folder/'reference.csv')),(baseline,intervals(folder/f'{baseline}_viterbi.csv')),('Projection',intervals(folder/'projection_viterbi.csv'))]
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
  ax.set_yticks(range(3),['Long STFT' if t[0] == 'long' else t[0] for t in tracks],fontsize=7)
  ax.invert_yaxis();ax.set_xlim(0,duration);ax.tick_params(axis='x',labelsize=7)
  ax.set_title(f'{title}: {name}; projection − {baseline} = {100*delta:+.1f} pp',fontsize=8,loc='left')
  ax.set_xlabel('Time (s)',fontsize=7)
  evidence.append({'label':title,'recording':name,'split':a.get('split','external_fast'),'projection_accuracy':float(a['duration_accuracy']),'baseline_accuracy':float(b['duration_accuracy']),'delta':delta,'coverage':float(a['coverage'])})
 for ext in ['pdf','png']:fig.savefig(output/f'error_cases.{ext}',dpi=200)
 plt.close(fig)
 (output/'error_case_selection.json').write_text(json.dumps({'source_run':str(run.resolve()),'baseline':baseline,'rule':'Post-hoc illustrations: largest and smallest per-recording projection-minus-baseline duration accuracy differences; lexical tie break. Not representative random examples and not used to change the model.','comparable_recordings':len(pairs),'excluded_from_case_selection':excluded,'cases':evidence},indent=2)+'\n')
 print(json.dumps(evidence,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new figure directory")
    args.output.mkdir(parents=True)
    cases(args.run, args.output, "long")
