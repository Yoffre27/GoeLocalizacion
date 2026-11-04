<?php
declare(strict_types=1);
if(PHP_SAPI!=='cli') exit(1);
require __DIR__.'/../app/bootstrap.php';
if(setting('db_name','geochavin')!=='geochavin') {fwrite(STDERR,"El esquema de instalación usa geochavin.\n");exit(1);}
$pdo=new PDO('mysql:host='.setting('db_host','127.0.0.1').';port='.setting('db_port','3306').';charset=utf8mb4',(string)setting('db_user','geochavin'),(string)setting('db_password'),[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$sql=file_get_contents(__DIR__.'/../database/schema.sql');
$pdo->exec($sql);
echo "Esquema geochavin instalado; datos existentes conservados.\n";
