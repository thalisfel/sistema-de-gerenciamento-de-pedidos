from flask import request, jsonify, session
from models.database_manager import db

def criar_pedido():
    """Cria um novo pedido"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    dados = request.get_json()
    
    if not dados.get('itens') or not dados.get('total'):
        return jsonify({"erro": "Dados incompletos"}), 400
    
    try:
        pedido = db.criar_pedido(dados.get('itens'), float(dados.get('total')))
        return jsonify({"sucesso": True, "pedido": pedido}), 201
    except (ValueError, TypeError) as e:
        return jsonify({"erro": "Dados inválidos: total deve ser um número válido"}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro ao criar pedido: {str(e)}"}), 500

def listar_pedidos():
    """Lista pedidos (apenas para usuários autenticados)"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    incluir_entregues = request.args.get('incluir_entregues', 'false').lower() == 'true'
    pedidos_lista = db.listar_pedidos(incluir_entregues=incluir_entregues)
    return jsonify(pedidos_lista), 200

def atualizar_status_pedido(id):
    """Atualiza o status de um pedido"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    dados = request.get_json()
    novo_status = dados.get('status')
    
    if novo_status not in ['Pendente', 'Preparando', 'Pronto', 'Entregue', 'Cancelado']:
        return jsonify({"erro": "Status inválido"}), 400
    
    pedido = db.atualizar_status_pedido(id, novo_status)
    
    if pedido:
        return jsonify(pedido), 200
    
    return jsonify({"erro": "Pedido não encontrado"}), 404

def deletar_pedido(id):
    """Deleta um pedido"""
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem deletar pedidos"}), 403
    
    if db.deletar_pedido(id):
        return jsonify({"mensagem": "Pedido deletado com sucesso"}), 200
    return jsonify({"erro": "Pedido não encontrado"}), 404

def obter_estatisticas():
    """Retorna estatísticas gerais"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    stats = db.obter_estatisticas_gerais()
    return jsonify(stats), 200

def obter_lucros():
    """Retorna lucros do período"""
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem ver lucros"}), 403
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    lucros = db.obter_lucros_periodo(data_inicio, data_fim)
    return jsonify(lucros), 200

def listar_historico():
    """Lista histórico de pedidos entregues"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    historico = db.listar_historico()
    return jsonify(historico), 200

def limpar_historico():
    """Limpa todo o histórico de pedidos (apenas admin)"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    if session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem limpar o histórico"}), 403
    
    count = db.limpar_historico()
    return jsonify({"sucesso": True, "mensagem": f"{count} registro(s) removido(s) do histórico"}), 200

def resetar_contadores():
    """Reseta todos os contadores de IDs - DELETA TUDO (apenas admin)"""
    if not session.get('autenticado'):
        return jsonify({"erro": "Não autorizado"}), 401
    
    if session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem resetar contadores"}), 403
    
    db.resetar_contadores()
    return jsonify({"sucesso": True, "mensagem": "✅ Sistema resetado! Todos os pedidos, histórico e produtos foram deletados."}), 200
