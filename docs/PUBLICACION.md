# Publicación y operación

La entrega contiene código e instrucciones; no se ha publicado en un dominio externo. La publicación del entorno cloud guarda su configuración/snapshot y es distinta del despliegue público de GeoChavín.

## Hosting Apache/PHP/MySQL
1. Elige un hosting PHP 8.2+ con PDO MySQL, mbstring, MySQL 8 o MariaDB compatible, HTTPS y respaldos. Configura el document root exactamente en `public/`; desactiva listado de directorios y no sirvas la raíz del repositorio.
2. Copia el código y Leaflet local. Importa `database/schema.sql` con una cuenta de migración. Crea usuario de aplicación limitado a SELECT/INSERT/UPDATE/DELETE de geochavin. Guarda credenciales en variables de servidor o `config.local.php` fuera del document root.
3. Configura `base_path` según el subdirectorio público; `session_secure=true`; HTTPS obligatorio, redirección HTTP→HTTPS en el proxy/Apache y HSTS después de validar el dominio. No uses el servidor integrado PHP en producción; usa Apache/mod_php o PHP-FPM.
4. Garantiza escritura privada de `storage/` y limpieza periódica de archivos `login-*.json` antiguos; no borres intentos recientes de limitación. Ejecuciones multinodo necesitan un limitador compartido (Redis/DB) antes de escalar.
5. Crea la primera cuenta con `bin/create-admin.php`. No introduzcas contraseñas en Git. Proporciona las credenciales al titular por un canal privado. No hay registro público ni recuperación automática por correo; las altas y restablecimientos los gestiona un administrador.
6. Proporciona datos reales cotejados y derechos fotográficos; elimina la referencia inicial si no procede. Revisa accesibilidad y contenido local antes de difusión pública.
7. Dimensiona un proveedor de mapas y, si se desea enrutamiento, proveedores HTTPS OSRM compatibles con automóvil y caminata por separado. La implementación no toma un token privado de servidor para exponerlo al cliente. Adapta política CSP/red de forma limitada a los dominios elegidos. El código añade el host de endpoints de ruta configurados a connect-src.
8. Comprueba autenticación, permisos, CSRF, formularios, API, ficha, reportes, GPS y ruta con dispositivos reales. Acepta GPS solo tras permiso y muestra el intercambio de coordenadas con proveedores. Revisa política de privacidad local y atribución de datos/fotos.
9. Programa copias de base de datos con cuenta de backup, protección de secretos, restauración de prueba y actualizaciones de PHP/OS/Leaflet. Las imágenes remotas dependen de su origen y licencia; considera alojamiento controlado al escalar.

## Recuperación y operación
- El esquema inicial es idempotente, no realiza migraciones de cambios posteriores. Usa migraciones revisadas al cambiar estructura; nunca borres el volumen para actualizar código.
- Docker: `docker compose stop` para detener y `docker compose up -d --wait` para retomar. `docker compose down` conserva el volumen; **no** uses `down -v` en una instalación con datos que quieras conservar.
- Si cambias código usando imágenes Docker, reconstruye la imagen y recrea solo web: `docker compose up -d --no-deps --force-recreate web`. La base de datos permanece.
- Exportación/backup: usa herramientas nativas de MySQL con un archivo de opciones privado o un gestor de secretos; no pongas contraseñas en argumentos/historial. Verifica restauración en una base aislada.
- El alojamiento externo, dominio, certificados y configuración de proveedores dependen del operador. No se necesita publicarlos para revisar el código y probarlo localmente.
