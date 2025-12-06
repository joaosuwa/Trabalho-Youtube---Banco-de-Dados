CREATE TABLE Conta (
    id_conta VARCHAR(255) PRIMARY KEY,
    e_mail VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255) UNIQUE NOT NULL,
    foto_perfil VARCHAR(255),
    data_criacao DATE NOT NULL
);

CREATE TABLE Canal (
    id_canal VARCHAR(255) PRIMARY KEY,
    id_conta VARCHAR(255) NOT NULL,
    nome VARCHAR(255) UNIQUE NOT NULL,
    visualizacoes BIGINT NOT NULL,
    descricao VARCHAR(255),
    foto_canal VARCHAR(255),
    inscritos INT NOT NULL,

    FOREIGN KEY (id_conta) REFERENCES Conta(id_conta)
);

CREATE TABLE Inscricao (
    id_conta VARCHAR(255) NOT NULL,
    id_canal VARCHAR(255) NOT NULL,
    membro BOOLEAN NOT NULL DEFAULT FALSE, 

    PRIMARY KEY (id_conta, id_canal), 
    FOREIGN KEY (id_conta) REFERENCES Conta(id_conta),
    FOREIGN KEY (id_canal) REFERENCES Canal(id_canal)
);

CREATE TABLE Publicacao (
    id_publicacao VARCHAR(255) PRIMARY KEY,
    id_canal VARCHAR(255) NOT NULL,
    data_publicacao DATE NOT NULL,
    likes INT NOT NULL DEFAULT 0,
    dislikes INT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_canal) REFERENCES Canal(id_canal)
);

CREATE TABLE Curtida (
    id_conta VARCHAR(255) NOT NULL,
    id_publicacao VARCHAR(255) NOT NULL,
    dislike BOOLEAN NOT NULL, 
    PRIMARY KEY (id_conta, id_publicacao),
    FOREIGN KEY (id_conta) REFERENCES Conta(id_conta),
    FOREIGN KEY (id_publicacao) REFERENCES Publicacao(id_publicacao)
);

CREATE TABLE Comentario (
    id_publicacao VARCHAR(255) PRIMARY KEY, 
    id_publicacao_comentada VARCHAR(255) NOT NULL,
    conteudo VARCHAR(500) NOT NULL,
    FOREIGN KEY (id_publicacao) REFERENCES Publicacao(id_publicacao),
    FOREIGN KEY (id_publicacao_comentada) REFERENCES Publicacao(id_publicacao)
);

CREATE TABLE Video (
    id_publicacao VARCHAR(255) PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descricao VARCHAR(500) NOT NULL,
    FOREIGN KEY (id_publicacao) REFERENCES Publicacao(id_publicacao)
);

CREATE TABLE TAG (
    id_tag VARCHAR(255) PRIMARY KEY,
    nome VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Anuncio (
    id_empresa VARCHAR(255) PRIMARY KEY,
    url_empresa VARCHAR(255) UNIQUE NOT NULL,
    nome_empresa VARCHAR(255) UNIQUE NOT NULL,
    duracao INT NOT NULL,
    pode_pular BOOLEAN NOT NULL
);

CREATE TABLE Tags_Video (
    id_tag VARCHAR(255) NOT NULL,
    id_publicacao VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_tag, id_publicacao),
    FOREIGN KEY (id_tag) REFERENCES TAG (id_tag),
    FOREIGN KEY (id_publicacao) REFERENCES Video (id_publicacao)
);

CREATE TABLE Anuncio_Video (
    id_empresa VARCHAR(255) NOT NULL,
    id_publicacao VARCHAR(255) NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (id_empresa, id_publicacao),
    FOREIGN KEY (id_empresa) REFERENCES Anuncio (id_empresa),
    FOREIGN KEY (id_publicacao) REFERENCES Video (id_publicacao)
);


CREATE TABLE Video_Normal (
    id_publicacao VARCHAR(255) PRIMARY KEY, 
    duracao INT NOT NULL,
    visualizacoes BIGINT NOT NULL,
    FOREIGN KEY (id_publicacao) REFERENCES Video(id_publicacao)
);

CREATE TABLE Livestream (
    id_publicacao VARCHAR(255) PRIMARY KEY, 
    duracao INT,
    numero_viewers BIGINT NOT NULL,
    FOREIGN KEY (id_publicacao) REFERENCES Video(id_publicacao)
);

CREATE TABLE Doacao (
    id_conta VARCHAR(255) NOT NULL,
    id_publicacao VARCHAR(255) NOT NULL, 
    quantia NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (id_conta, id_publicacao),
    FOREIGN KEY (id_conta) REFERENCES Conta(id_conta),
    FOREIGN KEY (id_publicacao) REFERENCES Livestream(id_publicacao) 
);

CREATE TABLE Playlist (
    id_playlist VARCHAR(255) PRIMARY KEY,
    id_canal VARCHAR(255) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    numero_videos INT NOT NULL,
    FOREIGN KEY (id_canal) REFERENCES Canal(id_canal)
);

CREATE TABLE Playlist_Videos (
    id_playlist VARCHAR(255) NOT NULL,
    id_publicacao VARCHAR(255) NOT NULL, 
    PRIMARY KEY (id_playlist, id_publicacao),
    FOREIGN KEY (id_playlist) REFERENCES Playlist (id_playlist),
    FOREIGN KEY (id_publicacao) REFERENCES Video_Normal (id_publicacao)
);

CREATE OR REPLACE FUNCTION atualiza_reacao()
RETURNS trigger AS $$
BEGIN
    IF NEW.dislike = TRUE THEN
        UPDATE Publicacao
        SET dislikes = dislikes + 1
        WHERE id_publicacao = NEW.id_publicacao;
    ELSE
        UPDATE Publicacao
        SET likes = likes + 1
        WHERE id_publicacao = NEW.id_publicacao;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualiza_reacao
AFTER INSERT ON Curtida
FOR EACH ROW
EXECUTE FUNCTION atualiza_reacao();

INSERT INTO Conta (id_conta, e_mail, nome, foto_perfil, data_criacao) VALUES
('C001', 'alice.silva@email.com', 'Alice Silva', NULL, '2024-01-15'),
('C002', 'bruno.costa@email.com', 'Bruno Costa', 'http://url.com/b_costa.png', '2023-11-20'),
('C003', 'carla.ferr@email.com', 'Carla Ferreira', 'http://url.com/c_ferr.png', '2024-05-01'),
('C004', 'davi.santos@email.com', 'Davi Santos', NULL, '2023-08-10'),
('C005', 'elena.oliveira@email.com', 'Elena Oliveira', 'http://url.com/e_oli.png', '2024-03-25'),
('C006', 'fabio.pereira@email.com', 'Fábio Pereira', 'http://url.com/f_pereira.png', '2023-05-18'),
('C007', 'gisele.rodrigues@email.com', 'Gisele Rodrigues', NULL, '2024-06-05'),
('C008', 'hugo.almeida@email.com', 'Hugo Almeida', 'http://url.com/h_almeida.png', '2023-02-01'),
('C009', 'isabela.gomes@email.com', 'Isabela Gomes', 'http://url.com/i_gomes.png', '2024-02-14'),
('C010', 'joao.martins@email.com', 'João Martins', NULL, '2023-10-30'),
('C011', 'lucas.ribeiro@email.com', 'Lucas Ribeiro', NULL, '2024-07-10');


INSERT INTO Canal (id_canal, id_conta, nome, visualizacoes, descricao, foto_canal, inscritos) VALUES
('KNL01', 'C001', 'Receitas da Alice', 150000, 'Culinária simples e rápida para o dia a dia.', 'http://url.com/fa_food.png', 5000),
('KNL02', 'C005', 'Dicas da Elena Fit', 5000000, 'Treinos e rotinas de vida saudável.', 'http://url.com/fit_elena.png', 120000),
('KNL03', 'C002', 'História do Mundo', 80000, 'Documentários e fatos históricos.', NULL, 2500),
('KNL04', 'C008', 'Desenho Técnico HP', 1200000, 'Aulas e tutoriais de desenho.', 'http://url.com/hugo_desenho.png', 45000),
('KNL05', 'C003', 'Viagens C&F', 950000, 'Guia de viagens e mochilão.', 'http://url.com/viagem_c.png', 30000),
('KNL06', 'C010', 'Games do João', 3000000, 'Gameplay e reviews de novos jogos.', NULL, 80000),
('KNL07', 'C006', 'Música e Arte FP', 25000, 'Covers de violão e arte digital.', 'http://url.com/fabio_art.png', 1500),
('KNL08', 'C009', 'Beleza da Bela', 1500000, 'Tutoriais de maquiagem e cuidados com a pele.', 'http://url.com/bela_make.png', 60000);

INSERT INTO Inscricao (id_conta, id_canal, membro) VALUES
('C001', 'KNL01', TRUE),
('C001', 'KNL02', FALSE),
('C002', 'KNL03', TRUE),
('C002', 'KNL04', FALSE),
('C003', 'KNL05', TRUE),
('C004', 'KNL01', FALSE),
('C004', 'KNL06', TRUE),
('C005', 'KNL02', TRUE),
('C005', 'KNL08', FALSE),
('C006', 'KNL07', TRUE),
('C007', 'KNL05', FALSE),
('C007', 'KNL04', FALSE),
('C008', 'KNL04', TRUE),
('C008', 'KNL01', TRUE),
('C009', 'KNL08', TRUE),
('C009', 'KNL07', FALSE),
('C010', 'KNL06', TRUE),
('C010', 'KNL03', FALSE),
('C003', 'KNL02', TRUE),
('C004', 'KNL07', FALSE);

INSERT INTO Publicacao (id_publicacao, id_canal, data_publicacao, likes, dislikes) VALUES
('PBL_A1', 'KNL01', '2025-11-21', 950, 20), 
('PBL_B1', 'KNL02', '2025-11-19', 25000, 450),
('PBL_D1', 'KNL04', '2025-11-17', 5000, 100),
('PBL_E1', 'KNL05', '2025-11-16', 1800, 75),
('PBL_F1', 'KNL06', '2025-11-15', 30000, 800),
('PBL_H1', 'KNL08', '2025-11-12', 10000, 250),
('PBL_LIVE01', 'KNL06', '2025-11-22', 1200, 35),
('PBL_A2', 'KNL01', '2025-11-20', 1500, 15),
('PBL_C1', 'KNL03', '2025-11-18', 120, 5), 
('PBL_F2', 'KNL06', '2025-11-14', 15000, 350),
('PBL_G1', 'KNL07', '2025-11-13', 45, 1),
('PBL_TEC01', 'KNL04', '2025-11-23', 4200, 50),   -- Canal de Desenho Técnico (Hugo)
('PBL_TEC02', 'KNL06', '2025-11-23', 18000, 300), -- Canal de Games (João)
('PBL_TEC03', 'KNL03', '2025-11-22', 900, 20),    -- Canal de História (Bruno)
('PBL_TEC04', 'KNL08', '2025-11-22', 7500, 180),  -- Canal da Isabela (Beleza)
('PBL_V01', 'KNL01', '2025-11-23', 320, 12),  -- Alice (culinária)
('PBL_V02', 'KNL02', '2025-11-22', 18000, 300), -- Elena Fit
('PBL_V03', 'KNL03', '2025-11-20', 210, 9), -- História do Mundo
('PBL_V04', 'KNL06', '2025-11-23', 12000, 220), -- João Games
('PBL_V05', 'KNL07', '2025-11-21', 70, 2), -- Fábio Música & Arte
('PBL_V06', 'KNL08', '2025-11-22', 5000, 130), -- Isabela Beleza
('PBL_LIVE02', 'KNL05', '2025-11-23', 900, 30),  -- Carla, live finalizada
('PBL_LIVE03', 'KNL04', '2025-11-23', 1100, 22),  -- Hugo — live ainda rolando (duracao = NULL)
('PBL_AD11', 'KNL02', '2025-11-10', 8000, 120),
('PBL_AD12', 'KNL03', '2025-11-09', 4300, 50),
('PBL_AD13', 'KNL04', '2025-11-08', 1500, 25),
('PBL_AD14', 'KNL06', '2025-11-07', 22000, 400);

INSERT INTO Curtida (id_conta, id_publicacao, dislike) VALUES
('C001', 'PBL_A1', FALSE),
('C001', 'PBL_B1', FALSE),
('C001', 'PBL_C1', TRUE),
('C001', 'PBL_F1', FALSE),
('C002', 'PBL_D1', FALSE),
('C002', 'PBL_E1', FALSE),
('C002', 'PBL_H1', TRUE),
('C003', 'PBL_A2', FALSE),
('C003', 'PBL_C1', FALSE),
('C003', 'PBL_F2', FALSE),
('C004', 'PBL_A1', TRUE),
('C004', 'PBL_D1', FALSE),
('C004', 'PBL_H1', FALSE),
('C005', 'PBL_B1', FALSE),
('C005', 'PBL_E1', TRUE),
('C005', 'PBL_G1', FALSE),
('C006', 'PBL_F1', FALSE),
('C006', 'PBL_D1', FALSE),
('C006', 'PBL_C1', TRUE),
('C007', 'PBL_A2', FALSE),
('C007', 'PBL_B1', TRUE),
('C007', 'PBL_F2', FALSE),
('C008', 'PBL_D1', FALSE),
('C008', 'PBL_A1', FALSE),
('C008', 'PBL_E1', FALSE),
('C009', 'PBL_H1', FALSE),
('C009', 'PBL_G1', FALSE),
('C009', 'PBL_F1', TRUE),
('C010', 'PBL_F2', FALSE),
('C010', 'PBL_B1', FALSE),
('C010', 'PBL_A2', TRUE),
('C010', 'PBL_LIVE01', FALSE),
('C001', 'PBL_LIVE01', FALSE),
('C004', 'PBL_LIVE01', FALSE),
('C009', 'PBL_LIVE01', TRUE),
('C011', 'PBL_F1', FALSE),
('C011', 'PBL_F2', FALSE),
('C011', 'PBL_LIVE01', FALSE),
('C011', 'PBL_TEC02', FALSE),
('C011', 'PBL_V04', FALSE);

INSERT INTO Comentario (id_publicacao, id_publicacao_comentada, conteudo) VALUES
('PBL_A2', 'PBL_A1', 'Muito bom esse vídeo, parabéns!'),
('PBL_C1', 'PBL_D1', 'Gostei da explicação, bem clara.'),
('PBL_F2', 'PBL_F1', 'Review top demais!'),
('PBL_G1', 'PBL_E1', 'Vídeo bem interessante, adorei!');

INSERT INTO Video (id_publicacao, titulo, descricao) VALUES
('PBL_A1', 'Bolo de Cenoura Fácil', 'Receita simples e rápida para o café da tarde.'),
('PBL_B1', 'Treino HIIT 15 Minutos', 'Rotina intensa de exercícios para queimar calorias.'),
('PBL_D1', 'Introdução ao Desenho Técnico', 'Primeiros passos para iniciantes.'),
('PBL_E1', 'Mochilão pela Noruega', 'Roteiro completo de viagem.'),
('PBL_F1', 'Review do Novo GameBox X', 'Análise completa do console.'),
('PBL_H1', 'Maquiagem para Noite', 'Tutorial com técnicas para festas.'),
('PBL_LIVE01', 'Live jogando Elden Ring - Parte 3', 'Explorando a nova expansão e enfrentando bosses ao vivo'),
('PBL_TEC01', 'Introdução ao CAD 3D', 'Aprenda os princípios de modelagem 3D.'),
('PBL_TEC02', 'O futuro dos gráficos RTX', 'Análise técnica sobre tecnologias gráficas.'),
('PBL_TEC03', 'Tecnologia na Idade Industrial', 'Impacto da tecnologia na História moderna.'),
('PBL_TEC04', 'A tecnologia por trás dos filtros de maquiagem', 
 'Explicando o funcionamento de filtros e algoritmos.'),
 ('PBL_V01', 'Receita de Lasanha Fácil', 'Aprenda a preparar uma lasanha deliciosa em menos de 30 minutos.'),
('PBL_V02', 'Treino HIIT Intenso', 'Sessão completa de HIIT para perder gordura rapidamente.'),
('PBL_V03', 'A Queda do Império Romano', 'Um resumo didático sobre os fatores que levaram ao fim do Império Romano.'),
('PBL_V04', 'Review: Elden Ring 2', 'Uma análise detalhada do novo lançamento da FromSoftware.'),
('PBL_V05', 'Cover ao Violão - Música Autoral', 'Apresentação exclusiva de uma composição própria.'),
('PBL_V06', 'Maquiagem para Festas', 'Tutorial com dicas de maquiagem para eventos noturnos.'),

('PBL_LIVE02', 'Live: Mochilão na Europa', 'Carla responde perguntas sobre viagens internacionais.'),
('PBL_LIVE03', 'Live: Aula de Desenho Técnico', 'Hugo está ensinando perspectiva ao vivo.'),
('PBL_AD11', 'Rotina Fit Completa', 'Dia completo de treinos e alimentação.'),
('PBL_AD12', 'Guerras Antigas Resumidas', 'Resumo animado das maiores guerras.'),
('PBL_AD13', 'Perspectiva Isométrica', 'Aula sobre técnicas de desenho técnico.'),
('PBL_AD14', 'Review do Novo Game X', 'Review do maior lançamento do ano.');


INSERT INTO TAG (id_tag, nome) VALUES
('T01', 'Culinária'),
('T02', 'Fitness'),
('T03', 'Educação'),
('T04', 'Viagem'),
('T05', 'Games'),
('T06', 'Maquiagem'),
('TG_TEC', 'Tecnologia');

INSERT INTO Anuncio (id_empresa, url_empresa, nome_empresa, duracao, pode_pular) VALUES
('EMP01', 'http://ads.com/profood', 'ProFood', 15, TRUE),
('EMP02', 'http://ads.com/fitlife', 'FitLife', 30, FALSE),
('EMP03', 'http://ads.com/travelplus', 'TravelPlus', 20, TRUE),
('EMP001', 'http://empresa1.com', 'TechPlus', 30, TRUE),
('EMP002', 'http://empresa2.com', 'MegaShop', 45, FALSE);

INSERT INTO Tags_Video (id_tag, id_publicacao) VALUES
('T01', 'PBL_A1'),
('T02', 'PBL_B1'),
('T03', 'PBL_D1'),
('T04', 'PBL_E1'),
('T05', 'PBL_F1'),
('T06', 'PBL_H1'),
('TG_TEC', 'PBL_TEC01'),
('TG_TEC', 'PBL_TEC02'),
('TG_TEC', 'PBL_TEC03'),
('TG_TEC', 'PBL_TEC04');

INSERT INTO Anuncio_Video (id_empresa, id_publicacao, valor) VALUES
('EMP01', 'PBL_A1', 150.00),
('EMP02', 'PBL_B1', 900.00),
('EMP03', 'PBL_E1', 650.00),
('EMP01', 'PBL_F1', 200.00),
('EMP001', 'PBL_AD11', 1500.00),
('EMP001', 'PBL_AD12', 1800.00),
('EMP001', 'PBL_AD13', 2100.00),
('EMP001', 'PBL_AD14', 3200.00),
('EMP002', 'PBL_AD11', 1200.00),
('EMP002', 'PBL_AD12', 950.00);

INSERT INTO Video_Normal (id_publicacao, duracao, visualizacoes) VALUES
('PBL_A1', 420, 150000),
('PBL_D1', 600, 1200000),
('PBL_E1', 900, 950000),
('PBL_H1', 480, 1500000),
('PBL_TEC01', 540, 150000),
('PBL_TEC02', 780, 900000),
('PBL_TEC03', 360, 30000),
('PBL_TEC04', 420, 220000),
('PBL_V01', 540, 25000),
('PBL_V02', 900, 800000),
('PBL_V03', 780, 35000),
('PBL_V04', 1020, 500000),
('PBL_V05', 240, 12000),
('PBL_V06', 600, 90000);


INSERT INTO Livestream (id_publicacao, duracao, numero_viewers) VALUES
('PBL_B1', 3600, 25000),
('PBL_F1', 5400, 30000),
('PBL_LIVE01', NULL, 8200),
('PBL_LIVE02', 7200, 1500),
('PBL_LIVE03', NULL, 3800);

INSERT INTO Doacao (id_conta, id_publicacao, quantia) VALUES
('C001', 'PBL_B1', 10.00),
('C004', 'PBL_F1', 25.50),
('C009', 'PBL_F1', 5.00),
('C007', 'PBL_B1', 3.00);

INSERT INTO Playlist (id_playlist, id_canal, titulo, numero_videos) VALUES
('PL01', 'KNL01', 'Sobremesas Rápidas', 2),
('PL02', 'KNL05', 'Viagens Europa', 2),
('PL03', 'KNL08', 'Make para Iniciantes', 1);

INSERT INTO Playlist_Videos (id_playlist, id_publicacao) VALUES
('PL01', 'PBL_A1'),
('PL01', 'PBL_E1'),
('PL02', 'PBL_E1'),
('PL02', 'PBL_D1'),
('PL03', 'PBL_H1');