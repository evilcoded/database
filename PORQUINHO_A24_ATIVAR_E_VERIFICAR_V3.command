#!/bin/bash
# macOS: guarded Porquinho restart; streaming GET-only status observation.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" "$@" <<'A24_ACTIVATION_PY'
import sys
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário; nenhum processo alterado.')
"""macOS orchestrator: restart only the identified Porquinho, use GET requests only."""
import hashlib,json,os,shlex,shutil,signal,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,ProxyHandler,Request
from urllib.error import URLError

EXPECTED = {'porquinho.py': 'e0ab60452286672621d7ff76392a32fa59ac4e6dcf7c438e3780debe63090891', 'brain/prospective_buy_forecast_live_hook.py': 'eec4dd4aa6e5fb95463ab0de5318fac8319c359e82b6fc1d91fa4d4b590b6467', 'brain/prospective_buy_forecast_store.py': 'b0377cb8a25169d07090d17d59eadb640c0f391e45db58fa89cb4d0b4e6394eb', 'webapp/server.py': '1137a8572b9db42ff8720e31b5c76cf7589d2f6a93b00ec43f77c1e50ce3ae06'}


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


def main(root,verify_only=False):
    root=Path(root).expanduser().resolve(strict=True)
    python=root/'.venv/bin/python'
    if not python.is_file() or not os.access(python,os.X_OK):raise RuntimeError('CANONICAL_VENV_PYTHON_REQUIRED')
    for rel,expected in EXPECTED.items():
        p=root/rel
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('SOURCE_HASH_MISMATCH:'+rel)
    old=listeners(8765)
    if len(old)!=1:raise RuntimeError('EXACTLY_ONE_PORQUINHO_LISTENER_REQUIRED')
    initial_id=identify(old[0],root,python)
    bridge_before=listeners(8787)
    bridge_start={p:shell(['/bin/ps','-p',str(p),'-o','lstart=']) for p in bridge_before}
    initial=status()
    if busy(initial):raise RuntimeError('ACTIVE_OR_QUEUED_JOB_RETRY_AFTER_NORMAL_CYCLE')
    before=forecasts(root)
    downloads=Path.home()/'Downloads';downloads.mkdir(exist_ok=True)
    marker=downloads/'.porquinho_a24_last_activation.json'
    verified_prior=False
    if marker.is_file():
        try:
            prior=json.loads(marker.read_text())
            verified_prior=(prior.get('root')==str(root) and prior.get('pid')==old[0]
                            and prior.get('process_started_at')==initial_id
                            and prior.get('hashes')==EXPECTED)
        except (ValueError,OSError):pass
    restarted=False;new_pid=old[0]
    if not verify_only and not verified_prior:
        # Recheck immediately before signaling; do not target broad process names.
        if listeners(8765)!=old or identify(old[0],root,python)!=initial_id or busy(status()):
            raise RuntimeError('PROCESS_OR_JOB_STATE_CHANGED_RETRY_LATER')
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
        marker.write_text(json.dumps({'root':str(root),'pid':new_pid,'process_started_at':new_start,'hashes':EXPECTED}))
    else:
        print('VERIFICACAO_SEM_NOVO_REINICIO',flush=True)
    # No refresh POST: wait for the existing scheduler cadence.
    print('HTTP_STATUS_OK; aguardando ciclo normal (até 12 minutos). Não force decisões ou compras.',flush=True)
    initial_snapshot=(initial.get('snapshot') or {}).get('timestamp')
    last_notice=0;completed=False;last=initial
    deadline=time.monotonic()+720
    while time.monotonic()<deadline:
        if listeners(8765)!=[new_pid]:raise RuntimeError('LISTENER_CHANGED_DURING_OBSERVATION')
        last=status()
        stamp=(last.get('snapshot') or {}).get('timestamp')
        if stamp and stamp!=initial_snapshot and not busy(last):
            completed=True;break
        if time.monotonic()-last_notice>=30:
            print('AGUARDANDO_CICLO_NORMAL: sem pedido manual de refresh.',flush=True);last_notice=time.monotonic()
        time.sleep(10)
    bridge_after=listeners(8787)
    bridge_same=(bridge_after==bridge_before and all(shell(['/bin/ps','-p',str(p),'-o','lstart='])==started for p,started in bridge_start.items()))
    capture=report_capture(root,before)
    report={'activation':'A24_PROSPECTIVE_CAPTURE','porquinho_restarted':restarted,
            'http_status_200':True,'bridge_listener_unchanged':bridge_same,
            'new_snapshot_observed':completed,'manual_refresh_requested':False,
            'financial_endpoint_requested':False,'canonical_publication_authorized':False,
            'capture':capture,
            'capture_interpretation':('NEW_COLD_START_RECORDS_OBSERVED' if capture['new_cold_start_records'] else
                'NO_NEW_CAPTURE_OBSERVED_NOT_PROOF_OF_FAILURE; A_NEW_COMPRE_EPISODE_IS_REQUIRED'),
            'status':'NEW_SNAPSHOT_OBSERVED' if completed else 'WAITING_FOR_NORMAL_CYCLE'}
    path=downloads/('PORQUINHO_A24_ACTIVATION_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print('RELATORIO_PARA_COMPARTILHAR='+str(path))
    print('O aplicativo retomou suas rotinas normais; este comando não solicitou operações financeiras ou treinamento.')
    if not bridge_same:raise RuntimeError('BRIDGE_LISTENER_CHANGED_EXTERNALLY_REVIEW_REQUIRED')
    if capture['old_forecast_files_changed_or_removed'] or capture['new_records_with_unexpected_probability_or_authority']:
        raise RuntimeError('CAPTURE_INVARIANT_REQUIRES_REVIEW')


if __name__=='__main__':
    if sys.platform!='darwin':raise SystemExit('Este comando de ativação é exclusivo para macOS.')
    LSOF=shutil.which('lsof') or '/usr/sbin/lsof'
    try:main(sys.argv[1],verify_only='--verificar' in sys.argv[2:])
    except KeyboardInterrupt:print('Observação interrompida; nenhum encerramento adicional solicitado.');raise SystemExit(130)
    except Exception as exc:
        message=str(exc) if isinstance(exc,RuntimeError) else type(exc).__name__
        print('ATIVACAO_NAO_CONCLUIDA:'+message)
        print('Nenhum SIGKILL será enviado e nenhum segundo servidor será iniciado automaticamente.')
        raise SystemExit(1)

A24_ACTIVATION_PY
