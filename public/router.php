<?php
// Solo para el servidor de desarrollo de PHP. Document root: public/.
$path=rawurldecode(parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH));
$file=realpath(__DIR__.$path);
if ($path!=='/' && $file && str_starts_with($file,__DIR__.DIRECTORY_SEPARATOR) && is_file($file) && !str_ends_with($file,'.php')) return false;
require __DIR__.'/index.php';
