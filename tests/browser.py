"""Chromium real. Fixtures GPS y ruta solo en memoria; red externa sustituida en tests."""
import os,pathlib,json
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
TEST=os.environ['GEOCHAVIN_TEST_URL'].rstrip('/')
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':1000})
 # Teselas y fotos externas no son requisitos de este test de UI sin Internet.
 context.route('https://**/*',lambda r:r.abort())
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 captures=ROOT/'docs'/'capturas';captures.mkdir(exist_ok=True)
 for width,name in [(1440,'inicio-escritorio'),(390,'inicio-movil')]:
  page.set_viewport_size({'width':width,'height':1000 if width>500 else 844})
  page.goto('http://127.0.0.1:8080/',wait_until='networkidle')
  assert page.locator('h1').inner_text().startswith('Hay lugares que visitas.')
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Desbordamiento horizontal'
  page.screenshot(path=str(captures/(name+'.png')),full_page=True)
  if width<500:
   toggle=page.get_by_role('button',name='Abrir navegación');toggle.click();assert toggle.get_attribute('aria-expanded')=='true';page.get_by_role('link',name='Explorar mapa',exact=True).click();assert page.locator('#mapa .leaflet-pane').count()>0
 print('PASS: inicio escritorio/móvil, menú responsive, Leaflet y ausencia de desbordamiento')
 page.goto(TEST+'/GoeLocalizacion-geochavin/public/?page=explorar',wait_until='networkidle')
 assert page.locator('#mapa .leaflet-pane').count()>0
 assert page.locator('#map-results').inner_text().startswith('Aún no hay lugares')
 print('PASS: CSS, JavaScript y Leaflet en la subcarpeta XAMPP')
 page.set_viewport_size({'width':1280,'height':900});page.goto(TEST+'/?page=explorar',wait_until='networkidle')
 assert page.locator('#map-results').inner_text().startswith('Aún no hay lugares')
 # Denegación de GPS: rama explícita del navegador, sin requerir un sensor real.
 page.evaluate("() => { navigator.geolocation.getCurrentPosition = (ok,fail) => fail({code:1}); }")
 page.locator('#locate').click();assert 'No autorizaste' in page.locator('#map-status').inner_text()
 print('PASS: estado cartográfico vacío y GPS denegado')
 # Datos inyectados solo en memoria en la página de la base de prueba.
 features={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[0.01,0.01]},'properties':{'id':900,'nombre':'[PRUEBA] destino sintético','categoria':'Prueba','url':'?page=atractivo&id=900'}}],'pendientes_mapa':0,'total_publicados':1}
 page.route('**/?page=api*',lambda r:r.fulfill(json=features))
 page.route('https://routing.test.invalid/**',lambda r:r.fulfill(json={'code':'Ok','routes':[{'distance':1500,'duration':600,'geometry':{'type':'LineString','coordinates':[[0,0],[0.01,0.01]]}}]}))
 page.goto(TEST+'/?page=explorar',wait_until='networkidle')
 page.evaluate("() => { navigator.geolocation.getCurrentPosition = ok => ok({coords:{latitude:0,longitude:0,accuracy:10}}); }")
 page.locator('#locate').click();page.get_by_role('button',name='Ver en mapa').click()
 assert 'Distancia directa' in page.locator('#map-status').inner_text()
 # El servidor de pruebas autoriza en CSP el host de fixture; se configura en DOM después de comprobar el estado sin proveedor.
 page.evaluate("document.getElementById('mapa').dataset.walking='https://routing.test.invalid/route/v1/foot'")
 page.on('dialog',lambda dialog:dialog.accept())
 page.get_by_role('button',name='Ver en mapa').click()
 page.wait_for_function("document.getElementById('map-status').textContent.includes('Ruta peatonal estimada')")
 assert '1.50 km' in page.locator('#map-status').inner_text();assert '10 min' in page.locator('#map-status').inner_text()
 page.locator('#travel-mode').select_option('driving');assert 'No hay proveedor de rutas vehiculares' in page.locator('#map-status').inner_text()
 print('PASS: GPS autorizado simulado, Haversine, ruta OSRM simulada, distancia/tiempo y perfiles separados')
 # Fallo de API visible al visitante.
 page.unroute('**/?page=api*');page.route('**/?page=api*',lambda r:r.fulfill(status=503,json={'error':'fixture'}))
 page.reload(wait_until='networkidle');page.wait_for_function("document.getElementById('map-status').textContent.includes('No se pudo cargar el inventario')")
 assert not errors,errors
 print('PASS: error API explícito y JavaScript sin excepciones')
 browser.close()
