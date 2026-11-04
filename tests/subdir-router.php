<?php
// Adaptador de prueba: simula el SCRIPT_NAME de Apache en una subcarpeta XAMPP.
$prefix='/GoeLocalizacion-geochavin/public';
$path=rawurldecode(parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH));
if($path===$prefix||str_starts_with($path,$prefix.'/')){
 $_SERVER['SCRIPT_NAME']=$prefix.'/index.php';
 $public=realpath(__DIR__.'/../public');$file=realpath($public.substr($path,strlen($prefix)));
 if($file&&str_starts_with($file,$public.DIRECTORY_SEPARATOR)&&is_file($file)&&!str_ends_with($file,'.php')){
  $type=match(pathinfo($file,PATHINFO_EXTENSION)){'css'=>'text/css','js'=>'text/javascript','svg'=>'image/svg+xml','png'=>'image/png',default=>'application/octet-stream'};
  header('Content-Type: '.$type);readfile($file);return true;
 }
 require __DIR__.'/../public/index.php';
}else {
 // El router vive fuera del document root; simular la entrada pública, no /tests/.
 $_SERVER['SCRIPT_NAME']='/index.php';
 return require __DIR__.'/../public/router.php';
}
