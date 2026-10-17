#!/bin/bash
# macOS: guarded Porquinho restart; streaming GET-only status observation.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" "$@" <<'A24_ACTIVATION_PY'
"""macOS orchestrator: restart only the identified Porquinho, use GET requests only."""
import hashlib,json,os,shlex,shutil,signal,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,ProxyHandler,Request
from urllib.error import URLError

EXPECTED = {'porquinho.py': 'e0ab60452286672621d7ff76392a32fa59ac4e6dcf7c438e3780debe63090891', 'brain/prospective_buy_forecast_live_hook.py': 'eec4dd4aa6e5fb95463ab0de5318fac8319c359e82b6fc1d91fa4d4b590b6467', 'brain/prospective_buy_forecast_store.py': 'b0377cb8a25169d07090d17d59eadb640c0f391e45db58fa89cb4d0b4e6394eb', 'webapp/server.py': '6256e97db4c0aaf276a88079b5fc5fa145039a97e7f47faffb00c9a1a1cdb050', 'tools/fetch_history.py': '68751ba3daee6e5e8a421f599773ce1c6b034854a649ce2d0f1e977bd13ffd98', 'brain/evolution/prediction_lab.py': '4ffb7e5065a5f174427a3afd95df4b881e677671536218216d556a377d9c6b40', 'brain/evolution/global_market_frame_a24.py': '69c8ffad548b7f3a507c9cac73f0c978bd0778dce0b8532ee0c3493c3aa58f9d', 'brain/evolution/p35e_prospective_issuance.py': 'd247729f172b62dcbb2a00ac7b34ba8d4a4bcee76cde6162b7d2ec001952ffc4', 'brain/evolution/p35h_capture_provenance.py': '0fc0be1dea0a0dfa8f82e27bbb5406000dd3ac4319cfee329da9226296e5b580', 'brain/evolution/p35f_outcome_reconciliation.py': '78969bfb188a83a7c48bdb5a8307b34d6a802f567f5eea3dd8cd4128f4c10c2a', 'brain/evolution/global_outcome_index_a24.py': 'cab04ff118fe793bb2d88a66ad5c3cdf800e0b7bbcf046a54677e2915cb4f82a', 'universal_portfolio/universal_observation_bridge.py': '47ebeb5ddf36ee3347b245d023c63207ae57fba2ad553fcfe9c737b1953059d6', 'universal_portfolio/funded_currency_research_a24.py': '96312739118a070574fbb18229fd74b690435d21cf4cbb6c078aa90e644d25c5', 'universal_portfolio/explicit_market_bindings_a24.py': '79a9e124fb6528325d47e05c50bd08849a8836d4d0f113df15049b92846145f7', 'universal_portfolio/research_quote_acquisition_a24.py': '5de162dcdbaae7833b7da97825b281e33035cc89625e322d966996350f2d6b2f', 'universal_portfolio/global_market_migration_a24.py': '12b814d543c7b7375db121c5cc197be09a68116429c7cfd5b54cebda367aa754', 'universal_portfolio/global_market_reader_a24.py': 'ef68a721d379ce4c90f5133e5e4a203d1b6b33002cbbaadf31adfb410f90416f', 'universal_portfolio/monitor_consolidation_a24.py': '28ce0de3313c2194ce12ab8206f85b4e5979143557231f2e907b59179b835231', 'static/app.js': '50b1a931e5193fefa459b5f87b6148a19ccd9ca5f5f89887084e667cd8e66f5a', 'universal_portfolio/reviewed_research_identity_links_a24.py': 'b2ed79e3ad84b2759abf5386c9302514d3c34f5f0cedae22dfd872b0d2d688a7', 'universal_portfolio/research_economic_series_a24.py': 'cdb8bf9dd5f135d800ca22630409f3b2af407cfa029583c2c817c7ba69fb941a', 'universal_portfolio/economic_evidence_source_status_a2.py': '4bb9bfcc2b87d2121d483d88d8530218a9d5adae7c071d6bc1763301cb46a005', 'universal_portfolio/scoped_economic_comparison_a24.py': 'a16076b1e5b5ddc422071063578788f2be2145705d3aed97822c70b3a96b4f02', 'universal_portfolio/universal_runtime_composition.py': '55ac6b239b354fe5ac9f4a4b826ac03f77431be911047762ad9fea53183af118', 'universal_portfolio/governed_economic_input_transport_a24.py': '9aa096717a0295625841cffc4503d4511d61c0bec766ef79aa83a209f9d2d153', 'universal_portfolio/economic_component_set_producer_a24.py': 'a7ada9cf953c275fe50b86da887fe773881b9b3fce76615dca3302cab0ca8e45', 'universal_portfolio/global_history_source_a24.py': 'b8d3c700a6afe86e0af863d2f747c07b8442325d0d825060d5d06c0e45cd0355', 'brain/evolution/global_research_lab_a24.py': '629040ff74f5e0b625e734085686c62156446749571916817448e2200852074c', 'universal_portfolio/research_economic_components_a24.py': 'f63551099da287de4e161aedd2c2785a59b24c0e461be2cab48b96135b6e2be5', 'universal_portfolio/account_cost_evidence_a24.py': '9e115bc53727bd464a70550a51c85fd9ed9b455593e51fc02ef315fbd4002eba', 'tools/review_account_costs_a24.py': '7899c4871942213fc30e7dd4f174110304430b4a7249e29adbcf7901d235d066', 'universal_portfolio/ledger.py': 'c217b5b7021f68ff86115fc4637c2d1981a4cdba0bed50dad2870b1912ce9727', 'universal_portfolio/observed_trade_costs_a24.py': '31c345c9481d54222891f06f39a4ad120f0eb00ddccc77541ba02c6d09fd690d', 'universal_portfolio/manual_external_trade_durable_store.py': '73581dfc80bd7a9ee0cbccaa0e9c560c0bfaaf5f90a86d729b44f1b4af29505b', 'brain/evolution/global_model_evaluation_a24.py': 'c34b1e1d82291b8b999740fb997ebaba2b8c5e397bc1d3a9ca7d82125c01ac1b', 'brain/evolution/global_existing_lab_a24.py': '5750f94d189a74c5b6a91ab06b4f2e54ef58ea28cc4790aba971e55e7dbead92', 'tools/run_global_existing_lab_a24.py': '095ed645df9590450b819e46fa45a79ca85e4a396e35b068d4ea311d45c22474', 'universal_portfolio/economic_action_plan_a24.py': '27211c50513aa4fa8b34b391747e2142df998c86b11c62e035cc9db93be1643d', 'universal_portfolio/economic_action_evidence_a24.py': '00ba91ce7b7d0c8a377685984c06f61da11e32472b1c4ed8ce0af281c511889e', 'universal_portfolio/economic_action_policy_a24.py': '52ebaa4957aeeada611c85af522ccdb0124bfbd335114749509e357e19806988', 'universal_portfolio/universal_adaptive_risk_policy_authority.py': 'e54420635d1a4f41ea6b4e3b0ad80b1158d6807105df8f893a74169b85e3840c', 'universal_portfolio/universal_adaptive_liquidity_policy_authority.py': '69f7fcc807dad124167040aa4687fd4470574e90b3d84174cfbe5302c3962827', 'universal_portfolio/universal_concentration_policy_authority.py': 'e3e3554e3abb85f9f7e06cdd1de7e40514f2d2e19f8580a11f1c276da466893b', 'universal_portfolio/universal_risk_evidence_authority.py': '78b130b99bb76202a4d7e586cf10f27911ff666a9b3a90922baa0592f2fb395f', 'universal_portfolio/universal_liquidity_evidence_authority.py': 'd6f53371446dcb1ff8f4ea0dea50ecc415daadd6427d7c1238f71f35ef3b566e', 'universal_portfolio/account_action_policy_store_a24.py': '3327c1fa33a8693ab5a58afb58a80d6829e77efc38cec47fd4d30e77cf6ddf5e', 'tools/configure_account_policies_a24.py': '9d58d3a881c9c997a00596a8d84e45faab08dc8ff548c12429f0a7f56b199ee9', 'brain/evolution/learned_allocation_policy_a24.py': 'eb8de365c9fe2c900c7300f08a940d7f5acc146f1046973de7274ad014339e7e', 'universal_portfolio/learned_policy_account_context_a24.py': '679823c97710ae63b9724bb7d5b2095c884fc49574bbb85f871e303578bcd3df', 'universal_portfolio/learned_policy_economic_basis_a24.py': '0c38fa5add3829329158615039da6d2495008e72203a9d9fea6e8019a07bb9aa', 'universal_portfolio/capital_relative_utility.py': '56d5b16d510c3f736b8d1ae954dfcc86e60690de89c775590c6ab78cf832bfdc', 'universal_portfolio/learned_policy_cost_context_a24.py': '61df49164c0c5c85c4273b9f1858a19bf997d29022aca215ddd5de9aea8ba793', 'universal_portfolio/cost_coverage_reconciliation_a24.py': '3e24721c15f9220c07639e8b578895b0d7dca8c7ed5a9b3da975aa0c2af6c682', 'brain/evolution/prospective_allocation_policy_a24.py': 'fa84f385188bbc586605510c07c1c7efd12955d1df6e71a50387df3924242cbd', 'brain/knowledge/system_registry.py': 'b8f71fd1202e11efaebfb96e89ae89a937b14e33415c67b7b5d80799870a2630', 'universal_portfolio/reallocation_analysis_a24.py': 'a4bdf52f2157a661ee43c4268ed96e0170433b734a8d4676fb8561611169b519', 'templates/index.html': 'd0d7c4ffd44c01fc7d8864caf62c5f01d86dcacf9ab91c6e45b71622d73044a6', 'static/universal_cockpit_a24.js': '287cef6aa3169f1e4eff409e321ff2d6a0cb3132aee739f5250dae6b0aadc842', 'static/universal_cockpit_a24.css': '20fb26718946e44c0ca5a1b8614046dcdb4e6f830e5d854fa5491de0ad44f2d9', 'universal_portfolio/universal_cockpit_a24.py': '9196731f235815f75296e1e4205baf4cf412e9e8389607c4203fe32657d95183', 'universal_portfolio/cockpit_charts_a24.py': '407b6f2f84a7ee890fb2ff2880a40537a040045d767d3fe65f536d973a9f69da', 'static/dashboard_universal_v35.js': 'c23c53e5c858b1d76ae6a5ff52b1d0185618128ed7569efbbf6a9da3d6ab2cb4', 'static/dashboard_universal_v35.css': '5b66d2afba73e840e8297d2dc6a3c477b6e8d05d81606e15dc74fac3218314ac', 'universal_portfolio/cockpit_intraday_a24.py': '18f09711fcfb14f7671503b8cadf023052823f632fde24a6b2a526c9db87e2fc'}


def shell(args):
    r=subprocess.run(args,capture_output=True,text=True,check=False)
    if r.returncode not in (0,1):raise RuntimeError('PROCESS_INSPECTION_FAILED')
    return r.stdout.strip()


def listeners(port):
    text=shell([LSOF,'-nP','-t','-iTCP:'+str(port),'-sTCP:LISTEN'])
    return sorted(set(int(x) for x in text.split() if x.isdigit()))


def identify(pid,root,python):
    uid=shell(['/bin/ps','-p',str(pid),'-o','uid='])
    args=shlex.split(shell(['/bin/ps','-ww','-p',str(pid),'-o','command=']))
    cwd=shell([LSOF,'-a','-p',str(pid),'-d','cwd','-Fn'])
    dirs=[Path(x[1:]).resolve() for x in cwd.splitlines() if x.startswith('n')]
    if uid!=str(os.getuid()) or dirs!=[root]:raise RuntimeError('LISTENER_OWNER_OR_ROOT_MISMATCH')
    if len(args)!=3 or args[1:]!=['-m','webapp.server']:
        raise RuntimeError('CANONICAL_LAUNCHER_NOT_CONFIRMED')
    binary=Path(args[0]);binary=binary if binary.is_absolute() else root/binary
    if binary.resolve()!=python.resolve():raise RuntimeError('LISTENER_PYTHON_MISMATCH')
    return shell(['/bin/ps','-p',str(pid),'-o','lstart='])


class StatusReader:
    """Bounded-memory JSON reader: retain only snapshot.timestamp and jobs.status."""
    def __init__(self, stream):
        import codecs
        self.stream=stream;self.decoder=codecs.getincrementaldecoder('utf-8')('strict')
        self.buffer='';self.index=0;self.eof=False;self.total=0;self.started=time.monotonic()
    def peek(self):
        if self.index>=len(self.buffer) and not self.eof:
            raw=self.stream.read(65536)
            self.total+=len(raw)
            if self.total>512*1024*1024:raise RuntimeError('STATUS_TRANSFER_LIMIT_EXCEEDED')
            if time.monotonic()-self.started>120:raise RuntimeError('STATUS_READ_DEADLINE_EXCEEDED')
            self.eof=not raw;self.buffer=self.decoder.decode(raw,final=self.eof);self.index=0
            if not self.buffer and not self.eof:return self.peek()
        return self.buffer[self.index] if self.index<len(self.buffer) else ''
    def take(self):
        c=self.peek()
        if not c:raise RuntimeError('STATUS_JSON_TRUNCATED')
        self.index+=1;return c
    def whitespace(self):
        while self.peek() and self.peek() in ' \t\r\n':self.index+=1
    def expect(self,c):
        self.whitespace()
        if self.take()!=c:raise RuntimeError('STATUS_JSON_INVALID')
    def string(self,keep):
        self.expect('"');chars=[];length=0
        while True:
            c=self.take()
            if c=='"':break
            if ord(c)<32:raise RuntimeError('STATUS_JSON_CONTROL_CHARACTER')
            if keep:
                chars.append(c);length+=1
                if length>16384:raise RuntimeError('STATUS_SELECTED_STRING_TOO_LARGE')
            if c=='\\':
                escaped=self.take()
                if escaped not in '"\\/bfnrtu':raise RuntimeError('STATUS_JSON_ESCAPE_INVALID')
                if keep:chars.append(escaped)
                if escaped=='u':
                    for _ in range(4):
                        digit=self.take()
                        if digit not in '0123456789abcdefABCDEF':raise RuntimeError('STATUS_JSON_UNICODE_INVALID')
                        if keep:chars.append(digit)
        return json.loads('"'+''.join(chars)+'"') if keep else None
    def value(self,path=(),keep=True,depth=0):
        if depth>128:raise RuntimeError('STATUS_JSON_DEPTH_LIMIT')
        self.whitespace();c=self.peek()
        if c=='{':
            self.take();self.whitespace();result={} if keep else None;seen=set()
            if self.peek()=='}':self.take();return result
            while True:
                key=self.string(keep)
                if keep:
                    if key in seen:raise RuntimeError('STATUS_DUPLICATE_SELECTED_OBJECT_KEY')
                    seen.add(key)
                    if len(seen)>10000:raise RuntimeError('STATUS_OBJECT_KEY_LIMIT_EXCEEDED')
                self.expect(':')
                child=keep and ((path==() and key in ('snapshot','jobs')) or
                    (path==('snapshot',) and key=='timestamp') or
                    (path==('jobs','*') and key=='status'))
                item=self.value(path+(key,) if child else (),child,depth+1)
                if child:result[key]=item
                self.whitespace();sep=self.take()
                if sep=='}':return result
                if sep!=',':raise RuntimeError('STATUS_JSON_OBJECT_INVALID')
        if c=='[':
            self.take();self.whitespace();result=[] if keep else None
            if self.peek()==']':self.take();return result
            while True:
                child=keep and path==('jobs',)
                item=self.value(('jobs','*') if child else (),child,depth+1)
                if child:
                    if len(result)>=10000:raise RuntimeError('STATUS_JOB_LIMIT_EXCEEDED')
                    result.append(item)
                self.whitespace();sep=self.take()
                if sep==']':return result
                if sep!=',':raise RuntimeError('STATUS_JSON_ARRAY_INVALID')
        if c=='"':return self.string(keep)
        token=[]
        while self.peek() and self.peek() not in ' \t\r\n,]}':
            token.append(self.take())
            if len(token)>128:raise RuntimeError('STATUS_JSON_TOKEN_INVALID')
        if not token:raise RuntimeError('STATUS_JSON_VALUE_REQUIRED')
        def invalid_constant(value):raise ValueError('NON_JSON_CONSTANT')
        item=json.loads(''.join(token),parse_constant=invalid_constant)
        return item if keep else None
    def read(self):
        result=self.value();self.whitespace()
        if self.peek():raise RuntimeError('STATUS_JSON_TRAILING_DATA')
        if (not isinstance(result,dict) or not isinstance(result.get('snapshot'),dict)
                or not isinstance(result.get('jobs'),list)
                or any(not isinstance(j,dict) or j.get('status') not in
                    ('queued','running','done','error') for j in result['jobs'])):
            raise RuntimeError('STATUS_CONTRACT_UNSUPPORTED')
        return result


def status():
    # Explicit loopback GET; ignore HTTP proxy variables for this local service.
    opener=build_opener(ProxyHandler({}))
    with opener.open(Request('http://127.0.0.1:8765/api/status',method='GET'),timeout=15) as response:
        if response.status!=200:raise RuntimeError('STATUS_HTTP_NOT_200')
        return StatusReader(response).read()


def busy(value):
    return any(isinstance(j,dict) and str(j.get('status','')).lower() in ('queued','running') for j in value['jobs'])


def forecasts(root):
    directory=root/'data/brain/prospective/buy_forecasts'
    if directory.is_symlink():raise RuntimeError('FORECAST_DIRECTORY_SYMLINK')
    out={}
    for p in directory.glob('*.json'):
        if p.is_symlink() or p.stat().st_size>4*1024*1024:raise RuntimeError('FORECAST_FILE_UNSUPPORTED')
        data=p.read_bytes();out[p.name]=hashlib.sha256(data).hexdigest()
    return out


def parse_time(value):
    try:
        stamp=datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return stamp.astimezone(timezone.utc) if stamp.tzinfo else None
    except (ValueError,TypeError):return None


def report_capture(root,before):
    after=forecasts(root)
    modified=sum(name not in after or after[name]!=digest for name,digest in before.items())
    new=sorted(set(after)-set(before));counts={};invalid=0
    for name in new:
        value=json.loads((root/'data/brain/prospective/buy_forecasts'/name).read_text())
        f=value.get('forecast') or {};h=f.get('horizon_days')
        counts[str(h)]=counts.get(str(h),0)+1
        if f.get('forecast_probability') is not None or f.get('execution_authorized') is not False:invalid+=1
    return {'new_cold_start_records':len(new),'new_records_by_horizon':counts,
            'old_forecast_files_changed_or_removed':modified,
            'new_records_with_unexpected_probability_or_authority':invalid}


"""Aggregate-only, read-only diagnostics. Does not resolve or assign identities."""
import csv,datetime as dt,hashlib,json,math
from pathlib import Path

UNIT='EXPLICIT_QUOTE_NEUTRAL_VALUES_SOURCE_UNATTESTED'

def text(v):return isinstance(v,str) and bool(v) and v==v.strip()
def finite(v):
    try:return not isinstance(v,bool) and math.isfinite(float(v))
    except (ValueError,TypeError,OverflowError):return False

def classification(row,forecast=False):
    origin=[row.get(k) for k in ('provider','provider_id','quote_currency')]
    iid=row.get('instrument_id')
    if not text(iid):return 'MISSING_INSTRUMENT_ID'
    if not all(text(v) for v in origin):return 'MISSING_OR_INVALID_PROVIDER_QUOTE'
    q=origin[-1]
    if not q.isascii() or not q.isalpha() or not q.isupper():return 'INVALID_QUOTE_CODE'
    if forecast:
        if row.get('price_unit_status')!=UNIT:return 'UNVERIFIED_PRICE_UNIT'
        if not finite(row.get('prediction_30d_pct',row.get('prediction_pct'))):return 'INVALID_PREDICTION'
    elif not finite(row.get('price')) or float(row['price'])<=0:return 'MISSING_OR_INVALID_NEUTRAL_PRICE'
    return 'EXPLICIT_BINDING_UNATTESTED'


def binding_diagnostics(root,checkpoint=None):
    root=Path(root);out={}
    def add(counts,key):counts[key]=counts.get(key,0)+1
    def missing(counts,row):
        for key in ('instrument_id','provider','provider_id','quote_currency'):
            if not text(row.get(key)):add(counts,key)
    def signature(path):
        s=path.stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
    market=root/'data/database/market_daily.csv'
    if not market.is_file():out['market']={'status':'MISSING'}
    else:
        before=signature(market);counts={};latest_counts={};missing_counts={};latest_missing={};latest=None;n=0
        with market.open(newline='',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            for row in reader:
                n+=1
                if n>2000000:raise ValueError('MARKET_ROW_LIMIT')
                state=classification(row);add(counts,state);missing(missing_counts,row)
                try:day=dt.date.fromisoformat(row.get('date',''))
                except (ValueError,TypeError):continue
                if latest is None or day>latest:latest=day;latest_counts={};latest_missing={}
                if day==latest:add(latest_counts,state);missing(latest_missing,row)
        stable=before==signature(market)
        out['market']={'status':'READ_ONLY_COUNTS' if stable else 'CHANGED_DURING_READ',
                       'rows':n if stable else None,'counts':counts if stable else {},
                       'latest_date':latest.isoformat() if latest and stable else None,
                       'latest_date_counts':latest_counts if stable else {},
                       'missing_fields':missing_counts if stable else {},'latest_date_missing_fields':latest_missing if stable else {}}
    lab=root/'results/prediction_lab.json'
    if not lab.is_file():out['prediction_lab']={'status':'MISSING'}
    else:
        before=signature(lab)
        if before[2]>32*1024*1024:raise ValueError('LAB_SIZE_LIMIT')
        value=json.loads(lab.read_text());groups={}
        if not isinstance(value,dict):raise ValueError('LAB_SCHEMA_INVALID')
        for key in ('predictions','ensemble_predictions'):
            rows=value.get(key) or []
            if not isinstance(rows,list) or any(not isinstance(r,dict) for r in rows):raise ValueError('LAB_ROWS_INVALID')
            counts={};missing_counts={}
            for row in rows:
                add(counts,classification(row,forecast=True));missing(missing_counts,row)
            groups[key]={'rows':len(rows),'counts':counts,'missing_fields':missing_counts}
        stable=before==signature(lab)
        trained=value.get('trained_at')
        out['prediction_lab']={'status':'READ_ONLY_COUNTS' if stable else 'CHANGED_DURING_READ',
                               'trained_at':trained if isinstance(trained,str) and len(trained)<=80 and stable else None,
                               'groups':groups if stable else {}}
    journal=root/'results/p35e_research_forecast_issuance.jsonl'
    if not journal.is_file():out['issuance']={'status':'MISSING','records':0}
    else:
        before=signature(journal);previous='GENESIS';counts={};missing_counts={};n=0;prefix=None;seen=set()
        if checkpoint and checkpoint.get('records')==0:prefix='GENESIS'
        with journal.open(encoding='utf-8') as f:
            for line in f:
                if len(line)>1024*1024 or not line.endswith('\n'):raise ValueError('JOURNAL_LINE_INVALID')
                item=json.loads(line);body=item['body']
                encoded=json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
                digest=hashlib.sha256((previous+'|'+encoded).encode()).hexdigest()
                if item.get('previous_hash')!=previous or item.get('hash')!=digest:raise ValueError('JOURNAL_CHAIN_INVALID')
                fid=body.get('forecast_id')
                if not text(fid) or fid in seen:raise ValueError('JOURNAL_ID_INVALID_OR_DUPLICATE')
                seen.add(fid);previous=digest;n+=1
                if n>2000000:raise ValueError('JOURNAL_ROW_LIMIT')
                add(counts,classification(body,forecast=True));missing(missing_counts,body)
                if checkpoint and n==checkpoint.get('records'):prefix=digest
        stable=before==signature(journal)
        out['issuance']={'status':'VERIFIED_LOCAL_CHAIN_UNATTESTED' if stable else 'CHANGED_DURING_READ',
                         'records':n if stable else None,'counts':counts if stable else {},'missing_fields':missing_counts if stable else {},
                         '_tail_hash':previous if stable else None,'_prior_prefix_hash':prefix if stable else None}
    return out


def public_diagnostics(value):
    return {key:{k:v for k,v in block.items() if not k.startswith('_')} for key,block in value.items()}


def verify_sources(root):
    for rel,expected in EXPECTED.items():
        p=root/rel
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('SOURCE_HASH_MISMATCH:'+rel)




def monitor_ui_status():
    opener=build_opener(ProxyHandler({}))
    with opener.open(Request('http://127.0.0.1:8765/api/research/monitor-consolidation',method='GET'),timeout=15) as response:
        raw=response.read(8*1024*1024+1)
        if response.status!=200 or len(raw)>8*1024*1024:raise RuntimeError('MONITOR_UI_RESPONSE_NOT_CONFIRMED')
        data=json.loads(raw)
    if (not isinstance(data,dict) or data.get('schema')!='porquinho.monitor-consolidation-a24/1.0'
            or any(data.get(k) is not False for k in ('financial_mutation','history_write_performed','execution_authorized','canonical_publication_authorized'))):
        raise RuntimeError('MONITOR_UI_CONTRACT_NOT_CONFIRMED')
    analysis=data.get('reallocation_analysis')
    if not isinstance(analysis,dict) or analysis.get('schema')!='porquinho.reallocation-analysis-a24/1.0' or analysis.get('execution_authorized') is not False:
        raise RuntimeError('REALLOCATION_UI_CONTRACT_NOT_CONFIRMED')
    facts=data.get('universal_portfolio')
    if not isinstance(facts,dict) or facts.get('schema')!='porquinho.universal-cockpit-a24/1.0' or facts.get('cross_currency_aggregation') is not False or facts.get('execution_authorized') is not False:
        raise RuntimeError('UNIVERSAL_DASHBOARD_UI_CONTRACT_NOT_CONFIRMED')
    charts=data.get('cockpit_charts')
    if not isinstance(charts,dict) or charts.get('schema')!='porquinho.cockpit-charts-a24/1.0' or charts.get('execution_authorized') is not False:
        raise RuntimeError('UNIVERSAL_DASHBOARD_UI_CONTRACT_NOT_CONFIRMED')
    intraday=data.get('cockpit_intraday')
    if not isinstance(intraday,dict) or intraday.get('schema')!='porquinho.cockpit-intraday-a24/1.0' or intraday.get('execution_authorized') is not False:
        raise RuntimeError('UNIVERSAL_INTRADAY_UI_CONTRACT_NOT_CONFIRMED')
    return {'endpoint_observed':True,'cockpit_intraday_summary':{k:v for k,v in intraday.items() if k!='series'},'cockpit_charts_summary':{k:v for k,v in charts.items() if k!='series'},'universal_cockpit_summary':{'schema':facts['schema'],'status':facts.get('status'),'position_count':len(facts.get('positions',[])),'account_count':len(facts.get('accounts',[])),'currencies':[v.get('currency') for v in facts.get('currency_totals',[])],'financial_values_exported':False},'reallocation_analysis':{k:v for k,v in (data.get('reallocation_analysis') or {}).items() if k!='rows'},'diagnostic_revision':data.get('diagnostic_revision'),'observed_manual_trade_costs':data.get('observed_manual_trade_costs'),'account_cost_evidence':data.get('account_cost_evidence'),'research_economic_components':data.get('research_economic_components'),'prospective_allocation_policy':data.get('prospective_allocation_policy'),'learned_policy_economic_basis':data.get('learned_policy_economic_basis'),'learned_policy_account_context':data.get('learned_policy_account_context'),'learned_allocation_policy':data.get('learned_allocation_policy'),'economic_action_policy':data.get('economic_action_policy'),'economic_action_evidence':data.get('economic_action_evidence'),'economic_action_plan':data.get('economic_action_plan'),'global_existing_lab':data.get('global_existing_lab'),'global_model_evaluation':data.get('global_model_evaluation'),'global_research_lab':data.get('global_research_lab'),'global_history_source':data.get('global_history_source'),'economic_set_producer_diagnostic':data.get('economic_set_producer_diagnostic'),'scoped_economic_comparison_summary':data.get('scoped_economic_comparison_summary'),'research_economic_series':data.get('research_economic_series'),'position_record_count':data.get('position_record_count'),'excluded_zero_position_count':data.get('excluded_zero_position_count'),'status':data.get('status'),'research_capture':data.get('research_capture'),
            'position_research_counts':data.get('position_research_counts'),'canonical':data.get('canonical'),'issues':data.get('issues',[])}

def reader_evidence(root,activated_at,process_confirmed,now=None):
    path=Path(root)/'results/prediction_lab.json'
    if not path.is_file():return {'status':'LAB_RESULT_NOT_PRESENT','loaded_reader_proven':False}
    if path.is_symlink() or path.stat().st_size>32*1024*1024:raise RuntimeError('LAB_RESULT_UNSUPPORTED')
    raw=path.read_bytes();value=json.loads(raw)
    if path.read_bytes()!=raw:return {'status':'LAB_CHANGED_DURING_READ','loaded_reader_proven':False}
    if not isinstance(value,dict):return {'status':'LAB_RESULT_INVALID','loaded_reader_proven':False}
    contract=value.get('input_contract')
    if not isinstance(contract,dict):return {'status':'INPUT_CONTRACT_NOT_YET_OBSERVED','loaded_reader_proven':False}
    counts=contract.get('unit_evidence_counts');row_count=contract.get('source_row_count');source_hash=contract.get('source_sha256')
    allowed={'EXPLICIT_QUOTE_DECLARATION_SOURCE_UNATTESTED','INVALID_QUOTE_DECLARATION_PRESERVED','ROW_QUOTE_DECLARED_LEGACY_MEASURE_UNIT_UNVERIFIED','LEGACY_EUR_COMPATIBLE_CURRENT_CODE_ONLY','UNIT_UNRESOLVED'}
    valid=(contract.get('schema')=='porquinho.global-market-reader-a24/1.0'
        and contract.get('status')=='READ_ONLY_INPUT_INSPECTED_NOT_CERTIFIED'
        and contract.get('storage_status') in ('EXACT_CONTENT_MIGRATION_VERIFIED','LIVE_SOURCE_NOT_ARCHIVED')
        and isinstance(source_hash,str) and len(source_hash)==64 and all(c in '0123456789abcdef' for c in source_hash)
        and type(row_count) is int and row_count>=0 and isinstance(counts,dict) and set(counts).issubset(allowed)
        and all(type(v) is int and v>=0 for v in counts.values()) and sum(counts.values())==row_count
        and contract.get('legacy_values_preserved') is True
        and all(contract.get(k) is False for k in ('historical_row_attestation','training_authorized_by_reader','canonical_publication_authorized'))
        and isinstance(contract.get('legacy_contract'),dict)
        and contract['legacy_contract'].get('sha256')==EXPECTED.get('tools/fetch_history.py')
        and contract['legacy_contract'].get('historical_row_attestation') is False)
    if not valid:return {'status':'INPUT_CONTRACT_INVALID_OR_UNEXPECTED','loaded_reader_proven':False}
    stamp=parse_time(value.get('trained_at'));activated=parse_time(activated_at);now=now or datetime.now(timezone.utc)
    fresh=bool(stamp and activated and activated<=stamp<=now)
    proven=bool(process_confirmed and fresh)
    return {'status':'LOADED_READER_OBSERVED_NOT_MODEL_CERTIFIED' if proven else 'INPUT_CONTRACT_PRESENT_ACTIVATION_NOT_PROVEN',
        'loaded_reader_proven':proven,'lab_result_timestamp_after_activation':fresh,
        'source_row_count':row_count,'unit_evidence_counts':counts,'source_sha256':source_hash,'storage_status':contract['storage_status'],
        'historical_row_attestation':False,'canonical_publication_authorized':False}


def locked_main(root,verify_only=False):
    import fcntl
    downloads=Path.home()/'Downloads';downloads.mkdir(exist_ok=True)
    if downloads.resolve().is_relative_to(Path(root).resolve()):raise RuntimeError('ACTIVATION_OUTPUT_MUST_BE_OUTSIDE_PROJECT')
    lock=downloads/'.porquinho_a24_activation.lock'
    fd=os.open(lock,os.O_WRONLY|os.O_CREAT|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'w') as stream:
        try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('ACTIVATION_ALREADY_RUNNING_NO_SECOND_ACTIVATOR')
        return main(root,verify_only=verify_only)

def console_report(report):
    keys=('activation','status','porquinho_restarted','http_status_200','bridge_listener_unchanged','new_snapshot_observed','manual_refresh_requested','financial_endpoint_requested','canonical_publication_authorized','capture','expected_source_hashes_verified','prior_issuance_prefix_preserved')
    result={k:report[k] for k in keys if k in report}
    ui=report.get('monitor_ui') or {}
    result['monitor_ui_status']=ui.get('status')
    result['diagnostic_revision']=ui.get('diagnostic_revision')
    result['issues']=ui.get('issues')
    basis=ui.get('learned_policy_economic_basis') or {}
    result['economic_research_status']=basis.get('status')
    result['scenario_count']=basis.get('scenario_count')
    result['net_comparable_scenario_count']=basis.get('net_comparable_scenario_count')
    result['cost_context_summary']=basis.get('cost_context_summary')
    result['prospective_allocation_policy']=ui.get('prospective_allocation_policy')
    action=ui.get('economic_action_plan') or {}
    result['manual_account_scope_summary']={k:action.get(k) for k in ('status','alternative_count','manual_currency_compatible_alternative_count','institution_asset_restriction_applied','automatic_broker_capability_inferred')}
    result['learned_cash_blocking_reason_counts']=(ui.get('learned_policy_account_context') or {}).get('blocking_reason_counts')
    action=ui.get('economic_action_plan') or {}
    result['manual_account_scope_summary']={k:action.get(k) for k in ('status','alternative_count','manual_currency_compatible_alternative_count','institution_asset_restriction_applied','automatic_broker_capability_inferred')}
    result['learned_cash_blocking_reason_counts']=(ui.get('learned_policy_account_context') or {}).get('blocking_reason_counts')
    result['reallocation_analysis']=ui.get('reallocation_analysis')
    result['universal_cockpit_summary']=ui.get('universal_cockpit_summary')
    result['cockpit_charts_summary']=ui.get('cockpit_charts_summary')
    result['cockpit_intraday_summary']=ui.get('cockpit_intraday_summary')
    result['browser_refresh_required']=True
    result['browser_loaded_new_ui_proven']=False
    result['console_is_compact_full_report_saved']=True
    return result


def main(root,verify_only=False):
    root=Path(root).expanduser().resolve(strict=True)
    python=root/'.venv/bin/python'
    if not python.is_file() or not os.access(python,os.X_OK):raise RuntimeError('CANONICAL_VENV_PYTHON_REQUIRED')
    verify_sources(root)
    old=listeners(8765)
    if len(old)!=1:raise RuntimeError('EXACTLY_ONE_PORQUINHO_LISTENER_REQUIRED')
    initial_id=identify(old[0],root,python)
    bridge_before=listeners(8787)
    if old[0] in bridge_before:raise RuntimeError('SHARED_BRIDGE_LISTENER_NO_RESTART')
    bridge_start={p:shell(['/bin/ps','-p',str(p),'-o','lstart=']) for p in bridge_before}
    initial=status()
    if busy(initial):raise RuntimeError('ACTIVE_OR_QUEUED_JOB_RETRY_AFTER_NORMAL_CYCLE')
    before=forecasts(root)
    diagnostics_before=binding_diagnostics(root)
    activation_time=None
    downloads=Path.home()/'Downloads';downloads.mkdir(exist_ok=True)
    marker=downloads/'.porquinho_a24_last_activation.json'
    verified_prior=False
    if marker.is_file():
        try:
            prior=json.loads(marker.read_text())
            activation_time=prior.get('activated_at')
            verified_prior=(prior.get('root')==str(root) and prior.get('pid')==old[0]
                            and prior.get('process_started_at')==initial_id
                            and prior.get('hashes')==EXPECTED)
        except (ValueError,OSError):pass
    restarted=False;new_pid=old[0]
    if not verify_only and not verified_prior:
        # Recheck immediately before signaling; do not target broad process names.
        if listeners(8765)!=old or identify(old[0],root,python)!=initial_id or busy(status()):
            raise RuntimeError('PROCESS_OR_JOB_STATE_CHANGED_RETRY_LATER')
        verify_sources(root)
        if listeners(8787)!=bridge_before or any(shell(['/bin/ps','-p',str(p),'-o','lstart='])!=started for p,started in bridge_start.items()):
            raise RuntimeError('BRIDGE_CHANGED_BEFORE_RESTART')
        print('REINICIANDO_SOMENTE_PORQUINHO: SIGTERM para o listener identificado; Bridge preservado.',flush=True)
        os.kill(old[0],signal.SIGTERM)
        deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            if not listeners(8765):
                # Ensure the old process exited as well as releasing the port.
                if not shell(['/bin/ps','-p',str(old[0]),'-o','pid=']):break
            time.sleep(1)
        else:raise RuntimeError('OLD_PROCESS_DID_NOT_EXIT_AFTER_SIGTERM_NO_FORCE_KILL_OR_SECOND_SERVER')
        if listeners(8765):raise RuntimeError('PORT_REOCCUPIED_NO_SECOND_SERVER_STARTED')
        log=downloads/('PORQUINHO_A24_STARTUP_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.log')
        activation_time=datetime.now(timezone.utc).isoformat()
        with log.open('xb') as stream:
            process=subprocess.Popen([str(python),'-m','webapp.server'],cwd=root,
                stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        new_pid=process.pid;restarted=True
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('NEW_SERVER_EXITED_INSPECT_LOCAL_STARTUP_LOG')
            if listeners(8765)==[new_pid]:
                try:
                    if isinstance(status().get('snapshot'),dict):break
                except (URLError,TimeoutError,OSError,ValueError):pass
            time.sleep(2)
        else:raise RuntimeError('HTTP_READINESS_NOT_CONFIRMED_SERVER_NOT_FORCE_STOPPED')
        new_start=identify(new_pid,root,python)
        verify_sources(root)
        marker.write_text(json.dumps({'root':str(root),'pid':new_pid,'process_started_at':new_start,'hashes':EXPECTED,'activated_at':activation_time}))
    else:
        print('VERIFICACAO_SEM_NOVO_REINICIO',flush=True)
    # No refresh POST: wait for the existing scheduler cadence.
    print('HTTP_STATUS_OK; aguardando ciclo normal (até 12 minutos). Não force decisões ou compras.',flush=True)
    initial_snapshot=(initial.get('snapshot') or {}).get('timestamp')
    snapshot_floor=parse_time(initial_snapshot) or datetime.now(timezone.utc)
    last_notice=0;completed=False;last=initial;reader={'status':'NOT_OBSERVED','loaded_reader_proven':False}
    deadline=time.monotonic()+720
    while time.monotonic()<deadline:
        if listeners(8765)!=[new_pid]:raise RuntimeError('LISTENER_CHANGED_DURING_OBSERVATION')
        last=status()
        stamp=(last.get('snapshot') or {}).get('timestamp')
        observed_time=parse_time(stamp)
        if observed_time and observed_time>snapshot_floor and not busy(last):
            completed=True
        reader=reader_evidence(root,activation_time,bool(restarted or verified_prior))
        if completed:
            try:ui_current=monitor_ui_status()
            except (RuntimeError,OSError,ValueError,TimeoutError):ui_current={}
            if ui_current.get('diagnostic_revision')=='UNIVERSAL_DASHBOARD_2' and isinstance(ui_current.get('cockpit_charts_summary'),dict) and isinstance(ui_current.get('universal_cockpit_summary'),dict) and isinstance(ui_current.get('reallocation_analysis'),dict) and isinstance(ui_current.get('economic_set_producer_diagnostic'),dict) and isinstance(ui_current.get('prospective_allocation_policy'),dict) and isinstance(ui_current.get('learned_policy_economic_basis'),dict) and isinstance(ui_current.get('learned_policy_account_context'),dict) and isinstance(ui_current.get('learned_allocation_policy'),dict) and isinstance(ui_current.get('economic_action_policy'),dict) and isinstance(ui_current.get('economic_action_evidence'),dict) and isinstance(ui_current.get('economic_action_plan'),dict) and isinstance(ui_current.get('global_existing_lab'),dict) and isinstance(ui_current.get('global_model_evaluation'),dict) and isinstance(ui_current.get('global_research_lab'),dict) and isinstance(ui_current.get('research_economic_components'),dict) and isinstance(ui_current.get('account_cost_evidence'),dict) and isinstance(ui_current.get('observed_manual_trade_costs'),dict):break
        if time.monotonic()-last_notice>=30:
            print('AGUARDANDO_CICLO_NORMAL: sem pedido manual de refresh.',flush=True);last_notice=time.monotonic()
        time.sleep(10)
    bridge_after=listeners(8787)
    bridge_same=(bridge_after==bridge_before and all(shell(['/bin/ps','-p',str(p),'-o','lstart='])==started for p,started in bridge_start.items()))
    verify_sources(root)
    capture=report_capture(root,before)
    try:
        diagnostics_after=binding_diagnostics(root,checkpoint=diagnostics_before.get('issuance'))
    except (OSError,ValueError,KeyError,TypeError):
        diagnostics_after={'inspection':{'status':'READ_UNAVAILABLE_OR_CHANGED_RETRY_DIAGNOSTICS'}}
    old_issuance=diagnostics_before.get('issuance') or {}
    new_issuance=diagnostics_after.get('issuance') or {}
    prefix_preserved=(new_issuance.get('_prior_prefix_hash')==old_issuance.get('_tail_hash')
        if old_issuance.get('status')=='VERIFIED_LOCAL_CHAIN_UNATTESTED' and new_issuance.get('status')=='VERIFIED_LOCAL_CHAIN_UNATTESTED' else None)
    trained=parse_time((diagnostics_after.get('prediction_lab') or {}).get('trained_at'))
    activated=parse_time(activation_time)
    lab_after_activation=(trained>=activated) if trained and activated and (restarted or verified_prior) else False
    try:ui_observation=monitor_ui_status()
    except (RuntimeError,OSError,ValueError,TimeoutError):ui_observation={'endpoint_observed':False,'status':'MONITOR_UI_NOT_YET_CONFIRMED'}
    report={'monitor_ui':ui_observation,'activation':'A24_POSITION_MONITOR_CONSOLIDATION','porquinho_restarted':restarted,
            'http_status_200':True,'bridge_listener_unchanged':bridge_same,
            'new_snapshot_observed':completed,'global_reader':reader,'manual_refresh_requested':False,
            'financial_endpoint_requested':False,'canonical_publication_authorized':False,
            'capture':capture,
            'expected_source_hashes_verified':True,
            'matching_activation_marker_or_new_process':bool(restarted or verified_prior),
            'lab_result_timestamp_after_activation':lab_after_activation,
            'lab_timestamp_is_not_pipeline_or_model_certification':True,
            'prior_issuance_prefix_preserved':prefix_preserved,
            'bindings_before':public_diagnostics(diagnostics_before),
            'bindings_after':public_diagnostics(diagnostics_after),
            'independent_global_identity_binding_proven':False,
            'capture_interpretation':('NEW_COLD_START_RECORDS_OBSERVED' if capture['new_cold_start_records'] else
                'NO_NEW_CAPTURE_OBSERVED_NOT_PROOF_OF_FAILURE; A_NEW_COMPRE_EPISODE_IS_REQUIRED'),
            'status':('DENSE_DASHBOARD_ACTIVATED_PARTIAL_DIAGNOSTIC' if ui_observation.get('status')=='PARTIAL_READ_ONLY_OBSERVATION' else 'DENSE_DASHBOARD_ACTIVATED_AND_OBSERVED') if completed and ui_observation['endpoint_observed'] and ui_observation.get('diagnostic_revision')=='UNIVERSAL_DASHBOARD_2' and isinstance(ui_observation.get('cockpit_charts_summary'),dict) and isinstance(ui_observation.get('universal_cockpit_summary'),dict) and isinstance(ui_observation.get('reallocation_analysis'),dict) and isinstance(ui_observation.get('economic_set_producer_diagnostic'),dict) and isinstance(ui_observation.get('prospective_allocation_policy'),dict) and isinstance(ui_observation.get('learned_policy_economic_basis'),dict) and isinstance(ui_observation.get('learned_policy_account_context'),dict) and isinstance(ui_observation.get('learned_allocation_policy'),dict) and isinstance(ui_observation.get('economic_action_policy'),dict) and isinstance(ui_observation.get('economic_action_evidence'),dict) and isinstance(ui_observation.get('economic_action_plan'),dict) and isinstance(ui_observation.get('global_existing_lab'),dict) and isinstance(ui_observation.get('global_model_evaluation'),dict) and isinstance(ui_observation.get('global_research_lab'),dict) and isinstance(ui_observation.get('research_economic_components'),dict) and isinstance(ui_observation.get('account_cost_evidence'),dict) and isinstance(ui_observation.get('observed_manual_trade_costs'),dict) else 'WAITING_FOR_UNIVERSAL_DASHBOARD_RESULT'}
    path=downloads/('PORQUINHO_A24_DENSE_ACTIVATION_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(console_report(report),ensure_ascii=False,indent=2))
    print('RELATORIO_PARA_COMPARTILHAR='+str(path))
    print('O aplicativo segue suas rotinas normais, inclusive aprendizado já configurado; este comando não solicitou refresh ou operações financeiras. O acompanhamento de políticas registra novas hipóteses em journal separado no ciclo normal, sem depender de COMPRA e sem certificar políticas ou substituir modelos anteriores.')
    if not bridge_same:raise RuntimeError('BRIDGE_LISTENER_CHANGED_EXTERNALLY_REVIEW_REQUIRED')
    if prefix_preserved is False:raise RuntimeError('PRIOR_ISSUANCE_PREFIX_CHANGED_REVIEW_REQUIRED')
    if capture['old_forecast_files_changed_or_removed'] or capture['new_records_with_unexpected_probability_or_authority']:
        raise RuntimeError('CAPTURE_INVARIANT_REQUIRES_REVIEW')


if __name__=='__main__':
    if sys.platform!='darwin':raise SystemExit('Este comando de ativação é exclusivo para macOS.')
    LSOF=shutil.which('lsof') or '/usr/sbin/lsof'
    try:locked_main(sys.argv[1],verify_only='--verificar' in sys.argv[2:])
    except KeyboardInterrupt:print('Observação interrompida; nenhum encerramento adicional solicitado.');raise SystemExit(130)
    except Exception as exc:
        message=str(exc) if isinstance(exc,RuntimeError) else type(exc).__name__
        print('ATIVACAO_NAO_CONCLUIDA:'+message)
        print('Nenhum SIGKILL será enviado e nenhum segundo servidor será iniciado automaticamente.')
        raise SystemExit(1)

A24_ACTIVATION_PY
