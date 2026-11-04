<?php
declare(strict_types=1);
$config = is_file(__DIR__.'/../config.local.php') ? require __DIR__.'/../config.local.php' : [];
function setting(string $key, mixed $default = ''): mixed {
 global $config;
 $value = getenv(strtoupper($key));
 return $value !== false ? $value : ($config[$key] ?? $default);
}
date_default_timezone_set('America/Lima');
ini_set('display_errors','0');
ini_set('session.use_strict_mode','1');
session_name('geochavin_session');
session_set_cookie_params(['httponly'=>true,'secure'=>filter_var(setting('session_secure',false), FILTER_VALIDATE_BOOLEAN),'samesite'=>'Lax','path'=>rtrim((string)setting('base_path'),'/').'/']);
if (PHP_SAPI !== 'cli') session_start();
require_once __DIR__.'/helpers.php';
function db(): PDO {
 static $pdo;
 if (!$pdo) {
  $name = (string)setting('db_name','geochavin');
  if (!preg_match('/^[a-zA-Z0-9_]+$/D',$name)) throw new RuntimeException('Invalid database name');
  $pdo = new PDO('mysql:host='.setting('db_host','127.0.0.1').';port='.setting('db_port','3306').';dbname='.$name.';charset=utf8mb4', (string)setting('db_user','geochavin'), (string)setting('db_password'), [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC,PDO::ATTR_EMULATE_PREPARES=>false]);
  $pdo->exec("SET time_zone = '-05:00'");
 }
 return $pdo;
}
function rows(string $sql, array $params=[]): array { $s=db()->prepare($sql); $s->execute($params); return $s->fetchAll(); }
function one(string $sql,array $params=[]): ?array { return rows($sql,$params)[0]??null; }
function execute(string $sql,array $params=[]): void { $s=db()->prepare($sql);$s->execute($params); }
function current_user(): ?array {
 if (empty($_SESSION['uid'])) return null;
 return one('SELECT u.id,u.nombre,u.email,r.nombre AS rol FROM usuarios u JOIN roles r ON r.id=u.rol_id WHERE u.id=? AND u.activo=1',[$_SESSION['uid']]);
}
