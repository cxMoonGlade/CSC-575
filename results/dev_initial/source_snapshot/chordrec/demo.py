"""Self-contained audio playback with a clickable predicted-chord timeline."""
import base64
import html
import json
from pathlib import Path


def write_player(destination, audio_path, title, tracks, duration):
    payload = json.dumps(dict(tracks=tracks, duration=duration)).replace("</", "<\\/")
    audio = base64.b64encode(Path(audio_path).read_bytes()).decode("ascii")
    page = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chord recognition example</title>
<style>body{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#17212b}
audio{width:100%}svg{width:100%;cursor:crosshair}p{color:#465260}.current{font-variant-numeric:tabular-nums}</style>
<h1>__TITLE__</h1>
<p>Development example. Click a chord row to seek; the cursor follows playback. X marks an unsupported reference chord.</p>
<audio id="audio" controls preload="metadata" src="data:audio/wav;base64,__AUDIO__"></audio>
<p class="current" id="current">0.00 s</p>
<svg id="timeline" role="img" aria-label="Reference and predicted chord timelines"></svg>
<script>
const data=__DATA__, audio=document.getElementById('audio'), svg=document.getElementById('timeline');
const ns='http://www.w3.org/2000/svg', width=1100, left=100, inner=width-left-15, rowHeight=45;
svg.setAttribute('viewBox',`0 0 ${width} ${data.tracks.length*rowHeight+35}`);
function element(tag, attrs, text){const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.appendChild(e);return e;}
const roots=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
data.tracks.forEach(([name,intervals],i)=>{
  element('text',{x:0,y:i*rowHeight+27,'font-size':13},name);
  intervals.forEach(([a,b,label])=>{
    const pitch=roots.indexOf(label.split(':')[0]);
    const color=pitch<0?'#ddd':`hsl(${pitch*30} 55% ${label.endsWith(':min')?66:80}%)`;
    const rect=element('rect',{x:left+a/data.duration*inner,y:i*rowHeight+5,width:Math.max(0,(b-a)/data.duration*inner),height:34,fill:color,stroke:'#777','stroke-width':.5});
    const t=document.createElementNS(ns,'title');t.textContent=`${label}: ${a.toFixed(2)}–${b.toFixed(2)} s`;rect.appendChild(t);
    if((b-a)/data.duration*inner>33)element('text',{x:left+(a+b)/2/data.duration*inner,y:i*rowHeight+27,'text-anchor':'middle','font-size':10},label.replace(':maj','').replace(':min','m'));
  });
});
for(let t=0;t<=data.duration;t+=5)element('text',{x:left+t/data.duration*inner,y:data.tracks.length*rowHeight+20,'text-anchor':'middle','font-size':11},`${t}s`);
const cursor=element('line',{x1:left,x2:left,y1:0,y2:data.tracks.length*rowHeight,stroke:'#111','stroke-width':2});
function update(){const x=left+audio.currentTime/data.duration*inner;cursor.setAttribute('x1',x);cursor.setAttribute('x2',x);document.getElementById('current').textContent=`${audio.currentTime.toFixed(2)} / ${data.duration.toFixed(2)} s`;if(!audio.paused)requestAnimationFrame(update);}
audio.addEventListener('play',update);audio.addEventListener('timeupdate',update);audio.addEventListener('seeked',update);
svg.addEventListener('click',event=>{const r=svg.getBoundingClientRect(),x=(event.clientX-r.left)/r.width*width;audio.currentTime=Math.max(0,Math.min(data.duration,(x-left)/inner*data.duration));update();});
</script></html>
"""
    Path(destination).write_text(page.replace("__TITLE__", html.escape(title))
                                .replace("__DATA__", payload).replace("__AUDIO__", audio))
