from flask import request, jsonify, session
from models.database_manager import db

def listar_produtos():
    """Lista todos os produtos (acesso público para clientes)"""
    produtos = db.listar_produtos()
    return jsonify(produtos), 200

def criar_produto():
    """Cria um novo produto"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    dados = request.get_json()
    
    # Validações
    if not dados.get('nome') or not dados.get('descricao') or not dados.get('preco'):
        return jsonify({"erro": "Dados incompletos"}), 400
    
    try:
        preco = float(dados.get('preco'))
        if preco < 0:
            return jsonify({"erro": "Preço deve ser positivo"}), 400
    except (ValueError, TypeError):
        return jsonify({"erro": "Preço inválido"}), 400
    
    produto_id = db.criar_produto(dados['nome'], dados['descricao'], preco)
    produtos = db.listar_produtos()
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    
    return jsonify(produto), 201

def atualizar_produto(id):
    """Atualiza um produto existente"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    dados = request.get_json()
    
    try:
        sucesso = db.atualizar_produto(id, dados.get('nome'), dados.get('descricao'), float(dados.get('preco')))
    except (ValueError, TypeError) as e:
        return jsonify({"erro": "Dados inválidos: preço deve ser um número válido"}), 400
    
    if sucesso:
        produtos = db.listar_produtos()
        produto = next((p for p in produtos if p['id'] == id), None)
        return jsonify(produto)
    
    return jsonify({"erro": "Produto não encontrado"}), 404

def deletar_produto(id):
    """Remove um produto"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    sucesso = db.remover_produto(id)
    if sucesso:
        return jsonify({"mensagem": "Produto removido"})
    return jsonify({"erro": "Produto não encontrado"}), 404
