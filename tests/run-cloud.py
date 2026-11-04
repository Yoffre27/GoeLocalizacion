"""Pruebas en base aislada; crea y elimina solamente sus propios recursos temporales."""
import os,pathlib,secrets,subprocess,tempfile,time,urllib.request,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
def run(args,**kw):return subprocess.run(args,check=True,**kw)
def sql(text):run(['docker','compose','exec','-T','db','sh','-c','MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot'],input=text.encode(),stdout=subprocess.DEVNULL)
# No destruir una base preexistente: el CREATE sin IF NOT EXISTS debe tener éxito.
sql('CREATE DATABASE geochavin_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
name='geochavin-test-'+secrets.token_hex(4)
failure_name=name+'-outage'
password=secrets.token_urlsafe(24)
try:
 sql((ROOT/'database/schema.sql').read_text().replace('geochavin','geochavin_test'))
 sql((ROOT/'database/schema.sql').read_text().replace('geochavin','geochavin_test'))
 sql("GRANT ALL ON geochavin_test.* TO 'geochavin'@'%';")
 local=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line)
 with tempfile.NamedTemporaryFile(mode='w',prefix='geochavin-test-',delete=False) as f:
  envfile=f.name;os.chmod(envfile,0o600)
  f.write('DB_HOST=db\nDB_NAME=geochavin_test\nDB_USER=geochavin\nDB_PASSWORD='+local['DB_PASSWORD']+'\nGEOCHAVIN_TEST=1\nROUTING_WALKING_URL=https://routing.test.invalid/route/v1/foot\nGEOCHAVIN_TEST_PASSWORD='+password+'\nGEOCHAVIN_ADMIN_PASSWORD='+password+'\n')
 # Resolver la red real, sin asumir el nombre del directorio/proyecto Compose.
 dbid=subprocess.check_output(['docker','compose','ps','-q','db'],text=True).strip()
 network=next(iter(json.loads(subprocess.check_output(['docker','inspect',dbid],text=True))[0]['NetworkSettings']['Networks']))
 common=['docker','run','--rm','--network',network,'--env-file',envfile]
 run(common+['geochavin-php:local','php','tests/database.php'])
 run(common+['geochavin-php:local','php','tests/fixtures.php'])
 run(common+['geochavin-php:local','php','bin/create-admin.php','cli.test@geochavin.invalid','Administrador CLI de prueba'])
 run(['docker','run','-d','--name',name,'--network',network,'--env-file',envfile,'-p','127.0.0.1:8081:8080','geochavin-php:local','php','-S','0.0.0.0:8080','-t','public','tests/subdir-router.php'],stdout=subprocess.DEVNULL)
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for attempt in range(30):
  try:
   with opener.open('http://127.0.0.1:8081/?page=api',timeout=2) as r:assert r.status==200
   break
  except Exception:
   if attempt==29:raise
   time.sleep(1)
 run(['docker','run','-d','--name',failure_name,'--network',network,'--env-file',envfile,'-e','DB_HOST=127.0.0.1','-e','DB_PORT=1','-p','127.0.0.1:8082:8080','geochavin-php:local'],stdout=subprocess.DEVNULL)
 env={**os.environ,'GEOCHAVIN_TEST_URL':'http://127.0.0.1:8081','GEOCHAVIN_TEST_PASSWORD':password}
 run(['python3','tests/smoke.py'],env=env)
 run(['python3','tests/browser.py'],env=env)
finally:
 subprocess.run(['docker','rm','-f',name,failure_name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 sql('DROP DATABASE geochavin_test;')
 if 'envfile' in locals():os.unlink(envfile)
