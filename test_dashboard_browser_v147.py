import json,os,threading,subprocess
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(os.environ.get('PORQUINHO_PROJECT','/workspace/porquinho-a24/project'))
fixture_path=Path(__file__).with_name('dashboard_fixture_v147.js')
fixture=json.loads(subprocess.check_output(['node','-e','process.stdout.write(JSON.stringify(require('+json.dumps(str(fixture_path))+')()))'],text=True))
artifacts=Path(os.environ.get('PORQUINHO_ARTIFACTS','/tmp/v147'));artifacts.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_address[1])
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1,reduced_motion='reduce')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('https://**/*',lambda route:route.abort())
 page.add_init_script("window.__requests147=[];window.fetch=(url,options)=>{window.__requests147.push({url,method:options?.method||'GET'});return new Promise(()=>{})};window.Chart=class{destroy(){}update(){}};window.Chart.defaults={};")
 page.goto(base+'/templates/index.html',wait_until='domcontentloaded')
 page.evaluate("""d=>{Date.now=()=>Date.parse('2026-10-30T21:00:00+00:00');a24MonitorData=d;lastStatus={};a24ExplicitFilters=true;a24CockpitState.currency='';a24CockpitState.account='';a24CockpitState.query='';showExperienceView('dashboard');a24UiMount();closeModal()}""",fixture)
 page.wait_for_timeout(200)
 print('desktop',page.evaluate("({width:innerWidth,scroll:document.documentElement.scrollWidth,evolution:document.querySelectorAll('#v35-dashboard .v37-evolution svg.v37-line').length,intraday:document.querySelectorAll('#v35-dashboard .v40-intraday svg.v35-intraday-svg').length,tickers:document.querySelectorAll('[data-v147-highlight]').length,dates:document.querySelectorAll('#v38-date').length})"))
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert page.locator('#v35-dashboard .v37-evolution svg.v37-line').count()==2
 page.screenshot(path=str(artifacts/'desktop.png'),full_page=True)
 page.locator('[data-v147-map]').first.click();assert 'Índices' in page.locator('#modalTitle').inner_text();page.evaluate('closeModal()')
 page.locator('#v147-modules').click();assert page.locator('#v147-menu-panel').is_visible()
 page.locator('.side-nav [data-target="market"]').click();assert page.locator('#view-market').evaluate("n=>n.classList.contains('active-view')")
 assert not page.locator('#v147-menu-panel').is_visible()
 page.reload(wait_until='domcontentloaded');assert page.locator('#view-market').evaluate("n=>n.classList.contains('active-view')")
 page.evaluate("d=>{Date.now=()=>Date.parse('2026-10-30T21:00:00+00:00');a24MonitorData=d;a24ExplicitFilters=true;a24CockpitState.currency='';a24CockpitState.account='';a24CockpitState.query='';a24UiMount()}",fixture)
 page.locator('#v147-modules').click();page.locator('.side-nav [data-target="dashboard"]').click()
 page.locator('#v35-dashboard [data-a24-currency="BRL"]').click()
 assert page.locator('#v35-dashboard .v37-evolution svg.v37-line').count()==1
 assert 'EUR' not in page.locator('#v38-top-assets').inner_text()
 page.locator('#v35-dashboard [data-a24-currency=""]').click()
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(100)
 print('mobile',page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})'))
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(artifacts/'mobile.png'),full_page=True)
 page.locator('#v147-modules').focus();page.keyboard.press('ArrowDown');assert page.locator('#v147-menu-panel').is_visible();page.keyboard.press('Escape');assert not page.locator('#v147-menu-panel').is_visible()
 assert not page.evaluate("__requests147.some(r=>r.method==='POST')")
 print('ERRORS',errors)
 assert not errors
 page.locator('.topbar [onclick="refreshNow()"]').click();assert page.evaluate("__requests147.some(r=>r.url==='/api/refresh'&&r.method==='POST')")
 browser.close()
server.shutdown()
print('CHROMIUM_DESKTOP_MOBILE_NAV_RELOAD_NATIVE_FILTERS_CHART_CLICKS_AND_EXPLICIT_MANUAL_CYCLE_OK')
