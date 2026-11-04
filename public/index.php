<?php
declare(strict_types=1);
require __DIR__.'/../app/bootstrap.php';
require __DIR__.'/../app/views.php';
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('X-Frame-Options: DENY');
header('Permissions-Policy: geolocation=(self), camera=(), microphone=()');
$routingHosts=[];
foreach(['routing_driving_url','routing_walking_url'] as $k) { $v=(string)setting($k);if(valid_https($v)) $routingHosts[]='https://'.parse_url($v,PHP_URL_HOST); }
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; connect-src 'self' https://*.tile.openstreetmap.org ".implode(' ',$routingHosts)."; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'");
try {
 $route=query_string('page')?:'home';
 if(in_array($route,['login','admin','logout','api','report'],true)) header('Cache-Control: no-store');
 if($route==='api') {api();exit;}
 if($route==='logout') {if($_SERVER['REQUEST_METHOD']!=='POST') fail_page('Método no permitido','Usa el formulario de cierre de sesión.',405);check_csrf();$_SESSION=[];session_regenerate_id(true);redirect('');}
 if($route==='login') {login_page();exit;}
 if($route==='admin'||$route==='report') {require __DIR__.'/../app/admin.php';admin_dispatch($route);exit;}
 switch($route) {
 case 'home':page('Un territorio por descubrir',fn()=>home());break;
 case 'explorar':page('Explora el territorio',fn()=>explore());break;
 case 'atractivo':detail_page();break;
 case 'directorio':page('Planifica tu estadía',fn()=>directory_page());break;
 case 'rutas':page('Caminos con historia',fn()=>routes_page());break;
 case 'historia':page('La memoria de un territorio',fn()=>history_page());break;
 default:fail_page('Página no encontrada','La página solicitada no existe.',404);
 }
} catch (DomainException $ex) {fail_page('Revisa la información',$ex->getMessage(),http_response_code()>=400?http_response_code():422);}
catch (Throwable $ex) {
 error_log('GeoChavin: '.$ex->getMessage());
 if(query_string('page')==='api') {http_response_code(503);header('Content-Type: application/json; charset=utf-8');echo json_encode(['error'=>'No se pudo consultar el inventario. Comprueba la conexión con MySQL.']);}
 else fail_page('No podemos consultar el inventario','La conexión con MySQL no está disponible o falta instalar el esquema. Consulta las instrucciones de instalación.',503);
}
