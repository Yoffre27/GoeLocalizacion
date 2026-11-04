<?php
// Copiar a config.local.php (ignorado por Git). No publicar credenciales.
return [
 'db_host' => '127.0.0.1', 'db_port' => '3306', 'db_name' => 'geochavin',
 'db_user' => 'geochavin', 'db_password' => '',
 'base_path' => '', // Vacío: detección automática. Override: /geochavin/public
 'session_secure' => false, // true en producción con HTTPS
 // Solo configurar proveedores HTTPS que soporten realmente cada perfil.
 'routing_driving_url' => '', 'routing_walking_url' => '',
];
