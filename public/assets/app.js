'use strict';
const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => {
 const open = menu.getAttribute('aria-expanded') !== 'true';
 menu.setAttribute('aria-expanded', String(open));
 document.getElementById('main-nav')?.classList.toggle('open', open);
});
for (const form of document.querySelectorAll('form[data-confirm]')) form.addEventListener('submit', event => { if (!window.confirm(form.dataset.confirm)) event.preventDefault(); });
const mapElement = document.getElementById('mapa');
if (mapElement) initMap();
function distanceKm(a, b) {
 const rad = n => n * Math.PI / 180;
 const dlat = rad(b[0] - a[0]), dlon = rad(b[1] - a[1]);
 const x = Math.sin(dlat / 2) ** 2 + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(dlon / 2) ** 2;
 return 6371 * 2 * Math.asin(Math.sqrt(Math.min(1, Math.max(0, x))));
}
async function initMap() {
 const status = document.getElementById('map-status');
 if (typeof L === 'undefined') { status.textContent = 'El componente del mapa no está disponible. Puedes consultar las fichas del inventario.'; return; }
 // Vista nacional de orientación, no posición de un atractivo inventada.
 const map = L.map(mapElement).setView([-9.2, -75], 5);
 const tile = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
 let tileWarning = false;
 tile.on('tileerror', () => { if (!tileWarning) { tileWarning = true; document.getElementById('tile-status').textContent = 'No se pudieron cargar las teselas. Revisa tu conexión; el inventario sigue disponible debajo del mapa.'; } });
 let origin = null, gpsMarker = null, routeLine = null, routeRequest = null, selection = null;
 const locate = document.getElementById('locate');
 locate.addEventListener('click', () => {
  if (!navigator.geolocation) { status.textContent = 'Este navegador no admite geolocalización.'; return; }
  locate.disabled = true; status.textContent = 'Esperando permiso y posición GPS…';
  navigator.geolocation.getCurrentPosition(pos => {
   locate.disabled = false;
   origin = [pos.coords.latitude, pos.coords.longitude];
   if (gpsMarker) map.removeLayer(gpsMarker);
   gpsMarker = L.circleMarker(origin, { radius: 8, color: '#174b74', fillOpacity: 0.9 }).addTo(map).bindPopup('Tu ubicación aproximada');
   map.setView(origin, 14);
   status.textContent = `Ubicación obtenida. Precisión aproximada: ${Math.round(pos.coords.accuracy)} m. No se ha guardado.`;
   if (selection) showDestination(selection);
  }, error => {
   locate.disabled = false;
   status.textContent = ({1:'No autorizaste la ubicación. Puedes seguir explorando el mapa.',2:'No se pudo determinar tu ubicación. Prueba al aire libre.',3:'Se agotó el tiempo para obtener el GPS. Vuelve a intentarlo.'})[error.code] || 'No se pudo acceder al GPS. Usa HTTPS o localhost.';
  }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 30000 });
 });
 document.getElementById('travel-mode').addEventListener('change', () => { if (selection) showDestination(selection); });
 async function showDestination(feature) {
  selection = feature;
  routeRequest?.abort(); routeRequest = null;
  if (routeLine) { map.removeLayer(routeLine); routeLine = null; }
  const target = [feature.geometry.coordinates[1], feature.geometry.coordinates[0]];
  map.setView(target, 15);
  if (!origin) { status.textContent = `${feature.properties.nombre}. Activa tu ubicación para calcular la distancia directa.`; return; }
  const direct = distanceKm(origin, target);
  const mode = document.getElementById('travel-mode').value;
  const endpoint = mode === 'walking' ? mapElement.dataset.walking : mapElement.dataset.driving;
  const baseline = `Distancia directa: ${direct.toFixed(2)} km. No representa un camino transitable.`;
  status.textContent = baseline;
  if (!endpoint) { status.textContent += ` No hay proveedor de rutas ${mode === 'walking' ? 'peatonales' : 'vehiculares'} configurado; no se estima un tiempo de viaje.`; return; }
  let provider;
  try { provider = new URL(endpoint); if(provider.protocol !== 'https:') throw new Error(); }
  catch { status.textContent += ' El proveedor de rutas no tiene una URL HTTPS válida.'; return; }
  if (!window.confirm(`Para calcular la ruta se enviarán tu ubicación y el destino a ${provider.hostname}. ¿Quieres continuar?`)) return;
  const controller = new AbortController(); routeRequest = controller;
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
   status.textContent = 'Consultando la ruta al proveedor…';
   const coordinates = `${origin[1]},${origin[0]};${target[1]},${target[0]}`;
   const response = await fetch(`${endpoint.replace(/\/$/, '')}/${coordinates}?overview=full&geometries=geojson`, {signal:controller.signal, credentials:'omit', referrerPolicy:'no-referrer'});
   if (!response.ok) throw new Error();
   const data = await response.json(), route = data.routes?.[0];
   if (data.code !== 'Ok' || !route || !Number.isFinite(route.distance) || !Number.isFinite(route.duration) || !route.geometry) throw new Error();
   routeLine = L.geoJSON(route.geometry, {style:{color:'#b7842e',weight:5}}).addTo(map);
   map.fitBounds(routeLine.getBounds(), {padding:[28,28]});
   status.textContent = `Ruta ${mode==='walking'?'peatonal':'vehicular'} estimada por ${provider.hostname}: ${(route.distance/1000).toFixed(2)} km · ${Math.ceil(route.duration/60)} min. Confirma accesos y condiciones de seguridad; no incluye tráfico en tiempo real.`;
  } catch (error) {
   if (routeRequest === controller) status.textContent = `${baseline} El proveedor no pudo calcular una ruta. No se ha dibujado una ruta ni estimado un tiempo.`;
  } finally { clearTimeout(timeout); }
 }
 try {
  const response = await fetch(mapElement.dataset.api, {headers:{Accept:'application/json'}});
  if (!response.ok) throw new Error();
  const data = await response.json();
  if (!Array.isArray(data.features)) throw new Error();
  const group = L.featureGroup().addTo(map);
  const results = document.getElementById('map-results');
  for (const feature of data.features) {
   const props = feature.properties, coord = feature.geometry.coordinates;
   const popup = document.createElement('div');
   const title = document.createElement('strong'); title.textContent = props.nombre;
   const link = document.createElement('a'); link.href = props.url; link.textContent = 'Abrir ficha →';
   popup.append(title, document.createElement('br'), link);
   const marker = L.marker([coord[1], coord[0]]).addTo(group).bindPopup(popup);
   marker.on('click', () => showDestination(feature));
   const item = document.createElement('div'); item.className = 'map-result';
   const name = document.createElement('h3'); name.textContent = props.nombre;
   const category = document.createElement('p'); category.textContent = props.categoria;
   const button = document.createElement('button'); button.className = 'text-button'; button.textContent = 'Ver en mapa ↗';
   button.addEventListener('click', () => { marker.openPopup(); showDestination(feature); });
   item.append(name, category, button); results.append(item);
   if (window.location.hash === `#lugar-${props.id}`) { marker.openPopup(); selection = feature; }
  }
  if (group.getLayers().length) map.fitBounds(group.getBounds(), {padding:[35,35],maxZoom:15});
  else results.textContent = 'Aún no hay lugares con coordenadas verificadas para estos filtros.';
  status.textContent = `${data.features.length} lugares con coordenadas verificadas. ${data.pendientes_mapa} fichas pendientes de posición o cotejo. La vista general no representa coordenadas de atractivos.`;
  if (selection) showDestination(selection);
 } catch { status.textContent = 'No se pudo cargar el inventario del mapa. Recarga la página o consulta las fichas debajo.'; }
}
