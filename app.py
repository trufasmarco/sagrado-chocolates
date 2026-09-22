import os
import json
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)
# Permitir imagens de até 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# SENHA DO ADMINISTRADOR
SENHA_ADMIN = os.environ.get("SENHA_ADMIN", "123456")

# DADOS DO PIX DO VENDEDOR
CHAVE_PIX_DEFAULT = os.environ.get("CHAVE_PIX", "sagradochocolates@gmail.com")
NOME_BENEFICIARIO = os.environ.get("NOME_BENEFICIARIO", "Sagrado Chocolates")

# URL do PostgreSQL (Railway / Neon)
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://neondb_owner:npg_aVBCmlS03XkO@ep-lingering-haze-ax7ral1g-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Tabela de Produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                produto TEXT NOT NULL,
                valor REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                img TEXT NOT NULL,
                imagens TEXT,
                categoria TEXT DEFAULT 'classicos',
                descricao TEXT DEFAULT '',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        try:
            cursor.execute('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS imagens TEXT;')
            cursor.execute('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS categoria TEXT DEFAULT \'classicos\';')
            cursor.execute('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS descricao TEXT DEFAULT \'\';')
            cursor.execute('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP;')
        except Exception:
            conn.rollback()

        # 2. Tabela de Usuários / Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                telefone TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # 3. Tabela de Fiados / Débitos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiados (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                valor REAL NOT NULL,
                descricao TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                comprovante TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pago_em TIMESTAMP
            );
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Aviso na inicialização do banco: {e}")

# ================= TRATAMENTO GLOBAL DE ERROS VISÍVEL =================

@app.errorhandler(500)
def erro_interno_servidor(e):
    erro_detalhado = traceback.format_exc()
    print("ERRO CRITICO 500:\n", erro_detalhado)
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Diagnóstico de Erro | Sagrado Chocolates</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #120505; color: #ffcccc; padding: 1.5rem; margin: 0; }}
            .card {{ background: #260c0c; border: 2px solid #e53e3e; border-radius: 12px; padding: 1.5rem; max-width: 800px; margin: 0 auto; }}
            h2 {{ color: #fc8181; margin-top: 0; }}
            pre {{ background: #150505; color: #fbd38d; padding: 1rem; border-radius: 8px; border: 1px solid #742a2a; overflow-x: auto; font-size: 13px; line-height: 1.4; }}
            .dica {{ background: #2d1810; border-left: 4px solid #d69e2e; padding: 0.8rem; margin: 1rem 0; color: #fefcbf; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>⚠️ Erro Identificado no Servidor (Modo Diagnóstico)</h2>
            <p>Ocorreu uma falha na execução. Veja os detalhes exatos abaixo para correção:</p>
            <div class="dica">
                <strong>Dica:</strong> Se o erro indicar conexão com banco (PostgreSQL), verifique a variável DATABASE_URL no Railway. Se indicar erro de template, verifique as tags do Jinja2.
            </div>
            <pre>{erro_detalhado if erro_detalhado.strip() else str(e)}</pre>
            <p style="text-align: center; margin-top: 1.5rem;">
                <a href="/" style="color: #63b3ed; text-decoration: none; font-weight: bold;">Tentar Recarregar Página</a>
            </p>
        </div>
    </body>
    </html>
    """, 500

# ================= ROTAS DE PÁGINAS COM DIAGNÓSTICO =================

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print("ERRO AO CARREGAR index.html:\n", erro_detalhado)
        return erro_interno_servidor(e)

@app.route('/admin')
def admin():
    try:
        return render_template('admin.html')
    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print("ERRO AO CARREGAR admin.html:\n", erro_detalhado)
        return erro_interno_servidor(e)

# ================= ROTAS DE PRODUTOS =================

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos ORDER BY id DESC')
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        lista = []
        for p in produtos:
            imagens_list = []
            if p.get('imagens'):
                try:
                    imagens_list = json.loads(p['imagens'])
                except Exception:
                    imagens_list = [p['img']]
            elif p.get('img'):
                imagens_list = [p['img']]

            lista.append({
                'id': p['id'], 
                'nome': p['produto'], 
                'preco': float(p['valor']), 
                'estoque': int(p['quantidade']), 
                'img': p.get('img') or (imagens_list[0] if imagens_list else ''),
                'imagens': imagens_list,
                'categoria': p.get('categoria', 'classicos'),
                'descricao': p.get('descricao', '')
            })
        return jsonify(lista)
    except Exception as e:
        erro = traceback.format_exc()
        print(f"Erro ao listar produtos: {erro}")
        return jsonify({'erro': str(e), 'detalhes': erro}), 500

@app.route('/api/produtos', methods=['POST'])
def cadastrar_produto():
    try:
        dados = request.json
        if not dados or not dados.get('nome') or not dados.get('preco'):
            return jsonify({'erro': 'Nome e preço são obrigatórios!'}), 400

        nome = dados.get('nome')
        preco = float(dados.get('preco'))
        estoque = int(dados.get('estoque', 0))
        categoria = dados.get('categoria', 'classicos')
        descricao = dados.get('descricao', '')
        
        imagens = dados.get('imagens', [])
        if isinstance(imagens, str):
            imagens = [imagens]
        
        imagens = imagens[:4] if imagens else []
        img_principal = dados.get('img') or (imagens[0] if imagens else '')
        if not imagens and img_principal:
            imagens = [img_principal]
            
        imagens_json = json.dumps(imagens)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO produtos (produto, valor, quantidade, img, imagens, categoria, descricao) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (nome, preco, estoque, img_principal, imagens_json, categoria, descricao)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'sucesso', 'mensagem': 'Produto cadastrado com sucesso!'}), 201
    except Exception as e:
        erro = traceback.format_exc()
        return jsonify({'erro': str(e), 'detalhes': erro}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def excluir_produto(produto_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = %s', (produto_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'sucesso', 'mensagem': 'Produto excluído!'})
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

# ================= AUTENTICAÇÃO DO CLIENTE =================

@app.route('/api/cliente/cadastro', methods=['POST'])
def cadastrar_cliente():
    try:
        dados = request.json or {}
        nome = (dados.get('nome') or '').strip()
        email = (dados.get('email') or '').strip().lower()
        senha = (dados.get('senha') or '').strip()
        telefone = (dados.get('telefone') or '').strip()

        if not nome or not email or not senha:
            return jsonify({'erro': 'Nome, e-mail e senha são obrigatórios!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'erro': 'Já existe uma conta com este e-mail!'}), 400

        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha, telefone) VALUES (%s, %s, %s, %s) RETURNING id, nome, email, telefone',
            (nome, email, senha, telefone)
        )
        usuario = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'sucesso',
            'mensagem': 'Conta criada com sucesso!',
            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'telefone': usuario['telefone']
            }
        }), 201
    except Exception as e:
        return jsonify({'erro': f'Erro ao criar conta: {str(e)}', 'detalhes': traceback.format_exc()}), 500

@app.route('/api/cliente/login', methods=['POST'])
def login_cliente():
    try:
        dados = request.json or {}
        email = (dados.get('email') or '').strip().lower()
        senha = (dados.get('senha') or '').strip()

        if not email or not senha:
            return jsonify({'erro': 'E-mail e senha são obrigatórios!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, email, senha, telefone FROM usuarios WHERE email = %s', (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if not usuario or usuario['senha'] != senha:
            return jsonify({'erro': 'E-mail ou senha incorretos!'}), 401

        return jsonify({
            'status': 'sucesso',
            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'telefone': usuario['telefone']
            }
        })
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

# ================= FIADO (CLIENTE) =================

@app.route('/api/cliente/fiados', methods=['GET'])
def listar_fiados_cliente():
    usuario_id = request.args.get('usuario_id')
    if not usuario_id:
        return jsonify({'erro': 'usuario_id obrigatório'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, valor, descricao, status, comprovante, criado_em, pago_em 
               FROM fiados 
               WHERE usuario_id = %s 
               ORDER BY id DESC''',
            (usuario_id,)
        )
        fiados = cursor.fetchall()
        cursor.close()
        conn.close()

        lista = []
        for f in fiados:
            lista.append({
                'id': f['id'],
                'valor': float(f['valor']),
                'descricao': f['descricao'],
                'status': f['status'],
                'tem_comprovante': bool(f['comprovante']),
                'criado_em': f['criado_em'].strftime('%d/%m/%Y %H:%M') if f['criado_em'] else '',
                'pago_em': f['pago_em'].strftime('%d/%m/%Y %H:%M') if f['pago_em'] else ''
            })
        return jsonify(lista)
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

@app.route('/api/cliente/fiados/anexar-comprovante', methods=['POST'])
def anexar_comprovante_cliente():
    try:
        dados = request.json or {}
        fiado_id = dados.get('fiado_id')
        comprovante = dados.get('comprovante')

        if not fiado_id or not comprovante:
            return jsonify({'erro': 'fiado_id e comprovante são obrigatórios!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE fiados 
               SET status = 'comprovante_enviado', comprovante = %s 
               WHERE id = %s AND status = 'pendente' ''',
            (comprovante, fiado_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'sucesso', 'mensagem': 'Comprovante enviado com sucesso para conferência do vendedor!'})
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

# ================= ADMIN =================

@app.route('/api/login', methods=['POST'])
def login_admin():
    dados = request.json
    if dados and dados.get('senha') == SENHA_ADMIN:
        return jsonify({'status': 'sucesso'}), 200
    return jsonify({'erro': 'Senha de administrador incorreta!'}), 401

@app.route('/api/admin/info-pix', methods=['GET'])
def info_pix():
    return jsonify({
        'chave_pix': CHAVE_PIX_DEFAULT,
        'beneficiario': NOME_BENEFICIARIO
    })

@app.route('/api/admin/clientes', methods=['GET'])
def admin_listar_clientes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                u.id, 
                u.nome, 
                u.email, 
                u.telefone, 
                u.criado_em,
                COALESCE(SUM(CASE WHEN f.status != 'pago' THEN f.valor ELSE 0 END), 0) AS total_devendo,
                COUNT(CASE WHEN f.status = 'comprovante_enviado' THEN 1 END) AS comprovantes_pendentes
            FROM usuarios u
            LEFT JOIN fiados f ON u.id = f.usuario_id
            GROUP BY u.id, u.nome, u.email, u.telefone, u.criado_em
            ORDER BY u.nome ASC
        ''')
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()

        lista = []
        for c in clientes:
            lista.append({
                'id': c['id'],
                'nome': c['nome'],
                'email': c['email'],
                'telefone': c['telefone'] or 'Não informado',
                'total_devendo': float(c['total_devendo']),
                'comprovantes_pendentes': int(c['comprovantes_pendentes']),
                'data_cadastro': c['criado_em'].strftime('%d/%m/%Y') if c['criado_em'] else ''
            })
        return jsonify(lista)
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

@app.route('/api/admin/fiados', methods=['GET'])
def admin_listar_fiados():
    cliente_id = request.args.get('cliente_id')
    status_filtro = request.args.get('status')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT 
                f.id, 
                f.usuario_id, 
                u.nome AS cliente_nome, 
                u.email AS cliente_email,
                u.telefone AS cliente_telefone,
                f.valor, 
                f.descricao, 
                f.status, 
                f.comprovante, 
                f.criado_em, 
                f.pago_em
            FROM fiados f
            JOIN usuarios u ON f.usuario_id = u.id
            WHERE 1=1
        '''
        params = []
        if cliente_id:
            query += ' AND f.usuario_id = %s'
            params.append(cliente_id)
        if status_filtro:
            query += ' AND f.status = %s'
            params.append(status_filtro)

        query += ' ORDER BY f.id DESC'
        cursor.execute(query, tuple(params))
        fiados = cursor.fetchall()
        cursor.close()
        conn.close()

        lista = []
        for f in fiados:
            lista.append({
                'id': f['id'],
                'usuario_id': f['usuario_id'],
                'cliente_nome': f['cliente_nome'],
                'cliente_email': f['cliente_email'],
                'cliente_telefone': f['cliente_telefone'],
                'valor': float(f['valor']),
                'descricao': f['descricao'],
                'status': f['status'],
                'tem_comprovante': bool(f['comprovante']),
                'comprovante': f['comprovante'],
                'criado_em': f['criado_em'].strftime('%d/%m/%Y %H:%M') if f['criado_em'] else '',
                'pago_em': f['pago_em'].strftime('%d/%m/%Y %H:%M') if f['pago_em'] else ''
            })
        return jsonify(lista)
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

@app.route('/api/admin/fiados', methods=['POST'])
def admin_adicionar_fiado():
    try:
        dados = request.json or {}
        usuario_id = dados.get('usuario_id')
        valor = float(dados.get('valor', 0))
        descricao = (dados.get('descricao') or 'Consumo de cones trufados').strip()

        if not usuario_id or valor <= 0:
            return jsonify({'erro': 'Usuário e valor válido maior que zero são obrigatórios!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO fiados (usuario_id, valor, descricao, status) 
               VALUES (%s, %s, %s, 'pendente') RETURNING id''',
            (usuario_id, valor, descricao)
        )
        fiado_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'sucesso', 'mensagem': 'Valor de fiado registrado com sucesso!', 'fiado_id': fiado_id}), 201
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

@app.route('/api/admin/fiados/<int:fiado_id>/status', methods=['POST'])
def admin_atualizar_status_fiado(fiado_id):
    try:
        dados = request.json or {}
        novo_status = dados.get('status')

        if novo_status not in ['pago', 'pendente', 'comprovante_enviado', 'recusado']:
            return jsonify({'erro': 'Status inválido!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        if novo_status == 'pago':
            cursor.execute(
                'UPDATE fiados SET status = %s, pago_em = CURRENT_TIMESTAMP WHERE id = %s',
                (novo_status, fiado_id)
            )
        else:
            cursor.execute(
                'UPDATE fiados SET status = %s WHERE id = %s',
                (novo_status, fiado_id)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'sucesso', 'mensagem': f'Status alterado para {novo_status}!'})
    except Exception as e:
        return jsonify({'erro': str(e), 'detalhes': traceback.format_exc()}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    try:
        init_db()
    except Exception as e:
        print(f"Erro no init_db global: {e}")
