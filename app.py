import os
from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# SENHA DO ADMINISTRADOR
SENHA_ADMIN = "123456"

# Sua URL de conexão oficial do Neon.tech
DATABASE_URL = "postgresql://neondb_owner:npg_aVBCmlS03XkO@ep-lingering-haze-ax7ral1g-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

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
        print("Tabela verificada com sucesso!")
    except Exception as e:
        print(f"ERRO CRITICO NO BANCO: {e}")

# Rota para a página principal (Vitrine HTML)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para o painel do vendedor (Admin HTML)
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/login', methods=['POST'])
def login_admin():
    dados = request.json
    if dados and dados.get('senha') == SENHA_ADMIN:
        return jsonify({'status': 'sucesso'}), 200
    return jsonify({'erro': 'Senha incorreta!'}), 401

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
        print(f"Erro ao listar produtos: {e}")
        return jsonify([]), 200

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
        return jsonify({'status': 'sucesso'}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
else:
    try:
        init_db()
    except Exception as e:
        print(f"Erro no init_db global: {e}")
```eof
