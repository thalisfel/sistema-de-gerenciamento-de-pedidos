from flask import Flask, render_template, session
from flask_cors import CORS
from datetime import timedelta
import os
from controllers import auth_controller, user_controller, product_controller, order_controller, backup_controller

app = Flask(__name__, 
            template_folder='views/templates',
            static_folder='views/static')

app.secret_key = 'chave-super-secreta-123'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

print("🗄️ Banco de dados SQLite inicializado!")

CORS(app, 
     supports_credentials=True,
     origins=["http://127.0.0.1:5000", "http://localhost:5000", "null"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type"]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/pedidos')
def pedidos_page():
    return render_template('pedidos.html')

@app.route('/cadastrar_produto')
def cadastrar_produto_page():
    return render_template('cadastrar_produto.html')

@app.route('/gerenciar_produto')
def gerenciar_produto_page():
    return render_template('gerenciar_produto.html')

@app.route('/gerenciar_usuarios')
def gerenciar_usuarios_page():
    return render_template('gerenciar_usuarios.html')

@app.route('/cadastro_funcionarios')
def cadastro_funcionarios_page():
    return render_template('cadastro_funcionarios.html')

@app.route('/pagina_inicial')
def pagina_inicial():
    return render_template('pagina_inicial.html')

@app.route('/api/login', methods=['POST'])
def login():
    return auth_controller.login()

@app.route('/api/logout', methods=['POST'])
def logout():
    return auth_controller.logout()

@app.route('/api/verificar-auth', methods=['GET'])
def verificar_auth():
    return auth_controller.verificar_auth()

@app.route('/api/usuarios', methods=['POST'])
def cadastrar_usuario():
    return user_controller.cadastrar_usuario()

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    return user_controller.listar_usuarios()

@app.route('/api/usuarios/<usuario>', methods=['DELETE'])
def remover_usuario(usuario):
    return user_controller.remover_usuario(usuario)

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    return product_controller.listar_produtos()

@app.route('/api/produtos', methods=['POST'])
def criar_produto():
    return product_controller.criar_produto()

@app.route('/api/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    return product_controller.atualizar_produto(id)

@app.route('/api/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    return product_controller.deletar_produto(id)

@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    return order_controller.criar_pedido()

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    return order_controller.listar_pedidos()

@app.route('/api/pedidos/<int:id>/status', methods=['PUT'])
def atualizar_status_pedido(id):
    return order_controller.atualizar_status_pedido(id)

@app.route('/api/pedidos/<int:id>', methods=['DELETE'])
def deletar_pedido(id):
    return order_controller.deletar_pedido(id)

@app.route('/api/estatisticas', methods=['GET'])
def obter_estatisticas():
    return order_controller.obter_estatisticas()

@app.route('/api/lucros', methods=['GET'])
def obter_lucros():
    return order_controller.obter_lucros()

@app.route('/api/pedidos/historico', methods=['GET'])
def listar_historico():
    return order_controller.listar_historico()

@app.route('/api/pedidos/historico', methods=['DELETE'])
def limpar_historico():
    return order_controller.limpar_historico()

@app.route('/api/resetar-ids', methods=['POST'])
def resetar_ids():
    return order_controller.resetar_contadores()

@app.route('/api/backup', methods=['POST'])
def criar_backup():
    return backup_controller.criar_backup()

@app.route('/api/backup/restaurar', methods=['POST'])
def restaurar_backup():
    return backup_controller.restaurar_backup()

@app.route('/api/backup/automatico', methods=['POST'])
def backup_automatico():
    return backup_controller.backup_automatico()

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )