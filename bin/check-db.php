<?php
declare(strict_types=1);
if(PHP_SAPI!=='cli')exit(1);
require __DIR__.'/../app/bootstrap.php';
$ok=true;
foreach(['pdo_mysql','mbstring'] as $extension){$present=extension_loaded($extension);echo $extension.': '.($present?'OK':'FALTA').PHP_EOL;$ok=$ok&&$present;}
if(!$ok)exit(1);
echo 'Configuración local: '.(is_file(__DIR__.'/../config.local.php')?'presente':'ausente (se usarán variables de entorno o valores de ejemplo)').PHP_EOL;
try {
 $required=['usuarios','roles','atractivos_turisticos','categorias','fotografias','servicios_turisticos','rutas_turisticas','puntos_ruta','ubicaciones','visitas'];
 // Normalizar alias para versiones de MySQL/MariaDB que cambian la capitalización.
 $tables=array_map(fn($row)=>strtolower((string)array_values($row)[0]),rows('SHOW TABLES'));
 $missing=array_diff($required,$tables);
 if($missing){fwrite(STDERR,'Conexión OK, pero faltan tablas: '.implode(', ',$missing).'. Importa database/schema.sql.'.PHP_EOL);exit(1);}
 echo "Conexión MySQL: OK. Las 10 tablas están disponibles.\n";
} catch(Throwable $ex){
 $code=$ex instanceof PDOException?($ex->errorInfo[1]??0):0;
 $message=match((int)$code){
  1045=>'Credenciales rechazadas: revisa usuario y contraseña de MySQL en config.local.php.',
  1049=>'La base no existe: importa database/schema.sql en phpMyAdmin.',
  2002,2003=>'No se puede conectar: inicia MySQL en XAMPP y revisa host y puerto.',
  default=>'No se pudo comprobar la base. Revisa configuración, esquema y log del servidor.'
 };
 fwrite(STDERR,$message.PHP_EOL);exit(1);
}
