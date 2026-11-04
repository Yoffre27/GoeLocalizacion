# Instalación XAMPP

## Requisitos
XAMPP con PHP 8.2 o superior y extensiones `pdo_mysql`, `mbstring`, sesiones y JSON; Apache; MySQL 8 o MariaDB 10.4+. UTF-8. El esquema usa CHECK y POINT generado compatibles con estos motores; la instancia comprobada en cloud se documenta en PRUEBAS.md. No hay Composer, Node ni compilación de frontend como requisito de ejecución.

## Instalación en Windows
1. Instala XAMPP desde su distribución oficial; inicia Apache y MySQL en el panel. No expongas XAMPP directamente a Internet.
2. Copia este proyecto a `C:\xampp\htdocs\geochavin`.
3. En phpMyAdmin importa `database/schema.sql`. El script crea `geochavin` y sus 10 tablas, roles, categorías y una ficha pendiente sin coordenadas. Se puede reimportar sin borrar datos; no es un sistema de migraciones de futuras versiones.
4. En phpMyAdmin crea un usuario de aplicación con contraseña propia, acceso a `geochavin.*` y permisos `SELECT`, `INSERT`, `UPDATE`, `DELETE`. Usa una cuenta distinta con DDL para instalación/migraciones. No ejecutes la aplicación como root.
5. Copia `config.example.php` a `config.local.php`, en la raíz. Configura host `127.0.0.1`, puerto MySQL, base `geochavin`, usuario y contraseña. Establece `base_path` a `/geochavin/public`; en desarrollo HTTP `session_secure=false`.
6. Como mínimo, protege las carpetas privadas: crea un VirtualHost con DocumentRoot `C:/xampp/htdocs/geochavin/public` (recomendado), usando `base_path=''` en ese caso. Si accedes por subcarpeta, añade en la configuración Apache reglas `Require all denied` para `app`, `bin`, `database`, `docs`, `storage`, `tests`, `.git`, y para `config.local.php`, `config.example.php`, `.env`, `compose.yaml`, `Dockerfile`. Verifica que esos archivos no son descargables. No confíes solo en que PHP ejecute el archivo de configuración.
7. Crea el administrador en PowerShell, sin incluir la contraseña en el historial:

```powershell
cd C:\xampp\htdocs\geochavin
$clave = Read-Host 'Contraseña (12–72 bytes)' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($clave)
try {
  $env:GEOCHAVIN_ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
  & C:\xampp\php\php.exe bin\create-admin.php 'tu-correo@ejemplo.com' 'Tu nombre'
} finally {
  Remove-Item Env:GEOCHAVIN_ADMIN_PASSWORD -ErrorAction SilentlyContinue
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
```

8. Accede al directorio público desde Apache. El enlace «Acceso al panel» lleva al login. No existe contraseña de ejemplo.
9. Verifica inicio, búsqueda, ficha, directorio, historia y mapa. En el panel crea/edita un registro real con su fuente. El mapa inicialmente no muestra posiciones turísticas: es intencional.

### VirtualHost de desarrollo recomendado
```apache
<VirtualHost *:80>
    ServerName geochavin.local
    DocumentRoot "C:/xampp/htdocs/geochavin/public"
    <Directory "C:/xampp/htdocs/geochavin/public">
        Options -Indexes
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```
Añade `127.0.0.1 geochavin.local` al archivo hosts si utilizas ese nombre. El GPS no está garantizado en un dominio HTTP personalizado: para GPS usa localhost o HTTPS. Para localhost por subcarpeta sigue el paso 6 de protección, o crea un VirtualHost de localhost dedicado.

## Carga editorial
1. Categorías: el esquema incluye Arqueología, Historia, Cultura y Naturaleza.
2. Ubicaciones: nombre, latitud, longitud, fuente, precisión/altitud si se conocen. La posición se expresa en WGS84. Coteja identidad, ubicación y pertenencia al distrito; marca ambas confirmaciones solo después de comprobarlas.
3. Atractivos: categoría, descripción y fuente. Asigna la ubicación. Publicar y verificar son controles separados. Para aparecer en el mapa deben estar verificados tanto el atractivo como la ubicación.
4. Fotografías: usa una URL HTTPS estable, autor, descripción alternativa, licencia y fuente. No publiques fotografías sin permiso. Verificar habilita su visualización en la ficha de un atractivo publicado. No se implementa carga de archivos en esta versión; las fotos se administran por URL.
5. Servicios: hoteles, restaurantes y transporte con dirección y contacto comprobados. Se pueden publicar como pendientes, con su etiqueta visible.
6. Rutas: guarda el itinerario sin verificar, añade por «Puntos de ruta» al menos dos ubicaciones verificadas con órdenes únicos; después verifica el conjunto. La distancia entre paradas se identifica como línea recta, nunca como longitud de camino.
7. Usuarios: solo administrador; selecciona rol editor o administrador. Para editar una cuenta, dejar contraseña vacía conserva el hash actual. No puedes desactivar/eliminar/degradar tu cuenta ni dejar sin administrador activo al sistema.
8. Reportes: filtra fechas (hora de Perú) y exporta CSV. Los conteos son vistas de fichas por sesión/día, no visitas presenciales.

## Resolución de problemas
- HTTP 503: comprueba servicio MySQL, importación del esquema, host/puerto, credenciales y extensión PDO MySQL. Consulta el log del servidor; el navegador no expone mensajes internos.
- Formularios vencidos: recarga la página; no desactives CSRF.
- Login limitado: tras 10 intentos por IP en 15 minutos hay que esperar. En producción detrás de proxy se requiere configuración adicional para distinguir IP de forma confiable; no se confía ciegamente en X-Forwarded-For.
- Mapa sin teselas: revisa red/OSM. El inventario y sus fichas siguen funcionando. Mantén atribución.
- Sin GPS: comprueba HTTPS/localhost, permisos del navegador y disponibilidad del sensor. La precisión varía.
- Sin rutas calculadas: configura proveedor con perfil real, cobertura y CORS. No desactives TLS ni inventes un tiempo estimado.
- Archivos temporales: `storage/` debe ser escribible por PHP; nunca `public/` completo con permisos 777. En producción conserva `display_errors=Off` y restringe acceso a logs.
