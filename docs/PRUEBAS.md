# Pruebas y estado de validación

## Entorno utilizado
Linux cloud con Docker, imagen PHP 8.3 CLI con PDO MySQL y mbstring, MySQL 8.4, Chromium real y Playwright para Python. El servidor principal usa la base `geochavin`. La prueba de integración crea `geochavin_test`, una instancia web separada y contraseñas aleatorias; los elimina al terminar, incluso ante un fallo. Se rechaza reutilizar una base de pruebas preexistente para no destruir datos ajenos.

## Comandos
Desde `/workspace/GoeLocalizacion`, después de `./bin/build-cloud.sh` y `./bin/dev.sh`:

```sh
# Sintaxis PHP; se conserva el estado de salida del verificador.
docker compose exec -T web sh -c 'find app bin public tests -name "*.php" -print0 | xargs -0 -n1 php -l'
node --check public/assets/app.js
# Requiere Playwright para Python y /usr/bin/chromium.
python3 tests/run-cloud.py
```

`tests/smoke.py` exige `GEOCHAVIN_TEST_URL` y `GEOCHAVIN_TEST_PASSWORD` si se ejecuta por separado. No se deben apuntar estas pruebas a producción. Los valores sintéticos de coordenadas, fotos, cuentas y establecimientos nunca se insertan en `geochavin` ni se presentan como inventario turístico.

## Resultado ejecutado

Validación final: esquema SQL y creación CLI de administrador correctos; **15/15 pruebas HTTP aprobadas**; comprobaciones Chromium aprobadas. GPS y OSRM se simularon; sus límites se describen más abajo. No hubo pruebas omitidas en esa ejecución.

## Cobertura
- Esquema real: 10 tablas; importación repetida sin duplicar semilla; textos UTF-8; POINT generado en orden longitud/latitud; CHECK de coordenadas y claves foráneas.
- 15 pruebas HTTP: páginas públicas y ficha, GeoJSON sin posiciones pendientes, búsqueda con intentos SQL/XSS, permisos editor/administrador, CSRF, creación/edición/eliminación, coordenadas fuera de rango, CSV y fechas, protección de la propia cuenta, rutas inexistentes y métodos, fuentes HTTPS, login/logout y flujo editorial completo.
- El flujo editorial crea ubicaciones de prueba, un atractivo, una fotografía atribuida, un servicio, una ruta con dos puntos y una cuenta editora. Comprueba su publicación, coordenadas, filtro de servicios, duración documentada y permisos. Desverifica una posición y comprueba su retirada de la API y el aviso de itinerario provisional. Elimina los registros temporales al concluir.
- Regresiones XAMPP: URL de subcarpeta con el nombre de descarga GitHub, CSS servido con HTTP 200 y tipo correcto, rutas JS/API y cookie de sesión con el prefijo correcto. Fallo de MySQL con HTTP 503 y un único documento/encabezado, sin HTML parcial.
- Chromium: inicio a 1440 y 390 píxeles sin desbordamiento horizontal; menú móvil; Leaflet; estado de inventario sin coordenadas; GPS denegado y autorizado simulado; distancia Haversine; ruta OSRM y distancia/tiempo simulados; separación de perfiles caminata/automóvil; error HTTP de la API visible; ausencia de excepciones JavaScript.
- Las capturas de [escritorio](capturas/inicio-escritorio.png) y [móvil](capturas/inicio-movil.png) muestran la base principal, no los fixtures.

## Límites de la validación
Las pruebas de GPS no prueban un sensor físico. El proveedor OSRM en Chromium es un fixture interceptado en memoria, no una validación de rutas reales. Las solicitudes externas de teselas se bloquean en la prueba para comprobar la degradación y mantenerla reproducible; no se afirma disponibilidad de OpenStreetMap en la red de esta sesión. La red inicial bloqueó la consulta a UNESCO: la ficha sigue pendiente.

No se ejecutó XAMPP en Windows ni un hosting externo; se proporcionan instrucciones y el esquema evita opciones exclusivas de MySQL como SRID 4326 obligatorio en la columna generada para facilitar MariaDB. Antes de publicar, importa y valida el esquema en la versión concreta de XAMPP. No se han comprobado senderos, accesos, horarios, coordenadas ni condiciones de viaje reales. Tampoco se ha publicado el sitio en Internet.

## Correcciones encontradas durante la ejecución
Se corrigieron permisos de lectura de la imagen/semilla SQL, se estableció `SET NAMES utf8mb4` para importaciones con clientes MySQL de distinta configuración y se separaron los avisos de teselas del estado GPS/API para que un error no oculte otro. Los healthchecks exigen una consulta real al esquema y una API GeoJSON válida, no solo puertos abiertos.
