CREATE DATABASE loja_de_jogos;
USE loja_de_jogos;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jogos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    data_lancamento DATE,
    categoria VARCHAR(50),
    imagem VARCHAR(255),
    data_adicionado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pendente', 'concluído', 'cancelado') DEFAULT 'pendente',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);


CREATE TABLE itens_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_jogo INT NOT NULL,
    quantidade INT NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id),
    FOREIGN KEY (id_jogo) REFERENCES jogos(id)
);

INSERT INTO usuarios (nome, email, senha) VALUES
('Gabriel Sanches', 'gabriel@example.com', 'senha123'),
('Ana Silva', 'ana@example.com', 'senha456');


