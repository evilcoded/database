#!/bin/bash
set -euo pipefail
umask 077
python3 -I -B - "$HOME/Downloads" <<'PORQUINHO_IPHONE_PY'
"""Prepare a private SSH loopback test guide. Never enables SSH or changes guards."""
import html,json,os,socket,subprocess,sys,urllib.request,datetime,ipaddress,shutil
from pathlib import Path

def lan_ip():
 for interface in ('en0','en1','en2'):
  try:
   value=subprocess.check_output(['/usr/sbin/ipconfig','getifaddr',interface],timeout=3,stderr=subprocess.DEVNULL).decode().strip();ip=ipaddress.ip_address(value)
   if ip.version==4 and any(ip in net for net in map(ipaddress.ip_network,('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'))):return value
  except Exception:continue
 return None

def private_overlay_ip():
 # Query only this Mac's address, never peers, credentials or auth state dumps.
 candidates=[shutil.which('tailscale'),'/Applications/Tailscale.app/Contents/MacOS/Tailscale']
 for binary in candidates:
  if not binary or not Path(binary).is_file():continue
  try:
   value=subprocess.check_output([binary,'ip','-4'],timeout=5,stderr=subprocess.DEVNULL).decode().strip()
   ip=ipaddress.ip_address(value)
   if ip.version==4 and ip in ipaddress.ip_network('100.64.0.0/10'):return str(ip)
  except Exception:continue
 return None

def check_local():
 try:
  with socket.create_connection(('127.0.0.1',22),timeout=2):ssh=True
 except OSError:ssh=False
 try:
  with urllib.request.urlopen('http://127.0.0.1:8765/',timeout=5) as response:http=response.status==200
 except Exception:http=False
 try:user=subprocess.check_output(['/usr/bin/id','-un'],timeout=2).decode().strip()
 except Exception:user='seu_usuario_do_Mac'
 return {'schema':'porquinho.iphone-local-access-a24/1.0','mac_lan_ip':lan_ip(),'mac_private_overlay_ip':private_overlay_ip(),'mac_user':user,'porquinho_http_200':http,'ssh_listener_reachable':ssh,'server_listener_changed':False,'security_guards_changed':False,'services_restarted':False,'financial_operation_requested':False,'iphone_connection_verified':False}

def render(state):
 esc=lambda x:html.escape(str(x));ip=state.get('mac_private_overlay_ip') or state.get('mac_lan_ip') or 'IP_PRIVADO_DO_MAC';user=state.get('mac_user') or 'USUARIO_DO_MAC'
 return '''<!doctype html><html lang="pt"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Porquinho — teste no iPhone</title><style>body{font:16px system-ui;background:#041d2b;color:#e0f3ff;max-width:850px;margin:35px auto;padding:20px;line-height:1.6}article{background:#072c40;border:1px solid #1b6077;padding:20px;border-radius:12px;margin:15px 0}code{color:#5df0bc;overflow-wrap:anywhere}h1{color:#59edbb}b{color:#dcf5ff}a{color:#6ceac7}table{border-collapse:collapse;width:100%}td{border-bottom:1px solid #1b6077;padding:9px;overflow-wrap:anywhere}</style><h1>Porquinho no iPhone</h1><p>Conexão privada ao sistema local com túnel SSH. Não publica o Porquinho na internet nem muda sua validação de origem.</p>'''+f'''<article><h2>Verificação no Mac</h2><p>Porquinho HTTP 200: <b>{esc(state.get('porquinho_http_200'))}</b><br>SSH local acessível: <b>{esc(state.get('ssh_listener_reachable'))}</b><br>IP privado escolhido (Tailscale quando detectado, senão Wi-Fi): <code>{esc(ip)}</code></p><p>Conexão real do iPhone: <b>ainda não verificada</b>.</p></article><article><h2>1. Preparar o Mac</h2><p>Para acesso de qualquer rede, instale o Tailscale no Mac e no iPhone pelos aplicativos oficiais e entre na mesma rede privada. No Mac, confira o IP privado na interface do Tailscale; se este guia não o detectar, use esse IP como servidor SSH no iPhone. Mantenha o Tailscale conectado nos dois dispositivos. Para teste sem Tailscale, use a mesma rede Wi-Fi. Se o SSH estiver desativado, abra Ajustes do Sistema → Geral → Compartilhamento → Acesso Remoto. Ative somente para o usuário que fará o teste. Essa alteração exige sua ação local; este assistente não a executa.</p><p>Mantenha o Mac ligado, conectado à internet e acordado, e o Porquinho em funcionamento; um Mac suspenso não atende o iPhone. Nas opções de energia, permita impedir repouso automático quando conectado à alimentação. A conexão funciona em Wi-Fi externo ou dados móveis enquanto a rede privada e o túnel SSH estiverem ativos. Não abra portas no roteador. Não use Tailscale Funnel ou Serve público; o acesso é Tailscale privado → SSH local forwarding → Porquinho loopback. Para revogar, remova o dispositivo na administração Tailscale e desative Acesso Remoto se não precisar dele.</p></article><article><h2>2. Configurar um cliente SSH no iPhone</h2><p>Use um cliente que suporte encaminhamento <b>local</b> de portas e mantenha o túnel ativo enquanto o Safari estiver aberto. Recursos e funcionamento em segundo plano dependem do cliente/iOS.</p><table><tr><td>Servidor SSH</td><td><code>{esc(ip)}</code></td></tr><tr><td>Porta SSH do Mac</td><td><code>22</code></td></tr><tr><td>Usuário do Mac</td><td><code>{esc(user)}</code></td></tr><tr><td>Endereço/porta local no iPhone</td><td><code>127.0.0.1:8765</code></td></tr><tr><td>Destino pelo SSH no Mac</td><td><code>127.0.0.1:8765</code></td></tr></table><p>Autentique no cliente SSH com o método de acesso do Mac. Não envie senha, chave ou token para o chat.</p></article><article><h2>3. Abrir no Safari</h2><p>Com o túnel conectado, abra <a href="http://127.0.0.1:8765/"><code>http://127.0.0.1:8765/</code></a> no Safari do iPhone. O endereço é o loopback do iPhone, encaminhado por SSH ao loopback do Mac; assim, Host/Origin permanecem locais.</p><p>Teste filtros, popups, Voltar, gráficos por toque e navegação. É a mesma instalação e os mesmos dados do Mac. Nenhuma transação é simulada automaticamente por este guia.</p></article><article><h2>Se não conectar</h2><p>Confira se o túnel continua ativo, IP Wi-Fi do Mac, Acesso Remoto, autorização do usuário e firewall. Redes Wi-Fi de convidados podem bloquear comunicação entre dispositivos. Se o iOS suspender o cliente SSH, reative a conexão ou use um cliente com suporte adequado a segundo plano. Se estiver fora de casa, teste com o Wi-Fi do iPhone desligado, usando dados móveis e Tailscale. Confirme a tela de leitura e uma navegação sem transação; este guia não consegue comprovar esse teste remotamente. Tailscale transporta o SSH em rede privada, mas um domínio Tailscale Serve direto não satisfaz os guards localhost das mutações. Não altere esses guards para contornar o teste.</p><p>Para encerrar, desconecte o túnel no iPhone; se não precisar mais do Acesso Remoto, desative-o nos Ajustes do Mac.</p></article></html>'''

def write_guide(folder,state):
 folder=Path(folder).expanduser()
 if folder.is_symlink() or any(p.is_symlink() for p in folder.parents):raise ValueError('SYMLINK_OUTPUT_REFUSED')
 folder.mkdir(parents=True,exist_ok=True)
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');path=folder/('PORQUINHO_TESTE_IPHONE_'+stamp+'.html')
 with path.open('x',encoding='utf-8') as f:f.write(render(state))
 path.chmod(0o600);return path
if __name__=='__main__':
 state=check_local();path=write_guide(sys.argv[1] if len(sys.argv)>1 else Path.home()/'Downloads',state)
 # Local console only. Guide includes the local address/username; no upload or telemetry.
 print('GUIA_IPHONE='+str(path));print('PORQUINHO_HTTP_200='+str(state['porquinho_http_200']));print('SSH_ATIVO='+str(state['ssh_listener_reachable']));print('TUNEL_IPHONE_AINDA_NAO_VERIFICADO; nenhum serviço, listener, guard ou dado alterado.')

 if Path('/usr/bin/open').exists() and os.environ.get('PORQUINHO_OPEN_MOBILE_GUIDE','1')=='1':subprocess.run(['/usr/bin/open',str(path)],check=False)

PORQUINHO_IPHONE_PY
