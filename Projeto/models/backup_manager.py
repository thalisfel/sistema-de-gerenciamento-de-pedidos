import json
from datetime import datetime
import os
import sqlite3

class BackupManager:
    def __init__(self, backup_dir='backups_json', db_path='cardapio.db'):
        self.backup_dir = backup_dir
        self.db_path = db_path
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def exportar_para_json(self, arquivo=None):
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = os.path.join(self.backup_dir, f"backup_{timestamp}.json")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        dados = {
            'metadata': {'data_backup': datetime.now().isoformat(), 'versao': '1.0'},
            'usuarios': [], 'produtos': [], 'pedidos': [], 'historico_pedidos': [], 'lucros_diarios': []
        }
        cursor.execute("SELECT id, usuario, tipo, data_cadastro, ativo FROM usuarios")
        dados['usuarios'] = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT * FROM produtos")
        dados['produtos'] = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT * FROM pedidos")
        dados['pedidos'] = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT * FROM historico_pedidos")
        dados['historico_pedidos'] = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT * FROM lucros_diarios")
        dados['lucros_diarios'] = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        stats = {
            'usuarios': len(dados['usuarios']),
            'produtos': len(dados['produtos']),
            'pedidos': len(dados['pedidos']),
            'historico': len(dados['historico_pedidos'])
        }
        print(f"✅ Backup criado: {arquivo}")
        return arquivo, stats
    
    def backup_automatico(self, max_backups=10):
        arquivo, stats = self.exportar_para_json()
        backups = sorted([os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir)
                         if f.startswith('backup_') and f.endswith('.json')])
        while len(backups) > max_backups:
            os.remove(backups.pop(0))
        return arquivo
    
    def importar_de_json(self, arquivo):
        if not os.path.exists(arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM lucros_diarios")
            cursor.execute("DELETE FROM historico_pedidos")
            cursor.execute("DELETE FROM pedidos")
            cursor.execute("DELETE FROM produtos")
            cursor.execute("DELETE FROM usuarios WHERE usuario != 'admin'")
            for produto in dados.get('produtos', []):
                cursor.execute("INSERT INTO produtos (nome, descricao, preco, ativo) VALUES (?, ?, ?, ?)",
                             (produto['nome'], produto['descricao'], produto['preco'], produto.get('ativo', 1)))
            for pedido in dados.get('pedidos', []):
                cursor.execute("INSERT INTO pedidos (itens_json, total, status, data_pedido) VALUES (?, ?, ?, ?)",
                             (pedido['itens_json'], pedido['total'], pedido['status'], pedido['data_pedido']))
            for hist in dados.get('historico_pedidos', []):
                cursor.execute("""INSERT INTO historico_pedidos (pedido_id, itens_json, total, status, 
                    data_pedido, data_entrega) VALUES (?, ?, ?, ?, ?, ?)""",
                    (hist['pedido_id'], hist['itens_json'], hist['total'], hist['status'], 
                     hist['data_pedido'], hist['data_entrega']))
            conn.commit()
            print(f"✅ Backup restaurado: {arquivo}")
            return True
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao importar backup: {str(e)}")
            raise
        finally:
            conn.close()
