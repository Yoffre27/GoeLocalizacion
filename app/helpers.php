<?php
declare(strict_types=1);
function e(mixed $s): string {return htmlspecialchars((string)$s,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');}
function url(string $path=''): string {return base_path().'/'.$path;}
function redirect(string $path): never {header('Location: '.url($path),true,303);exit;}
function csrf(): string { if(empty($_SESSION['csrf'])) $_SESSION['csrf']=bin2hex(random_bytes(32)); return '<input type="hidden" name="csrf" value="'.e($_SESSION['csrf']).'">'; }
function check_csrf(): void {if(!is_string($_POST['csrf']??null)||!hash_equals($_SESSION['csrf']??'',$_POST['csrf'])) {http_response_code(403);throw new DomainException('La sesión del formulario venció. Recarga la página.');}}
function badge(bool $v): string {return $v?'<span class="badge verified">Fuente cotejada</span>':'<span class="badge pending">Pendiente de verificación</span>';}
function valid_https(string $v): bool {return filter_var($v,FILTER_VALIDATE_URL)!==false && strtolower((string)parse_url($v,PHP_URL_SCHEME))==='https';}
function source_link(string $v): string {return valid_https($v)?'<a class="text-link" href="'.e($v).'" target="_blank" rel="noopener noreferrer">Consultar fuente →</a>':'';}
function fail_page(string $title,string $message,int $code=400): never {http_response_code($code);page($title,fn()=>print('<section class="section narrow"><span class="eyebrow">GEOCHAVÍN</span><h1>'.e($title).'</h1><p>'.e($message).'</p><a class="button" href="'.e(url()).'">Volver al inicio</a></section>'),false);exit;}
function flash(string $s):void {$_SESSION['flash']=$s;}
function input_string(string $key):string {if(isset($_POST[$key])&&!is_string($_POST[$key])) throw new DomainException('Formato de campo no válido.');return trim($_POST[$key]??'');}
function query_string(string $key):string {return is_string($_GET[$key]??null)?trim($_GET[$key]):'';}
function throttle_login(): array {
 $dir=__DIR__.'/../storage';
 if(!is_dir($dir)) mkdir($dir,0700,true);
 $file=$dir.'/login-'.hash('sha256',($_SERVER['REMOTE_ADDR']??'local')).'.json';
 $fp=fopen($file,'c+');if(!$fp||!flock($fp,LOCK_EX)) throw new RuntimeException('Rate limiter unavailable');
 $data=json_decode(stream_get_contents($fp),true)??[];
 $data=array_values(array_filter($data,fn($t)=>is_int($t)&&$t>time()-900));
 if(count($data)>=10) {flock($fp,LOCK_UN);fclose($fp);throw new DomainException('Demasiados intentos. Vuelve a intentarlo en 15 minutos.');}
 $data[]=time();ftruncate($fp,0);rewind($fp);fwrite($fp,json_encode($data));flock($fp,LOCK_UN);fclose($fp);return $data;
}
