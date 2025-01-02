import sqlite3

# Nome do banco de dados
DB_PATH = "banco_dados.db"

# Função para criar as tabelas
def criar_tabelas():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Criar tabela de dados faciais
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dados_faciais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL UNIQUE,
            hash_encoding TEXT NOT NULL UNIQUE
        );
        """)

        # Criar tabela de registros de ponto
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_ponto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            tipo TEXT NOT NULL,
            sincronizado TEXT NOT NULL
        );
        """)

        # Confirmar mudanças e fechar conexão
        conn.commit()
        print("Tabelas criadas com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        if conn:
            conn.close()

# Executar a função ao rodar o script
if __name__ == "__main__":
    criar_tabelas()
