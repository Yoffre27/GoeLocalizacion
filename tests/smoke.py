"""Integración HTTP real. Solo servidor apuntando a geochavin_test; no producción.
GEOCHAVIN_TEST_URL y GEOCHAVIN_TEST_PASSWORD requeridos. Sin dependencias pip.
"""
import os,re,json,urllib.request,urllib.parse,urllib.error,http.cookiejar,unittest
BASE=os.environ['GEOCHAVIN_TEST_URL'].rstrip('/')+'/'
PASSWORD=os.environ['GEOCHAVIN_TEST_PASSWORD']
class Client:
 def __init__(self):self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def req(self,path='',data=None):
  body=urllib.parse.urlencode(data).encode() if data is not None else None
  try:
   with self.opener.open(BASE+path,body,timeout=20) as r:return r.status,r.read().decode(),r.headers
  except urllib.error.HTTPError as r:return r.code,r.read().decode(),r.headers
 def token(self,path):
  code,body,_=self.req(path);assert code==200,(code,body[:200]);return re.search(r'name="csrf" value="([a-f0-9]+)"',body).group(1)
 def login(self,email):
  return self.req('?page=login',{'csrf':self.token('?page=login'),'email':email,'password':PASSWORD})
class Integration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.admin=Client();assert cls.admin.login('admin.test@geochavin.invalid')[0]==200
  cls.editor=Client();assert cls.editor.login('editor.test@geochavin.invalid')[0]==200
 def test_01_public_pages(self):
  c=Client()
  for page in ['', '?page=explorar','?page=directorio','?page=rutas','?page=historia','?page=atractivo&id=1']:
   with self.subTest(page=page):
    code,body,headers=c.req(page);self.assertEqual(code,200);self.assertIn('GeoChavín',body);self.assertIn('Content-Security-Policy',headers)
 def test_02_pending_not_mapped(self):
  code,body,_=Client().req('?page=api');data=json.loads(body);self.assertEqual(code,200);self.assertEqual(data['features'],[]);self.assertEqual(data['pendientes_mapa'],1)
 def test_03_sql_injection_and_xss_search(self):
  c=Client();code,body,_=c.req('?page=explorar&q='+urllib.parse.quote("' OR 1=1 -- <script>alert(1)</script>"));self.assertEqual(code,200);self.assertNotIn('<script>alert(1)</script>',body);self.assertIn('No hay lugares para estos filtros',body)
 def test_04_permissions(self):
  for page in ['?page=admin&entity=usuarios','?page=report','?page=report&format=csv']:
   self.assertEqual(self.editor.req(page)[0],403)
  self.assertIn('Acceso al panel',Client().req('?page=admin')[1])
 def test_05_csrf(self):
  self.assertEqual(self.admin.req('?page=admin&entity=categorias',{'action':'save','nombre':'No debe crearse'})[0],403)
 def test_06_crud_categories(self):
  path='?page=admin&entity=categorias';name='Categoría <script>fixture</script>'
  code,body,_=self.admin.req(path,{'csrf':self.admin.token(path),'action':'save','id':'0','nombre':name,'descripcion':'Fixture de integración'})
  self.assertEqual(code,200);self.assertNotIn(name,body);self.assertIn('Categoría &lt;script&gt;fixture&lt;/script&gt;',body)
  rows=re.findall(r'<tr>(.*?)</tr>',body,re.S);row=next(r for r in rows if 'fixture&lt;' in r);id=re.search(r'name="id" value="(\d+)"',row).group(1)
  self.assertEqual(self.admin.req(path,{'csrf':self.admin.token(path),'action':'save','id':id,'nombre':'Categoría editada de prueba','descripcion':'Actualizada'})[0],200)
  self.assertEqual(self.admin.req(path,{'csrf':self.admin.token(path),'action':'delete','id':id})[0],200)
 def test_07_invalid_coordinates(self):
  path='?page=admin&entity=ubicaciones'
  code,body,_=self.admin.req(path,{'csrf':self.admin.token(path),'action':'save','id':'0','nombre':'Fixture','latitud':'91','longitud':'-77','fuente_url':'https://example.invalid/fixture'})
  self.assertEqual(code,422);self.assertIn('fuera del rango',body)
 def test_08_csv_and_dates(self):
  code,body,headers=self.admin.req('?page=report&format=csv');self.assertEqual(code,200);self.assertIn('text/csv',headers['Content-Type']);self.assertIn('Visualizaciones',body)
  self.assertEqual(self.admin.req('?page=report&desde=2026-02-31')[0],422)
 def test_09_self_protection(self):
  code,body,_=self.admin.req('?page=admin&entity=usuarios');row=next(r for r in re.findall(r'<tr>(.*?)</tr>',body,re.S) if 'id=1' in r)
  id=re.search(r'name="id" value="(\d+)"',row).group(1)
  code,body,_=self.admin.req('?page=admin&entity=usuarios',{'csrf':self.admin.token('?page=admin&entity=usuarios'),'action':'delete','id':id})
  self.assertEqual(code,422);self.assertIn('propia cuenta',body)
 def test_10_unknown_and_invalid_methods(self):
  c=Client();self.assertEqual(c.req('?page=no-existe')[0],404);self.assertEqual(c.req('?page=atractivo&id=99999')[0],404);self.assertEqual(c.req('?page=logout')[0],405)
 def test_11_unsafe_source(self):
  path='?page=admin&entity=servicios_turisticos'
  code,body,_=self.editor.req(path,{'csrf':self.editor.token(path),'action':'save','nombre':'Fixture','tipo':'hotel','descripcion':'Prueba','fuente_url':'javascript:alert(1)'})
  self.assertEqual(code,422);self.assertIn('HTTPS',body)
 def test_12_bad_login_and_logout(self):
  c=Client();code,body,_=c.req('?page=login',{'csrf':c.token('?page=login'),'email':'missing@example.invalid','password':'incorrecta'});self.assertEqual(code,422);self.assertIn('incorrectos',body)
  c=Client();c.login('editor.test@geochavin.invalid');self.assertEqual(c.req('?page=logout',{'csrf':c.token('?page=admin')})[0],200);self.assertIn('Acceso al panel',c.req('?page=admin')[1])
 def test_13_complete_editorial_workflow(self):
  admin=self.admin
  def save(entity,data,id=0):
   path='?page=admin&entity='+entity
   code,body,_=admin.req(path,{'csrf':admin.token(path),'action':'save','id':str(id),**data})
   self.assertEqual(code,200,body[-2000:])
   return id or int(re.search(r'action=edit&amp;id=(\d+)',body).group(1))
  source='https://example.invalid/synthetic-test-only'
  # Sintéticos, exclusivamente geochavin_test: nunca se exportan a producción.
  locs=[]
  for i in range(2):
   locs.append(save('ubicaciones',{'nombre':'[PRUEBA] punto '+str(i),'latitud':str(i),'longitud':'0','fuente_url':source,'verificado':'1','confirmar_territorio':'1'}))
  a=save('atractivos_turisticos',{'nombre':'[PRUEBA] atractivo sintético','categoria_id':'1','ubicacion_id':str(locs[0]),'descripcion':'Fixture descartable, no es un destino real.','fuente_url':source,'verificado':'1','publicado':'1'})
  mapped=json.loads(Client().req('?page=api')[1]);self.assertEqual(len(mapped['features']),1);self.assertEqual(mapped['features'][0]['geometry']['coordinates'],[0,0])
  photo=save('fotografias',{'atractivo_id':str(a),'url':'https://example.invalid/test.jpg','descripcion':'[PRUEBA] foto sintética','autor':'Autor de prueba','licencia':'Fixture sin uso turístico','fuente_url':source,'verificado':'1'})
  detail=Client().req('?page=atractivo&id='+str(a))[1];self.assertIn('Autor de prueba',detail);self.assertIn('Latitud',detail)
  service=save('servicios_turisticos',{'nombre':'[PRUEBA] servicio sintético','tipo':'hotel','descripcion':'Fixture descartable','fuente_url':source,'publicado':'1','verificado':'1'})
  self.assertIn('[PRUEBA] servicio sintético',Client().req('?page=directorio&tipo=hotel')[1]);self.assertNotIn('[PRUEBA] servicio sintético',Client().req('?page=directorio&tipo=restaurante')[1])
  routeData={'nombre':'[PRUEBA] ruta sintética','descripcion':'Fixture descartable','modo':'peatonal','duracion_min':'20','fuente_url':source,'publicado':'1'}
  route=save('rutas_turisticas',routeData)
  points=[]
  for i,loc in enumerate(locs):points.append(save('puntos_ruta',{'ruta_id':str(route),'ubicacion_id':str(loc),'orden':str(i+1)}))
  save('rutas_turisticas',{**routeData,'verificado':'1'},route)
  content=Client().req('?page=rutas')[1];self.assertIn('20 minutos estimados por la fuente',content);self.assertIn('línea recta',content)
  # Una posición desverificada desaparece de la API y el itinerario no revela un trazado provisional.
  save('ubicaciones',{'nombre':'[PRUEBA] punto 0','latitud':'0','longitud':'0','fuente_url':source},locs[0])
  self.assertEqual(json.loads(Client().req('?page=api')[1])['features'],[])
  self.assertIn('Trazado pendiente de verificación',Client().req('?page=rutas')[1])
  user=save('usuarios',{'nombre':'[PRUEBA] cuenta creada','email':'created.test@geochavin.invalid','rol_id':'2','password':PASSWORD,'activo':'1'})
  c=Client();self.assertEqual(c.login('created.test@geochavin.invalid')[0],200);self.assertEqual(c.req('?page=report')[0],403)
  for entity,id in [('usuarios',user),('puntos_ruta',points[0]),('puntos_ruta',points[1]),('rutas_turisticas',route),('servicios_turisticos',service),('fotografias',photo),('atractivos_turisticos',a),('ubicaciones',locs[0]),('ubicaciones',locs[1])]:
   path='?page=admin&entity='+entity
   self.assertEqual(admin.req(path,{'csrf':admin.token(path),'action':'delete','id':str(id)})[0],200)
 def test_14_xampp_subdirectory(self):
  c=Client();prefix='GoeLocalizacion-geochavin/public/'
  code,body,headers=c.req(prefix)
  self.assertEqual(code,200);self.assertIn('href="/'+prefix+'assets/style.css"',body)
  self.assertIn('src="/'+prefix+'assets/app.js"',body)
  self.assertEqual(body.count('<!doctype html>'),1)
  self.assertIn(('path=/'+prefix).lower(),headers.get('Set-Cookie','').lower())
  code,css,headers=c.req(prefix+'assets/style.css');self.assertEqual(code,200);self.assertIn('text/css',headers['Content-Type']);self.assertIn('--green',css)
  self.assertEqual(json.loads(c.req(prefix+'?page=api')[1])['type'],'FeatureCollection')
 def test_15_database_outage_single_document(self):
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  try:opener.open('http://127.0.0.1:8082/',timeout=10);self.fail('Debía devolver 503')
  except urllib.error.HTTPError as response:
   body=response.read().decode();self.assertEqual(response.code,503)
   self.assertEqual(body.count('<!doctype html>'),1)
   self.assertEqual(body.count('class="site-header"'),1)
   self.assertIn('No podemos consultar el inventario',body)
if __name__=='__main__':unittest.main(verbosity=2)
