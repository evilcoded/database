"""Real browser controls use synthetic facts and block all financial API calls."""
import json,os,subprocess,threading
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
root=Path(os.environ.get('PORQUINHO_PROJECT','/workspace/porquinho-a24/project'))
f=Path(__file__).with_name('dashboard_fixture_v147.js')
fixture=json.loads(subprocess.check_output(['node','-e','process.stdout.write(JSON.stringify(require('+json.dumps(str(f))+')()))'],text=True))
for series in fixture['cockpit_panels']['observed_finance_intraday']['series']:
 series['points'].insert(0,{**series['points'][0],'date':'2026-10-30T18:00:00+00:00'})
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
artifacts=Path('/tmp/v149');artifacts.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1100},reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('https://**/*',lambda r:r.abort());page.add_init_script("window.__requests149=[];window.fetch=(url,options)=>{__requests149.push({url,method:options?.method||'GET'});return new Promise(()=>{})};window.Chart=class{destroy(){}update(){}};window.Chart.defaults={};")
 page.goto('http://127.0.0.1:'+str(server.server_address[1])+'/templates/index.html',wait_until='domcontentloaded')
 page.evaluate("""d=>{Date.now=()=>Date.parse('2026-10-30T21:00:00+00:00');a24MonitorData=d;lastStatus={};a24ExplicitFilters=true;a24CockpitState.currency='';a24CockpitState.account='';a24CockpitState.query='';showExperienceView('dashboard');a24UiMount();closeModal()}""",fixture)
 assert page.locator('.v149-card').count()==11
 assert page.locator('[data-v148-handle]').count()==0
 heights=page.locator('.v149-card').evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().height)');assert max(heights)-min(heights)<=1,heights
 assert page.locator('.v149-native-chart').count()==3
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(artifacts/'desktop.png'),full_page=True)
 main=page.locator('.workspace main');main.evaluate('n=>n.scrollTop=450');page.wait_for_timeout(50)
 y=page.locator('#v35-dashboard .a24-filters').bounding_box()['y'];my=main.bounding_box()['y'];assert abs(y-my)<=15,(y,my)
 main.evaluate('n=>n.scrollTop=0')
 page.locator('[data-v149-open="v149-card:evolution"]').click(position={'x':120,'y':60});assert page.locator('#modalBody').inner_text().find('Valores nativos registrados')>=0
 page.locator('#modalBody [data-v37-days="7"]').click();assert page.locator('#modalBody [data-v37-days="7"]').get_attribute('aria-pressed')=='true';page.evaluate('closeModal()')
 page.locator('[data-v149-open="v149-card:intraday"]>.v149-more').click();page.locator('#modalBody [data-v40-minutes]').select_option('30');assert page.locator('#modalBody .v149-native-chart circle').count()==6;page.evaluate('closeModal()')
 page.locator('#v147-modules').click();assert page.locator('#v147-menu-panel').is_visible();assert page.locator('#v147-menu-panel .nav-item').first.bounding_box()['height']<36
 page.keyboard.press('Escape')
 page.locator('#v35-dashboard [data-a24-currency="EUR"]').click();assert page.locator('[data-v149-open="v149-card:evolution"] .v149-native-chart path').count()==1
 page.locator('#v35-dashboard [data-a24-currency=""]').click()
 page.evaluate("()=>{for(const p of a24MonitorData.universal_portfolio.positions)p.display_label='IDENTIDADE_EXTENSA_DE_CONTROLE_'.repeat(12);a24UiMount()}")
 assert page.evaluate("[...document.querySelectorAll('.v149-card')].every(n=>n.scrollWidth<=n.clientWidth+1)")
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(artifacts/'mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.locator('[data-v149-open="v149-card:performance"]>.v149-more').click();assert 'IDENTIDADE_EXTENSA' in page.locator('#modalBody').inner_text();page.evaluate('closeModal()')
 assert not page.evaluate("__requests149.some(r=>r.method==='POST')");assert not errors,errors
 print('FIXED_ROWS_EQUAL_HEIGHT_NATIVE_COMBINED_CURVES_STICKY_FILTER_COMPACT_MENU_LONG_TEXT_POPUPS_AND_MOBILE_OK')
 browser.close()
server.shutdown()
