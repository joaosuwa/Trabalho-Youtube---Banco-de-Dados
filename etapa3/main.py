import psycopg2
import consultas

try:
    con = psycopg2.connect(
        host="localhost",
        database="Youtube",
        user="postgres",
        password="postgres",

        port=5432
    )

    cur = con.cursor()

    # Setar ou dar Update no Trigger
    consultas.cria_trigger(cur)
    con.commit()
    print('Trigger setado')

    consultas.cria_view_estatisticas(cur)
    con.commit()
    print('View criada')

    canal_alvo = "Games do João"
    
    resultados = consultas.tabela_curtidas_feitas_por_canal(cur, canal_alvo)

    print(f"\n=== LISTA DE TUDO QUE O CANAL '{canal_alvo}' CURTIU ===")
    print(f"{'USUÁRIO':<20} | {'ID PUBLICAÇÃO':<15} | {'CANAL DO VÍDEO':<20} | {'REAÇÃO'}")
    print("-" * 75)

    if not resultados:
        print("Esse canal não curtiu nada ainda.")
    else:
        for linha in resultados:
            usuario, id_pub, canal_video, is_dislike = linha
            
            reacao = "DISLIKE" if is_dislike else "LIKE"
            
            print(f"{usuario:<20} | {id_pub:<15} | {canal_video:<20} | {reacao}")

except Exception as erro:
    if con:
        con.rollback()
    print("Erro:", erro)

finally:
    if cur:
        cur.close()
    if con:
        con.close()