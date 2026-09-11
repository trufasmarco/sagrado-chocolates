from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('loja.db')
    conn.row_factory = sqlite3.Row
    return conn

# Cria a tabela de produtos caso não exista
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            img TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Rota para a loja principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a nova tela de administração/cadastro
@app.route('/admin')
def admin():
    return render_template('admin.html')

# API REST: Listar todos os produtos
@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    
    # Converte os dados do banco para um formato que o JavaScript entende (JSON)
    lista = [{'id': p['id'], 'nome': p['nome'], 'preco': p['preco'], 'estoque': p['estoque'], 'img': p['img']} for p in produtos]
    return jsonify(lista)

# API REST: Cadastrar novo produto
@app.route('/api/produtos', methods=['POST'])
def cadastrar_produto():
    dados = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO produtos (nome, preco, estoque, img) VALUES (?, ?, ?, ?)',
                 (dados['nome'], float(dados['preco']), int(dados['estoque']), dados['img']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'sucesso', 'mensagem': 'Produto cadastrado com sucesso!'}), 201

if __name__ == '__main__':
    init_db()
    # host='0.0.0.0' permite que a aplicação seja acessada pelo celular na mesma rede Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)
