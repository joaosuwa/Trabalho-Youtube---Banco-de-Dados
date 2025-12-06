import psycopg2

# Função para a criação do trigger
def cria_trigger(cursor):
    # Função que atualizará a tabela publicao
    sql_funcao = """
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
                """

    # Definição do trigger que atualiza a tabela publicacao toda vez que um INSERT for executado corretamente
    sql_trigger = """
                CREATE OR REPLACE TRIGGER trg_atualiza_reacao
                AFTER INSERT ON Curtida
                FOR EACH ROW
                EXECUTE FUNCTION atualiza_reacao();
                """
    
    try:
        cursor.execute(sql_funcao)
        cursor.execute(sql_trigger)

    except psycopg2.Error as erro:
        print(f"Erro ao configurar trigger: {erro}")
        raise erro


# Tabela mostrando todos os likes/dislikes feitos pelo usuario especificado, identificando também o nome do usuário, 
# o id da publicação que foi curtido pelo usuário e o canal.
def tabela_curtidas_feitas_por_canal(cursor, nome_canal):
    comando = """
    SELECT 
        ct.nome AS usuario,
        cu.id_publicacao,
        can.nome AS canal,  -- Este é o canal DO VÍDEO assistido
        cu.dislike
    FROM Curtida cu
    JOIN Conta ct ON cu.id_conta = ct.id_conta
    JOIN Publicacao p ON cu.id_publicacao = p.id_publicacao
    JOIN Canal can ON p.id_canal = can.id_canal
    -- Join extra para encontrar o canal da pessoa que curtiu
    JOIN Canal c_filtro ON ct.id_conta = c_filtro.id_conta
    WHERE c_filtro.nome = %s;
    """
    
    # Passando o parâmetro de forma segura
    cursor.execute(comando, (nome_canal,))
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela mostrar os vídeos normais com mais visualizações, com informações sobre o titulo, o id, 
# o nome do canal o qual fez o vídeo e a quantidade de vizualizações
def tabela_top_videos(cursor):
    comando = """
    SELECT 
        v.titulo,
        vn.id_publicacao,
        c.nome AS canal,
        vn.visualizacoes
    FROM Video_Normal vn
    JOIN Video v ON vn.id_publicacao = v.id_publicacao
    JOIN Publicacao p ON v.id_publicacao = p.id_publicacao
    JOIN Canal c ON p.id_canal = c.id_canal
    ORDER BY vn.visualizacoes DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela mostrando todas as livestreams registradas com informações adicionais, como o id da live, 
# número de viewers, o titulo da live e o nome do canal o qual está transmitindo.

def tabela_livestreams(cursor):
    comando = """
    SELECT 
        l.id_publicacao,
        l.numero_viewers,
        v.titulo,
        ct.nome AS dono,
        CASE
            WHEN l.duracao IS NULL THEN FALSE
            ELSE TRUE
        END AS terminada
    FROM Livestream l
    JOIN Video v ON l.id_publicacao = v.id_publicacao
    JOIN Publicacao p ON l.id_publicacao = p.id_publicacao
    JOIN Canal c ON p.id_canal = c.id_canal
    JOIN Conta ct ON c.id_conta = ct.id_conta;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela mostrando os usuários que doaram em uma livestream ordenados de forma decrescente do quanto, no total, doaram.

def tabela_maiores_doadores(cursor):
    comando = """
    SELECT 
        ct.nome AS doador,
        l.id_publicacao AS livestream,
        v.titulo,
        SUM(d.quantia) AS total_doado
    FROM Doacao d
    JOIN Conta ct ON d.id_conta = ct.id_conta
    JOIN Livestream l ON d.id_publicacao = l.id_publicacao
    JOIN Video v ON l.id_publicacao = v.id_publicacao
    GROUP BY ct.nome, l.id_publicacao, v.titulo
    ORDER BY total_doado DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado


# Tabela mostrando os canais que mais receberam lucros, em ordem decrescente, 
# a partir de anuncios e doações que receberam em seus vídeos (videos normais + livestreams)
def tabela_lucro_canais(cursor):
    comando = """
    SELECT 
        c.id_canal,
        c.nome AS nome_canal,
        COALESCE(SUM(av.valor), 0) AS total_anuncios,
        COALESCE(SUM(d.quantia), 0) AS total_doacoes,
        COALESCE(SUM(av.valor), 0) + COALESCE(SUM(d.quantia), 0) AS lucro_total
    FROM Canal c
    LEFT JOIN Publicacao p ON p.id_canal = c.id_canal
    LEFT JOIN Video v ON v.id_publicacao = p.id_publicacao
    LEFT JOIN Anuncio_Video av ON av.id_publicacao = v.id_publicacao
    LEFT JOIN Livestream ls ON ls.id_publicacao = p.id_publicacao
    LEFT JOIN Doacao d ON d.id_publicacao = ls.id_publicacao
    GROUP BY c.id_canal, c.nome
    ORDER BY lucro_total DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela mostrando o somatório do total de lucro (em anúncios) para cada TAG, 
# restringindo para que apenas apareça as TAGS que receberam um lucro total superior a 0
def tabela_lucro_por_tag(cursor):
    comando = """
    SELECT
        t.nome AS tag,
        SUM(av.valor) AS total_lucro
    FROM TAG t
    JOIN Tags_Video tv ON t.id_tag = tv.id_tag
    JOIN Anuncio_Video av ON tv.id_publicacao = av.id_publicacao
    GROUP BY t.nome
    HAVING SUM(av.valor) > 0
    ORDER BY total_lucro DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela retornando todos os vídeos que estão entre os 3 mais curtidos de cada canal.
def tabela_top3_videos_por_canal(cursor):
    comando = """
    SELECT 
        v.id_publicacao,
        c.nome AS canal,
        v.titulo,
        p.likes
    FROM Video v
    JOIN Publicacao p ON p.id_publicacao = v.id_publicacao
    JOIN Canal c ON c.id_canal = p.id_canal
    WHERE p.id_publicacao IN (
        -- Subconsulta que retorna os 3 vídeos mais curtidos daquele canal específico
        SELECT p2.id_publicacao
        FROM Publicacao p2
        JOIN Video v2 ON v2.id_publicacao = p2.id_publicacao
        WHERE p2.id_canal = p.id_canal
        ORDER BY p2.likes DESC
        LIMIT 3
    )
    ORDER BY c.id_canal, p.likes DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela mostrando vídeos que possuem anúncios de empresas, sendo que essas empresas devem ter mais que 3 anúncios em vídeos diferentes.
def relatorio_videos_anunciantes_frequentes(cursor):
    comando = """
    SELECT 
        v.id_publicacao,
        v.titulo,
        c.nome AS canal
    FROM Video v
    JOIN Publicacao p ON p.id_publicacao = v.id_publicacao
    JOIN Canal c ON c.id_canal = p.id_canal
    WHERE v.id_publicacao IN (
        SELECT av.id_publicacao
        FROM Anuncio_Video av
        WHERE av.id_empresa IN (
            SELECT id_empresa
            FROM Anuncio_Video
            GROUP BY id_empresa
            HAVING COUNT(*) > 3
        )
    );
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela mostrando os usuários que curtiram todos os videos do "nome_canal"
def tabela_usuarios_super_fas(cursor, nome_canal):
    comando = """
    SELECT conta.id_conta, conta.nome
    FROM Conta conta
    WHERE NOT EXISTS (
        -- Procura se existe algum vídeo do canal que o usuário NÃO curtiu
        SELECT *
        FROM Publicacao p
        JOIN Video v ON v.id_publicacao = p.id_publicacao
        JOIN Canal c ON c.id_canal = p.id_canal
        WHERE c.nome = %s
          AND NOT EXISTS (
                SELECT 1
                FROM Curtida cur
                WHERE cur.id_conta = conta.id_conta
                  AND cur.id_publicacao = p.id_publicacao
          )
    );
    """
    
    # Os parâmetros são enviados como tuplas
    cursor.execute(comando, (nome_canal,))
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Calcula estatisticas importantes para cada canal
def cria_view_estatisticas(cursor):
    comando = """
    CREATE OR REPLACE VIEW vw_estatisticas_canal AS
    SELECT
        c.id_canal,
        c.nome AS nome_canal,
        c.inscritos,
        c.visualizacoes AS visualizacoes_canal,

        COUNT(p.id_publicacao) AS total_publicacoes,
        COUNT(v.id_publicacao) AS total_videos,
        COUNT(cm.id_publicacao) AS total_comentarios,
        SUM(p.likes) AS total_likes,
        SUM(p.dislikes) AS total_dislikes

    FROM Canal c
    LEFT JOIN Publicacao p 
        ON p.id_canal = c.id_canal
    LEFT JOIN Video v
        ON v.id_publicacao = p.id_publicacao
    LEFT JOIN Comentario cm
        ON cm.id_publicacao_comentada = p.id_publicacao

    GROUP BY c.id_canal, c.nome, c.inscritos, c.visualizacoes;
    """

    # Alterei essa linha: ON cm.id_publicacao_comentada = p.id_publicacao
    # ja que estava dando algum erro

    cursor.execute(comando)

# Tabela de canais, os quais estão ordenados pela maior média de likes por vídeo
def tabela_view_ordenada_por_likes(cursor):
    comando = """
    SELECT
        vwe.id_canal,
        vwe.nome_canal,
        ROUND(AVG(p.likes), 2) AS media_likes_por_video
    FROM vw_estatisticas_canal vwe
    JOIN Publicacao p ON p.id_canal = vwe.id_canal
    JOIN Video v ON v.id_publicacao = p.id_publicacao
    GROUP BY vwe.id_canal, vwe.nome_canal
    HAVING COUNT(v.id_publicacao) > 0
    ORDER BY media_likes_por_video DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado

# Tabela de canais com os vídeos mais populares, onde o número de likes deve ser maior que 5000. 
def tabela_videos_populares(cursor):
    comando = """
    SELECT
        vwe.id_canal,
        vwe.nome_canal,
        COUNT(v.id_publicacao) AS videos_populares
    FROM vw_estatisticas_canal vwe
    JOIN Publicacao p ON p.id_canal = vwe.id_canal
    JOIN Video v ON v.id_publicacao = p.id_publicacao
    WHERE p.likes > 5000
    GROUP BY vwe.id_canal, vwe.nome_canal
    ORDER BY videos_populares DESC;
    """
    
    cursor.execute(comando)
    tabela_resultado = cursor.fetchall()
    
    return tabela_resultado