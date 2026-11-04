# GeoChavín

Sistema de geolocalización de atractivos turísticos de Chavín de Huántar, Huari, Áncash, Perú. PHP 8.2+, MySQL 8 / MariaDB 10.4+, HTML5, CSS3, JavaScript y Leaflet 1.9.4 con OpenStreetMap. Funciona con MySQL real; no hay datos turísticos ficticios ni sustitución de la base por localStorage.

## Entregables y orden de lectura

1. [Análisis, arquitectura, flujos, diseño y diagrama entidad-relación](docs/ARQUITECTURA.md).
2. [Esquema SQL completo: 10 tablas, claves, relaciones, índices y semilla](database/schema.sql).
3. [Instalación XAMPP y uso del panel](docs/XAMPP.md).
4. [Pruebas, estado de validación y límites](docs/PRUEBAS.md).
5. [Publicación y operación](docs/PUBLICACION.md).

## Módulos implementados

- Inicio responsive con buscador y categorías; inventario y fichas con fuentes, estado editorial, recomendaciones y galería atribuida.
- Mapa Leaflet/OpenStreetMap, GeoJSON desde PDO, filtros y posiciones verificadas. GPS por permiso del navegador, sin almacenar coordenadas personales.
- Distancia directa por Haversine; solicitud de ruta y tiempo estimado mediante un proveedor OSRM configurado para cada perfil. Los perfiles peatonal y vehicular son independientes: no se presenta una ruta de automóvil como caminata.
- Itinerarios documentados con puntos ordenados, distancias directas identificadas y duración de la fuente; directorio de hoteles, restaurantes y transporte.
- Historia, fuentes y política de privacidad.
- Login, sesiones, CSRF, consultas preparadas, validaciones y roles administrador/editor.
- CRUD de atractivos, categorías, coordenadas, fotos, servicios, rutas, puntos de ruta y usuarios. Reportes de visualizaciones por fechas y exportación CSV protegida contra fórmulas.

## XAMPP (resumen)

Consulta [las instrucciones completas](docs/XAMPP.md). Copia el proyecto a `htdocs/geochavin`, inicia Apache/MySQL, importa `database/schema.sql` en phpMyAdmin, crea un usuario de aplicación con permisos limitados y copia `config.example.php` a `config.local.php`. Deja `base_path` vacío para detectar automáticamente la carpeta pública y abre la carpeta pública con Apache. Crea el primer administrador mediante `bin/create-admin.php` con una contraseña propia; no hay credenciales predeterminadas.

## Entorno cloud actual

```sh
cd /workspace/GoeLocalizacion
./bin/build-cloud.sh
./bin/dev.sh
```

El primer comando construye PHP/PDO con la CA del proxy; el segundo genera `.env` local si no existe y arranca MySQL y PHP con Docker Compose. Se conserva el volumen de MySQL entre reinicios. Leaflet está incluido localmente con su licencia, por lo que no requiere npm para ejecutar el sitio. El servidor integrado PHP se usa solo en desarrollo.

Crear administrador sin exponer la contraseña en argumentos:

```sh
read -rs -p 'Contraseña del administrador (12–72 bytes): ' GEOCHAVIN_ADMIN_PASSWORD
export GEOCHAVIN_ADMIN_PASSWORD
printf '\n'
docker compose exec -T -e GEOCHAVIN_ADMIN_PASSWORD web php bin/create-admin.php tu-correo@ejemplo.com 'Tu nombre'
unset GEOCHAVIN_ADMIN_PASSWORD
```

El comando rechaza correos duplicados. La contraseña se almacena únicamente con `password_hash()`. En PowerShell/XAMPP hay una alternativa en la guía.

## Datos y servicios externos

La única ficha inicial es una referencia al sitio arqueológico de Chavín, marcada **pendiente de verificación**, con enlace a UNESCO, sin coordenadas ni fotografías. El catálogo inicial no es un inventario completo ni oficial. No se inventaron establecimientos, teléfonos, precios, horarios, trayectos ni puntos GPS. El ilustrador paisajístico es un SVG artístico referencial, no una fotografía documental.

Las fuentes oficiales no pudieron consultarse desde la política de red original. Un editor debe cotejar cada ficha y ubicación antes de verificarlas. El mapa permanece funcional con un estado informativo cuando no existen coordenadas comprobadas.

Teselas: `a.tile.openstreetmap.org`, `b.tile.openstreetmap.org`, `c.tile.openstreetmap.org`; conservar atribución y respetar la [política OSM](https://operations.osmfoundation.org/policies/tiles/). Para producción, usa un proveedor dimensionado a tu tráfico. GPS: HTTPS o localhost y permiso del usuario.

En `config.local.php` (o variables `ROUTING_WALKING_URL`, `ROUTING_DRIVING_URL`) configura endpoints OSRM HTTPS que realmente implementen el perfil indicado, por ejemplo la ruta base `/route/v1/…` del servicio contratado o autogestionado. No se incluye un servidor público de uso ilimitado ni un perfil peatonal ficticio. Sin proveedor, se informa solo distancia directa y no se estima tiempo. La aplicación solicita consentimiento antes de enviar origen/destino. El proveedor debe permitir CORS y añadirse a la política de red del entorno si se consulta desde allí. No pongas claves secretas en estas URLs visibles al navegador.

## Carpetas

```text
app/                 PHP: conexión, vistas, seguridad y administración
bin/                 Instalación, creación de administrador y arranque cloud
database/            Esquema SQL y datos iniciales documentados
docs/                Arquitectura, XAMPP, pruebas y publicación
public/              Único document root: index.php, router y assets
public/assets/vendor Leaflet 1.9.4 y licencia BSD
storage/             Archivos temporales del limitador; fuera de public
tests/               Pruebas HTTP y navegador; solo bases aisladas
```

`config.local.php`, `.env` y `storage` están excluidos de Git. Nunca publiques el directorio raíz con el servidor PHP; en Apache configura el document root en `public/` o bloquea explícitamente las carpetas privadas según la guía.
