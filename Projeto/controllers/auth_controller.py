from flask import request, jsonify, session
from models.database_manager import db

def login():
    dados = request.get_json()
    usuario = dados.get('usuario')
    senha = dados.get('senha')
    
    sucesso, tipo = db.verificar_login(usuario, senha)
    
    if sucesso:
        session['autenticado'] = True
        session['usuario'] = usuario
        session['tipo'] = tipo
        session.permanent = True
        return jsonify({
            "sucesso": True,
            "mensagem": f"Bem-vindo, {usuario}!",
            "tipo": tipo
        }), 200
    else:
        return jsonify({
            "sucesso": False,
            "mensagem": "Usuário ou senha inválidos"
        }), 401

def logout():
    session.clear()
    return jsonify({"sucesso": True, "mensagem": "Logout realizado com sucesso"}), 200

def verificar_auth():
    if session.get('autenticado'):
        return jsonify({
            "autenticado": True,
            "usuario": session.get('usuario'),
            "tipo": session.get('tipo', 'gerente')
        }), 200
    return jsonify({"autenticado": False}), 401
