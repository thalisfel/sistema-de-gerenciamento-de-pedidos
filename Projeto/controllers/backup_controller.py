from flask import request, jsonify, session
from models.backup_manager import BackupManager

# Instância do gerenciador de backups
backup_manager = BackupManager()

def criar_backup():
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem criar backups"}), 403
    
    try:
        arquivo, stats = backup_manager.exportar_para_json()
        return jsonify({
            "sucesso": True,
            "mensagem": "Backup criado com sucesso",
            "arquivo": arquivo,
            "estatisticas": stats
        }), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao criar backup: {str(e)}"}), 500

def restaurar_backup():
    """Restaura dados de um backup JSON"""
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem restaurar backups"}), 403
    
    dados = request.get_json()
    arquivo = dados.get('arquivo')
    
    if not arquivo:
        return jsonify({"erro": "Nome do arquivo não fornecido"}), 400
    
    try:
        backup_manager.importar_de_json(arquivo)
        return jsonify({
            "sucesso": True,
            "mensagem": "Backup restaurado com sucesso"
        }), 200
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de backup não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": f"Erro ao restaurar backup: {str(e)}"}), 500

def backup_automatico():
    """Cria backup automático com limpeza de antigos"""
    if not session.get('autenticado') or session.get('tipo') != 'admin':
        return jsonify({"erro": "Apenas administradores podem criar backups"}), 403
    
    try:
        arquivo = backup_manager.backup_automatico()
        return jsonify({
            "sucesso": True,
            "mensagem": "Backup automático criado",
            "arquivo": arquivo
        }), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao criar backup: {str(e)}"}), 500
