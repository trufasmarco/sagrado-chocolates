import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
# Enable CORS for all domains so the React frontend can talk to the Flask API
CORS(app)

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
        print(f"Error fetching products: {e}")
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

```text:requirements.txt
Flask==3.0.2
psycopg2-binary==2.9.9
gunicorn==21.2.0
Flask-Cors==4.0.0
```eof

Based on the image you sent of your GitHub repository, it looks like you are currently serving HTML templates directly from Flask (`templates/index.html`, `templates/admin.html`).

When moving to a modern React architecture, especially if you plan to deploy on a service like Vercel (for the frontend) and Railway (for the backend), you need to separate them.

Here is the plan to adapt your repository for this new architecture:

1.  **The Backend (Flask API on Railway):** We need to update your `app.py` to act *only* as an API (JSON data) and stop serving HTML files. We also must add `flask-cors` so your React app can securely request data from it. I have generated the updated `app.py` and `requirements.txt` above.
2.  **The Frontend (React App):** The massive `index_2.html` file you tested previously is a standalone React app bundled into one file (using Babel). This is great for quick tests, but for production, you should create a proper React project (e.g., using Vite) and deploy it separately on Vercel.

**Steps to transition to Railway (Backend):**

1.  **Update GitHub:**
    *   Replace your current `app.py` with the new one generated above. Notice that I removed the `@app.route('/')` and `@app.route('/admin')` that served HTML. It is now a pure API.
    *   Update your `requirements.txt` to include `Flask-Cors==4.0.0`.
    *   You can safely **delete** the `templates` and `static` folders from your GitHub repository if you intend to host the frontend elsewhere (like Vercel). The Flask app no longer needs them.
2.  **Deploy on Railway:**
    *   Log in to [Railway.app](https://railway.app/).
    *   Click "New Project" -> "Deploy from GitHub repo".
    *   Select your `sagrado-chocolates` repository.
    *   Railway will automatically detect the `Procfile` and `requirements.txt` and build your Python environment.
    *   Once deployed, go to the "Settings" tab of your service in Railway, look for "Networking", and click "Generate Domain". This will give you your new API URL (e.g., `[https://sagrado-backend-production.up.railway.app](https://sagrado-backend-production.up.railway.app)`).

**Next Steps for the Frontend:**

Once your Flask API is running on Railway, we need to set up the React frontend. Do you want to continue using that single standalone HTML file (which is easier to host but less professional), or do you want me to guide you through creating a real React project (using Vite) to deploy on Vercel for free?
