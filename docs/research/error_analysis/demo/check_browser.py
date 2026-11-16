import asyncio, datetime, json
from pathlib import Path
from playwright.async_api import async_playwright

project=Path(__file__).resolve().parents[4]
root=project/'results/nc_diagnostic'
audit=Path(__file__).resolve().parent
async def main():
    errors=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=await browser.new_page(viewport={'width':1400,'height':1040},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        await page.add_init_script('''(() => {
            const originalRequest=requestAnimationFrame.bind(window),originalCancel=cancelAnimationFrame.bind(window),active=new Set();
            window.rafCheck={active,max:0};
            window.requestAnimationFrame=f=>{let id=originalRequest(t=>{active.delete(id);f(t);});active.add(id);window.rafCheck.max=Math.max(window.rafCheck.max,active.size);return id;};
            window.cancelAnimationFrame=id=>{active.delete(id);originalCancel(id);};
        })();''')
        async def poll_function(predicate, **kwargs):
            return await page.wait_for_function(predicate, polling=50, **kwargs)
        await page.goto((root/'jazz_8.html').as_uri())
        await poll_function("document.getElementById('audio').readyState>=1")
        audio=page.locator('#audio')
        metadata=await audio.evaluate('(a)=>({duration:a.duration,error:a.error})')
        assert metadata['error'] is None and abs(metadata['duration']-44.63634920634921)<1e-5
        assert await page.locator('#examples option').count()==8
        assert 'CC BY-NC-ND 4.0' in await page.text_content('.credits')
        assert 'GuitarSet' not in await page.text_content('.credits')
        payload=await page.locator('#payload').text_content()
        start,end=json.loads(payload)['focus'][0]
        await audio.evaluate('(a)=>a.playbackRate=4')
        await page.click('#play-range')
        await poll_function("!document.getElementById('audio').paused")
        observed_start=await audio.evaluate('(a)=>a.currentTime')
        assert start<=observed_start<start+0.8
        await poll_function("document.getElementById('audio').paused",timeout=5000)
        observed_stop=await audio.evaluate('(a)=>a.currentTime')
        assert abs(observed_stop-end)<0.02,(observed_stop,end)
        assert await page.evaluate('window.rafCheck.active.size')==0
        await page.click('#play-context')
        await poll_function("!document.getElementById('audio').paused")
        context_start=await audio.evaluate('(a)=>a.currentTime')
        assert start-1<=context_start<start-0.2
        await poll_function("document.getElementById('audio').paused",timeout=5000)
        context_stop=await audio.evaluate('(a)=>a.currentTime')
        assert abs(context_stop-(end+1))<0.02
        box=await page.locator('#overview').bounding_box()
        await page.mouse.click(box['x']+(140+995*.5)/1150*box['width'],box['y']+30)
        await poll_function('(t)=>Math.abs(document.getElementById("audio").currentTime-t)<.02',arg=metadata['duration']*.5)
        full_seek=await audio.evaluate('(a)=>a.currentTime')
        await page.select_option('#examples','3')
        selected_start,selected_end=json.loads(payload)['focus'][3]
        box=await page.locator('#detail').bounding_box()
        await page.mouse.click(box['x']+(140+995*.5)/1150*box['width'],box['y']+30)
        await poll_function('(t)=>Math.abs(document.getElementById("audio").currentTime-t)<.02',arg=(selected_start+selected_end)*.5)
        zoom_seek=await audio.evaluate('(a)=>a.currentTime')
        await page.fill('#end','0')
        await page.click('#play-range')
        assert 'Choose a start' in await page.text_content('#message')
        await page.select_option('#examples','0')
        await page.click('#focus')
        await audio.evaluate('(a)=>a.currentTime=9.9')
        await page.screenshot(path=str(root/'jazz_8.png'),full_page=True)
        raf=await page.evaluate('({pending:window.rafCheck.active.size,max:window.rafCheck.max})')
        assert raf['pending']==0 and raf['max']==1 and not errors,(raf,errors)
        result={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'browser':browser.version,'headless':True,'status':'passed','metadata':metadata,
                'interval_playback':{'requested':[start,end],'observed_start':observed_start,'observed_stop':observed_stop},
                'context_playback':{'requested':[start-1,end+1],'observed_start':context_start,'observed_stop':context_stop},
                'full_seek':full_seek,'zoom_seek':zoom_seek,'invalid_interval_rejected':True,
                'raf':raf,'page_errors':errors,'audio_content_listened_to':False,'html':'results/nc_diagnostic/jazz_8.html','screenshot':'results/nc_diagnostic/jazz_8.png'}
        (audit/'browser_validation.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result,indent=2))
        await browser.close()
asyncio.run(main())
