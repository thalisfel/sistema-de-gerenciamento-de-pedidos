from flask import request, jsonify, session
from models.database_manager import db

def cadastrar_usuario():
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem cadastrar usuários"}), 403
    
    dados = request.get_json()
    usuario = dados.get('usuario', '').strip()
    senha = dados.get('senha', '')
    tipo = dados.get('tipo', 'gerente')
    
    # Validações básicas
    if not usuario or len(usuario) < 3:
        return jsonify({"erro": "Nome de usuário deve ter no mínimo 3 caracteres"}), 400
    
    if not senha or len(senha) < 6:
        return jsonify({"erro": "Senha deve ter no mínimo 6 caracteres"}), 400
    
    if tipo not in ['admin', 'gerente']:
        return jsonify({"erro": "Tipo de usuário inválido"}), 400
    
    # Cadastrar no banco de dados
    sucesso, mensagem = db.criar_usuario(usuario, senha, tipo)
    
    if sucesso:
        return jsonify({
            "sucesso": True,
            "mensagem": f"Usuário {usuario} cadastrado com sucesso!",
            "usuario": usuario,
            "tipo": tipo
        }), 201
    else:
        return jsonify({"erro": mensagem}), 400

def listar_usuarios():
    """Lista todos os usuários (apenas admin)"""
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem listar usuários"}), 403
    
    usuarios = db.listar_usuarios()
    return jsonify(usuarios), 200

def remover_usuario(usuario):
    """Remove um usuário (apenas admin)"""
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem remover usuários"}), 403
    
    # Não permitir remover a si mesmo
    if usuario == session.get('usuario'):
        return jsonify({"erro": "Você não pode remover sua própria conta"}), 400
    
    # Não permitir remover o último admin
    tipo_usuario = db.get_tipo_usuario(usuario)
    if tipo_usuario == 'admin':
        if db.contar_admins() <= 1:
            return jsonify({"erro": "Não é possível remover o último administrador"}), 400
    
    # Remover do banco
    if db.remover_usuario(usuario):
        return jsonify({"sucesso": True, "mensagem": "Usuário removido com sucesso!"}), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404
