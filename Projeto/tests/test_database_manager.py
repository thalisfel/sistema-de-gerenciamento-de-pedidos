import pytest
import os
import tempfile
import shutil
import json
from models.database_manager import DatabaseManager

@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Copia o schema para o diretório temporário
    schema_original = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_schema.sql')
    if os.path.exists(schema_original):
        schema_temp = os.path.join(temp_dir, 'database_schema.sql')
        shutil.copy(schema_original, schema_temp)
    
    # Muda temporariamente para o diretório do teste
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    db = DatabaseManager(db_path=db_path)
    
    yield db
    
    # Restaura diretório e limpa
    os.chdir(original_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestDatabaseManager:
    """Testes para DatabaseManager"""
    
    def test_init_database(self, temp_db):
        """Testa inicialização do banco de dados"""
        assert os.path.exists(temp_db.db_path)
        conn = temp_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'usuarios' in tables
        assert 'produtos' in tables
        assert 'pedidos' in tables
    
    def test_criar_usuario_sucesso(self, temp_db):
        """Testa criação de usuário com sucesso"""
        sucesso, msg = temp_db.criar_usuario('teste', 'senha123', 'gerente')
        assert sucesso is True
        assert 'sucesso' in msg.lower()
    
    def test_criar_usuario_duplicado(self, temp_db):
        """Testa criação de usuário duplicado"""
        temp_db.criar_usuario('teste', 'senha123', 'gerente')
        sucesso, msg = temp_db.criar_usuario('teste', 'senha456', 'admin')
        assert sucesso is False
        assert 'existe' in msg.lower()
    
    def test_verificar_login_sucesso(self, temp_db):
        """Testa login com credenciais corretas"""
        temp_db.criar_usuario('user1', 'password123', 'admin')
        sucesso, tipo = temp_db.verificar_login('user1', 'password123')
        assert sucesso is True
        assert tipo == 'admin'
    
    def test_verificar_login_senha_incorreta(self, temp_db):
        """Testa login com senha incorreta"""
        temp_db.criar_usuario('user1', 'password123', 'gerente')
        sucesso, tipo = temp_db.verificar_login('user1', 'senha_errada')
        assert sucesso is False
        assert tipo is None
    
    def test_verificar_login_usuario_inexistente(self, temp_db):
        """Testa login com usuário inexistente"""
        sucesso, tipo = temp_db.verificar_login('naoexiste', 'senha')
        assert sucesso is False
        assert tipo is None
    
    def test_listar_usuarios(self, temp_db):
        """Testa listagem de usuários"""
        temp_db.criar_usuario('user1', 'pass1', 'admin')
        temp_db.criar_usuario('user2', 'pass2', 'gerente')
        
        usuarios = temp_db.listar_usuarios()
        assert len(usuarios) >= 2
        nomes = [u['usuario'] for u in usuarios]
        assert 'user1' in nomes
        assert 'user2' in nomes
    
    def test_remover_usuario(self, temp_db):
        """Testa remoção de usuário"""
        temp_db.criar_usuario('userremove', 'pass123', 'gerente')
        sucesso = temp_db.remover_usuario('userremove')
        assert sucesso is True
        
        usuarios = temp_db.listar_usuarios()
        nomes = [u['usuario'] for u in usuarios]
        assert 'userremove' not in nomes
    
    def test_remover_usuario_inexistente(self, temp_db):
        """Testa remoção de usuário inexistente"""
        sucesso = temp_db.remover_usuario('naoexiste')
        assert sucesso is False
    
    def test_get_tipo_usuario(self, temp_db):
        """Testa obtenção de tipo de usuário"""
        temp_db.criar_usuario('admin1', 'pass', 'admin')
        tipo = temp_db.get_tipo_usuario('admin1')
        assert tipo == 'admin'
    
    def test_get_tipo_usuario_inexistente(self, temp_db):
        """Testa obtenção de tipo de usuário inexistente"""
        tipo = temp_db.get_tipo_usuario('naoexiste')
        assert tipo is None
    
    def test_contar_admins(self, temp_db):
        """Testa contagem de administradores"""
        temp_db.criar_usuario('admin1', 'pass1', 'admin')
        temp_db.criar_usuario('admin2', 'pass2', 'admin')
        temp_db.criar_usuario('gerente1', 'pass3', 'gerente')
        
        count = temp_db.contar_admins()
        assert count >= 2
    
    def test_criar_produto(self, temp_db):
        """Testa criação de produto"""
        produto_id = temp_db.criar_produto('Pizza', 'Pizza de calabresa', 35.90)
        assert produto_id > 0
    
    def test_listar_produtos(self, temp_db):
        """Testa listagem de produtos"""
        temp_db.criar_produto('Produto 1', 'Desc 1', 10.00)
        temp_db.criar_produto('Produto 2', 'Desc 2', 20.00)
        
        produtos = temp_db.listar_produtos()
        assert len(produtos) >= 2
    
    def test_atualizar_produto(self, temp_db):
        """Testa atualização de produto"""
        produto_id = temp_db.criar_produto('Produto Original', 'Desc', 10.00)
        sucesso = temp_db.atualizar_produto(produto_id, 'Produto Atualizado', 'Nova desc', 15.00)
        assert sucesso is True
        
        produtos = temp_db.listar_produtos()
        produto = next((p for p in produtos if p['id'] == produto_id), None)
        assert produto is not None
        assert produto['nome'] == 'Produto Atualizado'
        assert produto['preco'] == 15.00
    
    def test_atualizar_produto_inexistente(self, temp_db):
        """Testa atualização de produto inexistente"""
        sucesso = temp_db.atualizar_produto(9999, 'Nome', 'Desc', 10.00)
        assert sucesso is False
    
    def test_remover_produto(self, temp_db):
        """Testa remoção de produto"""
        produto_id = temp_db.criar_produto('Produto Remover', 'Desc', 10.00)
        sucesso = temp_db.remover_produto(produto_id)
        assert sucesso is True
        
        produtos = temp_db.listar_produtos()
        produto = next((p for p in produtos if p['id'] == produto_id), None)
        assert produto is None
    
    def test_criar_pedido(self, temp_db):
        """Testa criação de pedido"""
        itens = [{'nome': 'Pizza', 'preco': 35.90, 'quantidade': 2}]
        total = 71.80
        
        pedido = temp_db.criar_pedido(itens, total)
        assert pedido is not None
        assert pedido['total'] == total
        assert pedido['status'] == 'Pendente'
        assert len(pedido['itens']) == 1
    
    def test_listar_pedidos(self, temp_db):
        """Testa listagem de pedidos"""
        itens1 = [{'nome': 'Item 1', 'preco': 10.00, 'quantidade': 1}]
        itens2 = [{'nome': 'Item 2', 'preco': 20.00, 'quantidade': 1}]
        
        temp_db.criar_pedido(itens1, 10.00)
        temp_db.criar_pedido(itens2, 20.00)
        
        pedidos = temp_db.listar_pedidos()
        assert len(pedidos) >= 2
    
    def test_atualizar_status_pedido(self, temp_db):
        """Testa atualização de status de pedido"""
        itens = [{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}]
        pedido = temp_db.criar_pedido(itens, 10.00)
        
        pedido_atualizado = temp_db.atualizar_status_pedido(pedido['id'], 'Preparando')
        assert pedido_atualizado is not None
        assert pedido_atualizado['status'] == 'Preparando'
    
    def test_atualizar_status_pedido_para_entregue(self, temp_db):
        """Testa atualização de pedido para status Entregue"""
        itens = [{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}]
        pedido = temp_db.criar_pedido(itens, 10.00)
        
        pedido_atualizado = temp_db.atualizar_status_pedido(pedido['id'], 'Entregue')
        assert pedido_atualizado is not None
        assert pedido_atualizado['status'] == 'Entregue'
        assert pedido_atualizado['data_entrega'] is not None
    
    def test_deletar_pedido(self, temp_db):
        """Testa deleção de pedido"""
        itens = [{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}]
        pedido = temp_db.criar_pedido(itens, 10.00)
        
        sucesso = temp_db.deletar_pedido(pedido['id'])
        assert sucesso is True
    
    def test_deletar_pedido_inexistente(self, temp_db):
        """Testa deleção de pedido inexistente"""
        sucesso = temp_db.deletar_pedido(9999)
        assert sucesso is False
    
    def test_obter_estatisticas_gerais(self, temp_db):
        """Testa obtenção de estatísticas gerais"""
        # Cria alguns pedidos e marca como entregue
        itens = [{'nome': 'Item', 'preco': 50.00, 'quantidade': 1}]
        pedido1 = temp_db.criar_pedido(itens, 50.00)
        temp_db.atualizar_status_pedido(pedido1['id'], 'Entregue')
        
        pedido2 = temp_db.criar_pedido(itens, 50.00)
        temp_db.atualizar_status_pedido(pedido2['id'], 'Entregue')
        
        stats = temp_db.obter_estatisticas_gerais()
        
        assert 'total_pedidos' in stats
        assert 'receita_total' in stats
        assert 'ticket_medio' in stats
        assert stats['total_pedidos'] >= 2
        assert stats['receita_total'] >= 100.00
    
    def test_listar_historico(self, temp_db):
        """Testa listagem de histórico"""
        # Cria e entrega um pedido
        itens = [{'nome': 'Item', 'preco': 30.00, 'quantidade': 1}]
        pedido = temp_db.criar_pedido(itens, 30.00)
        temp_db.atualizar_status_pedido(pedido['id'], 'Entregue')
        
        historico = temp_db.listar_historico()
        
        assert isinstance(historico, list)
        assert len(historico) >= 1
        assert historico[0]['itens'] is not None
    
    def test_obter_lucros_periodo(self, temp_db):
        """Testa obtenção de lucros por período"""
        lucros = temp_db.obter_lucros_periodo()
        
        assert isinstance(lucros, list)
    
    def test_limpar_historico(self, temp_db):
        """Testa limpeza do histórico"""
        # Cria e entrega pedidos
        itens = [{'nome': 'Item', 'preco': 20.00, 'quantidade': 1}]
        pedido1 = temp_db.criar_pedido(itens, 20.00)
        temp_db.atualizar_status_pedido(pedido1['id'], 'Entregue')
        
        # Limpa histórico
        count = temp_db.limpar_historico()
        
        assert count >= 1
        
        # Verifica se histórico está vazio
        historico = temp_db.listar_historico()
        assert len(historico) == 0
    
    def test_resetar_contadores(self, temp_db):
        """Testa reset de contadores"""
        # Cria alguns dados
        temp_db.criar_produto('Produto', 'Desc', 10.00)
        itens = [{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}]
        temp_db.criar_pedido(itens, 10.00)
        
        # Reseta contadores
        resultado = temp_db.resetar_contadores()
        
        assert resultado is True
        
        # Verifica se tudo foi limpo
        produtos = temp_db.listar_produtos()
        pedidos = temp_db.listar_pedidos()
        
        assert len(produtos) == 0
        assert len(pedidos) == 0
    
    def test_limpar_banco(self, temp_db):
        """Testa limpeza do banco"""
        # Cria alguns dados
        temp_db.criar_produto('Produto', 'Desc', 10.00)
        itens = [{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}]
        temp_db.criar_pedido(itens, 10.00)
        
        # Limpa banco
        temp_db.limpar_banco()
        
        # Verifica limpeza
        pedidos = temp_db.listar_pedidos(incluir_entregues=True)
        assert len(pedidos) == 0
    
    def test_listar_pedidos_incluir_entregues(self, temp_db):
        """Testa listagem incluindo pedidos entregues"""
        itens = [{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}]
        pedido = temp_db.criar_pedido(itens, 10.00)
        temp_db.atualizar_status_pedido(pedido['id'], 'Entregue')
        
        # Lista sem incluir entregues
        pedidos_ativos = temp_db.listar_pedidos(incluir_entregues=False)
        
        # Lista incluindo entregues
        todos_pedidos = temp_db.listar_pedidos(incluir_entregues=True)
        
        assert len(todos_pedidos) >= len(pedidos_ativos)
    
    def test_listar_produtos_inativos(self, temp_db):
        """Testa listagem incluindo produtos inativos"""
        temp_db.criar_produto('Produto Ativo', 'Desc', 10.00)
        
        produtos_ativos = temp_db.listar_produtos(apenas_ativos=True)
        todos_produtos = temp_db.listar_produtos(apenas_ativos=False)
        
        assert len(todos_produtos) >= len(produtos_ativos)
