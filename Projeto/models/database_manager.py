import sqlite3
import json
import bcrypt
import os

class DatabaseManager:
    def __init__(self, db_path='cardapio.db'):
        self.db_path = db_path
        self._inicializar_banco()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _inicializar_banco(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                cursor.executescript(f.read())
        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado")
    
    def criar_usuario(self, usuario, senha, tipo='gerente'):
        conn = None
        try:
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha_hash, tipo) VALUES (?, ?, ?)", 
                         (usuario, senha_hash, tipo))
            conn.commit()
            return True, "Usuário criado com sucesso"
        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()
            return False, "Usuário já existe"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Erro ao criar usuário: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def verificar_login(self, usuario, senha):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, tipo FROM usuarios WHERE usuario = ? AND ativo = 1", (usuario,))
        result = cursor.fetchone()
        conn.close()
        if result and bcrypt.checkpw(senha.encode('utf-8'), result['senha_hash'].encode('utf-8')):
            return True, result['tipo']
        return False, None
    
    def listar_usuarios(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, tipo, data_cadastro, ativo FROM usuarios")
        usuarios = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return usuarios
    
    def remover_usuario(self, usuario):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
        sucesso = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return sucesso
    
    def get_tipo_usuario(self, usuario):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tipo FROM usuarios WHERE usuario = ?", (usuario,))
        result = cursor.fetchone()
        conn.close()
        return result['tipo'] if result else None
    
    def contar_admins(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE tipo = 'admin' AND ativo = 1")
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def criar_produto(self, nome, descricao, preco):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)", (nome, descricao, preco))
        produto_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return produto_id
    
    def listar_produtos(self, apenas_ativos=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        if apenas_ativos:
            cursor.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome")
        else:
            cursor.execute("SELECT * FROM produtos ORDER BY nome")
        produtos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return produtos
    
    def atualizar_produto(self, produto_id, nome, descricao, preco):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET nome = ?, descricao = ?, preco = ? WHERE id = ?",
                      (nome, descricao, preco, produto_id))
        sucesso = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return sucesso
    
    def remover_produto(self, produto_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        sucesso = cursor.rowcount > 0
        
        # Verifica se a tabela ficou vazia
        cursor.execute("SELECT COUNT(*) FROM produtos")
        count = cursor.fetchone()[0]
        
        # Se a tabela estiver vazia, reseta o auto-increment
        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='produtos'")
            print("🔄 Tabela de produtos zerada - contador resetado para ID 1")
        
        conn.commit()
        conn.close()
        return sucesso
    
    def criar_pedido(self, itens, total):
        conn = self.get_connection()
        cursor = conn.cursor()
        itens_json = json.dumps(itens)
        cursor.execute("INSERT INTO pedidos (itens_json, total, status) VALUES (?, ?, 'Pendente')",
                      (itens_json, total))
        pedido_id = cursor.lastrowid
        conn.commit()
        cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        pedido = dict(cursor.fetchone())
        pedido['itens'] = json.loads(pedido['itens_json'])
        conn.close()
        return pedido
    
    def listar_pedidos(self, incluir_entregues=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        if incluir_entregues:
            cursor.execute("SELECT * FROM pedidos ORDER BY data_pedido DESC")
        else:
            cursor.execute("SELECT * FROM pedidos WHERE status NOT IN ('Entregue', 'Cancelado') ORDER BY data_pedido DESC")
        pedidos = []
        for row in cursor.fetchall():
            pedido = dict(row)
            pedido['itens'] = json.loads(pedido['itens_json'])
            pedidos.append(pedido)
        conn.close()
        return pedidos
    
    def atualizar_status_pedido(self, pedido_id, novo_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""UPDATE pedidos SET status = ?, 
            data_entrega = CASE WHEN ? = 'Entregue' THEN datetime('now', 'localtime') ELSE data_entrega END 
            WHERE id = ?""", (novo_status, novo_status, pedido_id))
        if novo_status == 'Entregue':
            cursor.execute("""INSERT INTO historico_pedidos (pedido_id, itens_json, total, status, data_pedido, data_entrega)
                SELECT id, itens_json, total, status, data_pedido, data_entrega FROM pedidos WHERE id = ?""", (pedido_id,))
        conn.commit()
        cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        result = cursor.fetchone()
        if result:
            pedido = dict(result)
            pedido['itens'] = json.loads(pedido['itens_json'])
            conn.close()
            return pedido
        conn.close()
        return None
    
    def deletar_pedido(self, pedido_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        sucesso = cursor.rowcount > 0
        
        # Verifica se a tabela ficou vazia
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        count = cursor.fetchone()[0]
        
        # Se a tabela estiver vazia, reseta o auto-increment
        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='pedidos'")
            print("🔄 Tabela de pedidos zerada - contador resetado para ID 1")
        
        conn.commit()
        conn.close()
        return sucesso
    
    def obter_estatisticas_gerais(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as receita FROM historico_pedidos")
        result = cursor.fetchone()
        total_pedidos = result['count']
        receita_total = result['receita']
        cursor.execute("""SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as receita
            FROM historico_pedidos WHERE DATE(data_entrega) = DATE('now')""")
        result = cursor.fetchone()
        pedidos_hoje = result['count']
        receita_hoje = result['receita']
        ticket_medio = receita_total / total_pedidos if total_pedidos > 0 else 0
        conn.close()
        return {
            'total_pedidos': total_pedidos,
            'receita_total': receita_total,
            'ticket_medio': ticket_medio,
            'pedidos_hoje': pedidos_hoje,
            'receita_hoje': receita_hoje
        }
    
    def listar_historico(self):
        """Lista todos os pedidos do histórico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historico_pedidos ORDER BY data_entrega DESC")
        historico = []
        for row in cursor.fetchall():
            pedido = dict(row)
            pedido['itens'] = json.loads(pedido['itens_json'])
            historico.append(pedido)
        conn.close()
        return historico
    
    def obter_lucros_periodo(self, data_inicio=None, data_fim=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if data_inicio and data_fim:
            cursor.execute("SELECT * FROM lucros_diarios WHERE data BETWEEN ? AND ? ORDER BY data DESC",
                         (data_inicio, data_fim))
        else:
            cursor.execute("SELECT * FROM lucros_diarios ORDER BY data DESC LIMIT 30")
        lucros = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return lucros
    
    def limpar_historico(self):
        """Limpa todos os registros do histórico de pedidos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historico_pedidos")
        count = cursor.rowcount
        
        # Reseta o auto-increment do histórico
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='historico_pedidos'")
        print("🔄 Histórico de pedidos limpo - contador resetado para ID 1")
        
        conn.commit()
        conn.close()
        return count
    
    def resetar_contadores(self):
        """Reseta todos os contadores de IDs deletando todos os dados e resetando sqlite_sequence"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Deletar todos os registros (mantém admin)
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM historico_pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM lucros_diarios")
        
        # Resetar os contadores
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('pedidos', 'historico_pedidos', 'produtos')")
        
        print("🔄 Todos os contadores resetados - próximos IDs serão #1")
        
        conn.commit()
        conn.close()
        return True
    
    def limpar_banco(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM historico_pedidos")
        cursor.execute("DELETE FROM lucros_diarios")
        cursor.execute("DELETE FROM usuarios WHERE usuario != 'admin'")
        conn.commit()
        conn.close()

db = DatabaseManager()
