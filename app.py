import os
import subprocess
import sys

# Função para verificar e instalar dependências automaticamente (útil para testes locais)
def verificar_e_instalar(pacote, import_nome=None):
    if import_nome is None:
        import_nome = pacote
    try:
        __import__(import_nome)
    except ImportError:
        print(f"Biblioteca '{pacote}' não encontrada. Instalando automaticamente...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])

# Garante que o Flask e o Psycopg2 estejam instalados
verificar_e_instalar("flask")
verificar_e_instalar("psycopg2-binary", "psycopg2")

from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# Sua URL de conexão oficial do Neon.tech
DATABASE_URL = "postgresql://neondb_owner:npg_aVBCmlS03XkO@ep-lingering-haze-ax7ral1g-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Função para conectar ao PostgreSQL na nuvem
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

# Cria a tabela de produtos na nuvem caso ela ainda não exista
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                produto TEXT NOT NULL,
                valor REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                img TEXT NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabela 'produtos' conectada e verificada com sucesso no Neon.tech!")
    except Exception as e:
        print(f"Erro ao criar tabela no Neon: {e}")

# Rota para a loja principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a tela de administração/cadastro
@app.route('/admin')
def admin():
    return render_template('admin.html')

# API REST: Listar todos os produtos da nuvem
@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos')
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        lista = [{
            'id': p['id'], 
            'nome': p['produto'], 
            'preco': p['valor'], 
            'estoque': p['quantidade'], 
            'img': p['img']
        } for p in produtos]
        
        return jsonify(lista)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API REST: Cadastrar novo produto na nuvem
@app.route('/api/produtos', methods=['POST'])
def cadastrar_produto():
    try:
        dados = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO produtos (produto, valor, quantidade, img) VALUES (%s, %s, %s, %s)',
            (dados['nome'], float(dados['preco']), int(dados['estoque']), dados['img'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'sucesso', 'mensagem': 'Produto cadastrado na nuvem com sucesso!'}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    init_db()
    # Pega a porta fornecida pelo Render ou usa 5000 por padrão localmente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
