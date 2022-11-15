USE my_database;
DROP TABLE IF EXISTS persona;
CREATE TABLE persona (
	idPersona INT AUTO_INCREMENT,
    nombre VARCHAR(32) NOT NULL,
    cedula VARCHAR(32) NOT NULL,
    PRIMARY KEY (idPersona)
);
DROP TABLE IF EXISTS carro;
CREATE TABLE carro (
	idCarro INT AUTO_INCREMENT,
    color VARCHAR(32) NOT NULL,
    placa VARCHAR(32) NOT NULL,
    persona_id INT,
    PRIMARY KEY (idCarro),
    CONSTRAINT fk_persona
    FOREIGN KEY(persona_id)
    REFERENCES persona(idPersona)
);
INSERT INTO persona (nombre, cedula) VALUES ("test", "1234");
INSERT INTO carro (color, placa, persona_id) VALUES ("rojo", "12345", 1);
SELECT * FROM persona;
SELECT * FROM carro