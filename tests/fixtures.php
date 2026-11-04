<?php
declare(strict_types=1);
// Exclusivamente en una base de pruebas; nunca crea geografía de prueba en producción.
if(PHP_SAPI!=='cli'||setting_test_env()!==true)exit(1);
function setting_test_env():bool {return getenv('GEOCHAVIN_TEST')==='1'&&getenv('DB_NAME')==='geochavin_test';}
require __DIR__.'/../app/bootstrap.php';
$password=getenv('GEOCHAVIN_TEST_PASSWORD');
if(!$password||strlen($password)<12)exit(1);
foreach(['admin.test@geochavin.invalid'=>1,'editor.test@geochavin.invalid'=>2] as $email=>$role)execute('INSERT INTO usuarios(rol_id,nombre,email,password_hash) VALUES(?,?,?,?)',[$role,'Cuenta de prueba',$email,password_hash($password,PASSWORD_DEFAULT)]);
echo "Fixtures de cuentas en geochavin_test.\n";
