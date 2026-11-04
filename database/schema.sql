SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS geochavin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE geochavin;
CREATE TABLE IF NOT EXISTS roles (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 nombre VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS usuarios (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 rol_id INT UNSIGNED NOT NULL,
 nombre VARCHAR(120) NOT NULL,
 email VARCHAR(190) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 activo TINYINT(1) NOT NULL DEFAULT 1,
 creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE RESTRICT
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS categorias (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 nombre VARCHAR(80) NOT NULL UNIQUE,
 descripcion TEXT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS ubicaciones (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 nombre VARCHAR(160) NOT NULL,
 latitud DECIMAL(10,7) NOT NULL,
 longitud DECIMAL(11,7) NOT NULL,
 altitud_m DECIMAL(8,2) NULL,
 precision_m DECIMAL(8,2) NULL,
 fuente_url VARCHAR(1000) NOT NULL,
 verificado TINYINT(1) NOT NULL DEFAULT 0,
 posicion POINT GENERATED ALWAYS AS (POINT(longitud,latitud)) STORED,
 CHECK (latitud BETWEEN -90 AND 90),
 CHECK (longitud BETWEEN -180 AND 180),
 CHECK (precision_m IS NULL OR precision_m >= 0),
 INDEX idx_ubicacion_estado (verificado)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS atractivos_turisticos (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 categoria_id INT UNSIGNED NOT NULL,
 ubicacion_id INT UNSIGNED NULL,
 nombre VARCHAR(180) NOT NULL,
 descripcion TEXT NOT NULL,
 recomendaciones TEXT NULL,
 fuente_url VARCHAR(1000) NOT NULL,
 verificado TINYINT(1) NOT NULL DEFAULT 0,
 publicado TINYINT(1) NOT NULL DEFAULT 0,
 creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT,
 FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id) ON DELETE SET NULL,
 INDEX idx_atr_publico (publicado,verificado),
 INDEX idx_atr_nombre (nombre)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS fotografias (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 atractivo_id INT UNSIGNED NOT NULL,
 url VARCHAR(1000) NOT NULL,
 descripcion VARCHAR(250) NOT NULL,
 autor VARCHAR(180) NOT NULL,
 licencia VARCHAR(180) NOT NULL,
 fuente_url VARCHAR(1000) NOT NULL,
 verificado TINYINT(1) NOT NULL DEFAULT 0,
 FOREIGN KEY (atractivo_id) REFERENCES atractivos_turisticos(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS servicios_turisticos (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 ubicacion_id INT UNSIGNED NULL,
 nombre VARCHAR(180) NOT NULL,
 tipo ENUM('hotel','restaurante','transporte') NOT NULL,
 descripcion TEXT NOT NULL,
 telefono VARCHAR(40) NULL,
 direccion VARCHAR(250) NULL,
 sitio_web VARCHAR(1000) NULL,
 fuente_url VARCHAR(1000) NOT NULL,
 verificado TINYINT(1) NOT NULL DEFAULT 0,
 publicado TINYINT(1) NOT NULL DEFAULT 0,
 FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id) ON DELETE SET NULL,
 INDEX idx_serv_tipo (tipo,publicado)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS rutas_turisticas (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 nombre VARCHAR(180) NOT NULL,
 descripcion TEXT NOT NULL,
 modo ENUM('peatonal','vehicular') NOT NULL,
 duracion_min INT UNSIGNED NULL,
 fuente_url VARCHAR(1000) NOT NULL,
 verificado TINYINT(1) NOT NULL DEFAULT 0,
 publicado TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS puntos_ruta (
 id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 ruta_id INT UNSIGNED NOT NULL,
 ubicacion_id INT UNSIGNED NOT NULL,
 orden INT UNSIGNED NOT NULL,
 FOREIGN KEY (ruta_id) REFERENCES rutas_turisticas(id) ON DELETE CASCADE,
 FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id) ON DELETE RESTRICT,
 UNIQUE KEY idx_ruta_orden (ruta_id,orden)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS visitas (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 atractivo_id INT UNSIGNED NOT NULL,
 usuario_id INT UNSIGNED NULL,
 fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (atractivo_id) REFERENCES atractivos_turisticos(id) ON DELETE CASCADE,
 FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
 INDEX idx_visita_fecha (fecha),
 INDEX idx_visita_atr_fecha (atractivo_id,fecha)
) ENGINE=InnoDB;
INSERT IGNORE INTO roles(id,nombre) VALUES (1,'administrador'),(2,'editor');
INSERT IGNORE INTO categorias(id,nombre,descripcion) VALUES
 (1,'Arqueología','Patrimonio arqueológico'),(2,'Historia','Patrimonio histórico'),
 (3,'Cultura','Manifestaciones culturales'),(4,'Naturaleza','Patrimonio natural');
-- Referencia pendiente de cotejo: sin coordenadas, horarios, precios ni fotografías inventadas.
INSERT INTO atractivos_turisticos(id,categoria_id,nombre,descripcion,recomendaciones,fuente_url,verificado,publicado)
SELECT 1,1,'Sitio arqueológico de Chavín','Referencia patrimonial para iniciar el inventario de Chavín de Huántar. La ficha local, sus accesos y su información turística están pendientes de cotejo con fuentes oficiales.','Consulta las indicaciones vigentes del Ministerio de Cultura antes de planificar tu visita.','https://whc.unesco.org/en/list/330/',0,1
WHERE NOT EXISTS (SELECT 1 FROM atractivos_turisticos WHERE id=1);
