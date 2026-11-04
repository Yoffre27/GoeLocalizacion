<?php
declare(strict_types=1);
if(PHP_SAPI!=='cli'||getenv('GEOCHAVIN_TEST')!=='1'||getenv('DB_NAME')!=='geochavin_test')exit(1);
require __DIR__.'/../app/bootstrap.php';
set_exception_handler(function(Throwable $ex):void {fwrite(STDERR,'Database test failed: '.$ex->getMessage()."\n");exit(1);});
function expect(bool $ok,string $message):void {if(!$ok)throw new RuntimeException($message);}
expect((int)one('SELECT COUNT(*) n FROM information_schema.tables WHERE table_schema=DATABASE()')['n']===10,'Se esperaban 10 tablas');
expect(one('SELECT nombre FROM categorias WHERE id=1')['nombre']==='Arqueología','Importación UTF-8 incorrecta');
expect(one('SELECT nombre FROM atractivos_turisticos WHERE id=1')['nombre']==='Sitio arqueológico de Chavín','Texto UTF-8 de la ficha incorrecto');
expect((int)one('SELECT COUNT(*) n FROM atractivos_turisticos')['n']===1,'Semilla no idempotente');
db()->beginTransaction();
try {
 execute('INSERT INTO ubicaciones(nombre,latitud,longitud,fuente_url) VALUES(?,?,?,?)',['[PRUEBA SINTÉTICA] POINT',12.3456789,-77.1234567,'https://example.invalid/fixture']);
 $id=db()->lastInsertId();$p=one('SELECT ST_X(posicion) x, ST_Y(posicion) y FROM ubicaciones WHERE id=?',[$id]);
 expect(abs((float)$p['x']+77.1234567)<0.0000001&&abs((float)$p['y']-12.3456789)<0.0000001,'Orden POINT debe ser longitud, latitud');
 $rejected=false;
 try{execute('INSERT INTO ubicaciones(nombre,latitud,longitud,fuente_url) VALUES(?,?,?,?)',['[PRUEBA] inválida',91,0,'https://example.invalid/fixture']);}catch(PDOException $ex){$rejected=true;}
 expect($rejected,'La base debe rechazar coordenadas fuera de rango');
 $rejected=false;try{execute('DELETE FROM categorias WHERE id=1');}catch(PDOException $ex){$rejected=true;}
 expect($rejected,'Una FK debe impedir borrar la categoría de una ficha');
 echo "PASS: 10 tablas, importación idempotente, UTF-8, POINT(lon,lat), CHECK y clave foránea.\n";
}finally{db()->rollBack();}
