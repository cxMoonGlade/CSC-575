"""Inspect saved chord predictions with audio and reference coverage."""
from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import math
from pathlib import Path
import wave

from .data import reduce_label

ATTRIBUTIONS = {
    'idmt': {
        'dataset': 'IDMT-SMT-Guitar, subset 4',
        'creators': 'Christian Kehling, Andreas Männchen, and Arndt Eppler',
        'url': 'https://zenodo.org/records/7544110',
        'license': 'CC BY-NC-ND 4.0',
        'license_url': 'https://creativecommons.org/licenses/by-nc-nd/4.0/',
        'nc_note': 'Source NC is mapped to N for evaluation. The dataset guide does not define NC; listen before interpreting it as silence.',
    },
    'guitarset': {
        'dataset': 'GuitarSet v1.1.0',
        'creators': 'Qingyang Xi, Rachel M. Bittner, Johan Pauwels, Xuzhou Ye, and Juan Pablo Bello',
        'url': 'https://zenodo.org/records/3371780',
        'license': 'CC BY 4.0',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'nc_note': 'N denotes the no-chord class. Unsupported reference labels and unannotated audio are excluded from scoring.',
    },
}


def load_intervals(path):
    """Read the interval CSV files written by the experiment runners."""
    with Path(path).open(newline='') as source:
        return [(float(row['start']), float(row['end']), row['label'])
                for row in csv.DictReader(source)]


def _validated(intervals, duration):
    previous_end = 0.0
    result = []
    for start, end, label in intervals:
        start, end = float(start), float(end)
        if (not math.isfinite(start) or not math.isfinite(end)
                or start < previous_end - 1e-8 or end <= start
                or end > duration + 1e-8 or not isinstance(label, str)):
            raise ValueError('Intervals must be ordered, disjoint, and inside the audio')
        start, end = max(0.0, start), min(duration, end)
        result.append((start, end, label))
        previous_end = end
    return result


def coverage_intervals(reference, duration):
    """Separate scored chords, N, unsupported labels, and annotation gaps."""
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Audio duration must be positive and finite')
    result = []
    end = 0.0
    for start, stop, label in _validated(reference, duration):
        if start > end + 1e-8:
            result.append((end, start, 'unannotated'))
        reduced = reduce_label(label)
        status = 'unsupported' if reduced is None else ('N' if reduced == 'N' else 'chord')
        if result and result[-1][2] == status and abs(result[-1][1] - start) <= 1e-8:
            result[-1] = (result[-1][0], stop, status)
        else:
            result.append((start, stop, status))
        end = stop
    if end < duration - 1e-8:
        result.append((end, duration, 'unannotated'))
    return result


def write_diagnostic_player(destination, audio_path, title, reference, predictions,
                            *, dataset, context='', focus_intervals=None):
    """Embed the unchanged WAV file with labelled reference and prediction rows.

    Focus intervals control playback and zoom only. They do not alter labels,
    crop the source audio, or rerun recognition.
    """
    if dataset not in ATTRIBUTIONS:
        raise ValueError(f'Unknown dataset: {dataset}')
    audio_path = Path(audio_path)
    with wave.open(str(audio_path)) as recording:
        duration = recording.getnframes() / recording.getframerate()
    reference = _validated(reference, duration)
    coverage = coverage_intervals(reference, duration)
    tracks = [('Reference', reference)]
    for name, intervals in predictions.items():
        tracks.append((str(name), _validated(intervals, duration)))
    if focus_intervals is None:
        selected = [(a, b) for a, b, label in coverage if label == 'N']
        if not selected:
            selected = [(a, b) for a, b, label in coverage if label == 'unsupported']
        if not selected:
            selected = [(0.0, min(duration, 10.0))]
    else:
        selected = [(float(a), float(b)) for a, b in focus_intervals]
    if not selected or any(not math.isfinite(a) or not math.isfinite(b)
                           or a < 0 or b <= a or b > duration for a, b in selected):
        raise ValueError('Focus intervals must lie within the audio')
    attribution = ATTRIBUTIONS[dataset]
    data = {'duration': duration, 'tracks': tracks, 'coverage': coverage,
            'focus': selected, 'sourceNC': dataset == 'idmt'}
    payload = json.dumps(data, allow_nan=False).replace('<', '\\u003c')
    audio = base64.b64encode(audio_path.read_bytes()).decode('ascii')
    replacements = {
        '__TITLE__': html.escape(title), '__CONTEXT__': html.escape(context),
        '__NOTE__': html.escape(attribution['nc_note']),
        '__DATASET__': html.escape(attribution['dataset']),
        '__CREATORS__': html.escape(attribution['creators']),
        '__SOURCE__': attribution['url'], '__LICENSE__': attribution['license'],
        '__LICENSE_URL__': attribution['license_url'], '__AUDIO__': audio,
        '__PAYLOAD__': payload,
    }
    page = _PAGE
    for token, value in replacements.items():
        page = page.replace(token, value)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding='utf-8')
    return {'audio_duration_seconds': duration, 'focus_intervals': selected,
            'reference_intervals': len(reference), 'prediction_tracks': len(predictions)}


_PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
body{font:16px system-ui,sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#182831;background:#fafbfc}
h1{font-size:1.6rem}p{line-height:1.5}audio,svg{width:100%}svg{background:white;cursor:crosshair}
button,input,select{font:inherit}button{cursor:pointer;padding:.4rem .7rem}input{width:7.5rem}
.controls{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem;margin:1rem 0}
.note,.credits{color:#465767}.current{font-variant-numeric:tabular-nums}.legend{display:flex;flex-wrap:wrap;gap:1rem;font-size:.9rem}
.swatch{display:inline-block;width:.9em;height:.9em;margin-right:.3em;border:1px solid #667}
#message{min-height:1.5em;color:#8a280f}.timeline-title{margin-bottom:.25rem;font-size:1rem}
</style></head><body><h1>__TITLE__</h1><p>__CONTEXT__</p>
<p class="note">__NOTE__</p>
<audio id="audio" controls preload="metadata" src="data:audio/wav;base64,__AUDIO__"></audio>
<p class="current" id="current">0.00 s</p>
<div class="legend"><span><i class="swatch" style="background:#c8e5c6"></i>Scored chord</span>
<span><i class="swatch" style="background:#f5ce8e"></i>Scored N</span>
<span><i class="swatch" style="background:#d9c8ee"></i>Unsupported reference</span>
<span><i class="swatch" style="background:#e5e8ea"></i>Unannotated</span></div>
<h2 class="timeline-title">Full recording</h2>
<svg id="overview" role="img" aria-label="Full recording with reference coverage and saved predictions"></svg>
<div class="controls"><label>Interval <select id="examples"></select></label>
<label>Start (s) <input id="start" type="number" min="0" step="0.01"></label>
<label>End (s) <input id="end" type="number" min="0" step="0.01"></label>
<button id="focus">Focus interval</button><button id="play-range">Play interval</button>
<button id="play-context">Play with 1 s context</button><button id="whole">Show whole recording</button></div>
<p id="message" role="status"></p>
<h2 class="timeline-title" id="zoom-title">Selected interval</h2>
<svg id="detail" role="img" aria-label="Selected interval with reference coverage and saved predictions"></svg>
<p>Click either timeline to seek. Interval playback stops at its end. Chord names retain the saved labels; the coverage row uses the major/minor scoring vocabulary.</p>
<p class="credits">Audio: <a href="__SOURCE__">__DATASET__</a>, __CREATORS__.
<a href="__LICENSE_URL__">__LICENSE__</a>. The WAV file is embedded unchanged.</p>
<script id="payload" type="application/json">__PAYLOAD__</script><script>
const data=JSON.parse(document.getElementById('payload').textContent),audio=document.getElementById('audio');
const width=1150,left=140,inner=995,rowHeight=39,ns='http://www.w3.org/2000/svg';
const roots=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
const enharmonic={Db:1,Eb:3,Gb:6,Ab:8,Bb:10,Cb:11,Fb:4,'E#':5,'B#':0};
const statusNames={chord:'Chord',N:data.sourceNC?'NC → N':'N',unsupported:'Unsupported',unannotated:'Unannotated'};
const statusColors={chord:'#c8e5c6',N:'#f5ce8e',unsupported:'#d9c8ee',unannotated:'#e5e8ea'};
const views=[];let zoom=[0,data.duration],clipEnd=null,frame=null;
const startInput=document.getElementById('start'),endInput=document.getElementById('end'),message=document.getElementById('message');
startInput.max=endInput.max=data.duration;
function element(svg,tag,attrs,text){const e=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.appendChild(e);return e;}
function color(label){if(label==='N')return'#f5ce8e';const name=label.split(':')[0],root=enharmonic[name]??roots.indexOf(name);return root<0?'#ddd':`hsl(${root*30} 48% ${label.endsWith(':min')?68:83}%)`;}
function draw(id,range){
 const svg=document.getElementById(id);svg.replaceChildren();const rows=[['Coverage',data.coverage],...data.tracks];
 const span=range[1]-range[0];svg.setAttribute('viewBox',`0 0 ${width} ${rows.length*rowHeight+27}`);
 rows.forEach(([name,intervals],i)=>{element(svg,'text',{x:2,y:i*rowHeight+25,'font-size':13},name);
 intervals.forEach(([a,b,label])=>{const begin=Math.max(a,range[0]),end=Math.min(b,range[1]);if(end<=begin)return;
 const x=left+(begin-range[0])/span*inner,w=(end-begin)/span*inner;
 const rect=element(svg,'rect',{x,y:i*rowHeight+4,width:w,height:32,fill:i===0?statusColors[label]:color(label),stroke:'#84929b','stroke-width':.5});
 const title=document.createElementNS(ns,'title');title.textContent=`${i===0?statusNames[label]:label}: ${a.toFixed(3)}–${b.toFixed(3)} s`;rect.appendChild(title);
 const text=i===0?statusNames[label]:label;if(w>Math.max(30,text.length*6.1))element(svg,'text',{x:x+w/2,y:i*rowHeight+25,'text-anchor':'middle','font-size':11},text);
 });});
 for(let i=0;i<=5;i++){const t=range[0]+i*span/5;element(svg,'text',{x:left+i*inner/5,y:rows.length*rowHeight+18,'text-anchor':'middle','font-size':11},`${t.toFixed(1)} s`);}
 const cursor=element(svg,'line',{y1:0,y2:rows.length*rowHeight,stroke:'#141b22','stroke-width':2});
 const view={id,svg,range,cursor};const old=views.findIndex(v=>v.id===id);if(old<0)views.push(view);else views[old]=view;
 svg.onclick=event=>{const box=svg.getBoundingClientRect(),x=(event.clientX-box.left)/box.width*width;if(x<left||x>left+inner)return;clipEnd=null;audio.currentTime=Math.max(range[0],Math.min(range[1],range[0]+(x-left)/inner*span));update();};
 update();
}
function update(){
 if(clipEnd!==null&&audio.currentTime>=clipEnd){const stop=clipEnd;clipEnd=null;audio.pause();audio.currentTime=stop;}
 for(const view of views){const x=left+(audio.currentTime-view.range[0])/(view.range[1]-view.range[0])*inner;view.cursor.setAttribute('x1',x);view.cursor.setAttribute('x2',x);view.cursor.setAttribute('visibility',x>=left&&x<=left+inner?'visible':'hidden');}
 document.getElementById('current').textContent=`${audio.currentTime.toFixed(2)} / ${data.duration.toFixed(2)} s`;
}
function animate(){frame=null;update();if(!audio.paused)frame=requestAnimationFrame(animate);}
audio.addEventListener('play',()=>{if(frame===null)frame=requestAnimationFrame(animate);});
audio.addEventListener('pause',()=>{if(frame!==null)cancelAnimationFrame(frame);frame=null;update();});
audio.addEventListener('timeupdate',update);audio.addEventListener('seeked',update);
function selected(){const a=Number(startInput.value),b=Math.min(Number(endInput.value),data.duration);if(!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<=a||Number(endInput.value)>data.duration+1e-8){message.textContent='Choose a start and end inside the recording.';return null;}message.textContent='';return[a,b];}
function focus(range){zoom=[Math.max(0,range[0]-1),Math.min(data.duration,range[1]+1)];draw('detail',zoom);document.getElementById('zoom-title').textContent=`Selected interval: ${range[0].toFixed(2)}–${range[1].toFixed(2)} s (1 s context)`;}
function choose(i){const range=data.focus[i];startInput.value=range[0].toFixed(9);endInput.value=range[1].toFixed(9);focus(range);}
const examples=document.getElementById('examples');data.focus.forEach(([a,b],i)=>{const option=document.createElement('option');option.value=i;option.textContent=`${i+1}: ${a.toFixed(2)}–${b.toFixed(2)} s`;examples.appendChild(option);});
examples.addEventListener('change',()=>choose(Number(examples.value)));
document.getElementById('focus').onclick=()=>{const range=selected();if(range)focus(range);};
async function playRange(context){const range=selected();if(!range)return;focus(range);audio.pause();audio.currentTime=Math.max(0,range[0]-context);clipEnd=Math.min(data.duration,range[1]+context);try{await audio.play();}catch(error){clipEnd=null;message.textContent=`Playback failed: ${error.message}`;}}
document.getElementById('play-range').onclick=()=>playRange(0);
document.getElementById('play-context').onclick=()=>playRange(1);
document.getElementById('whole').onclick=()=>{clipEnd=null;draw('detail',[0,data.duration]);document.getElementById('zoom-title').textContent='Whole recording';};
audio.addEventListener('error',()=>{message.textContent='The browser could not decode the embedded WAV file.';});
draw('overview',[0,data.duration]);choose(0);
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--prediction', type=Path, required=True)
    parser.add_argument('--prediction-name', default='Long 8192')
    parser.add_argument('--recording', required=True)
    parser.add_argument('--dataset', choices=sorted(ATTRIBUTIONS), required=True)
    parser.add_argument('--context', default='Saved predictions for error inspection.')
    parser.add_argument('--focus', type=float, nargs=2, action='append')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = write_diagnostic_player(args.output, args.audio, args.recording,
             load_intervals(args.reference), {args.prediction_name: load_intervals(args.prediction)},
             dataset=args.dataset, context=args.context, focus_intervals=args.focus)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
