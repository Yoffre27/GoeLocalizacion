<?php
declare(strict_types=1);
if(PHP_SAPI!=='cli') exit(1);
require __DIR__.'/../app/bootstrap.php';
$email=$argv[1]??'';$name=$argv[2]??'Administrador';$password=getenv('GEOCHAVIN_ADMIN_PASSWORD')?:'';
if(!filter_var($email,FILTER_VALIDATE_EMAIL)||strlen($email)>190||strlen($name)>120||strlen($password)<12||strlen($password)>72) {fwrite(STDERR,"Uso: GEOCHAVIN_ADMIN_PASSWORD (12–72 bytes) php bin/create-admin.php correo nombre\n");exit(1);}
try {execute('INSERT INTO usuarios(rol_id,nombre,email,password_hash) VALUES(1,?,?,?)',[$name,$email,password_hash($password,PASSWORD_DEFAULT)]);echo "Administrador creado. No existe contraseña predeterminada.\n";} catch(PDOException $ex) {fwrite(STDERR,"No se pudo crear la cuenta. Comprueba conexión y correo duplicado.\n");exit(1);}
