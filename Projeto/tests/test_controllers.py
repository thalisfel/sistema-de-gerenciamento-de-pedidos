import pytest
import json
from flask import session

class TestAuthController:
    """Testes para auth_controller"""
    
    def test_login_sucesso(self, client):
        """Testa login com sucesso"""
        # Primeiro cria um usuário para teste
        from models.database_manager import db
        db.criar_usuario('testuser', 'testpass', 'admin')
        
        response = client.post('/api/login', 
                              json={'usuario': 'testuser', 'senha': 'testpass'},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
        assert 'testuser' in data['mensagem']
        assert data['tipo'] == 'admin'
    
    def test_login_senha_incorreta(self, client):
        """Testa login com senha incorreta"""
        from models.database_manager import db
        db.criar_usuario('testuser2', 'senha_correta', 'gerente')
        
        response = client.post('/api/login',
                              json={'usuario': 'testuser2', 'senha': 'senha_errada'},
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['sucesso'] is False
    
    def test_login_usuario_inexistente(self, client):
        """Testa login com usuário inexistente"""
        response = client.post('/api/login',
                              json={'usuario': 'naoexiste', 'senha': 'qualquer'},
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_logout(self, authenticated_client):
        """Testa logout"""
        response = authenticated_client.post('/api/logout')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_verificar_auth_autenticado(self, authenticated_client):
        """Testa verificação de autenticação quando está autenticado"""
        response = authenticated_client.get('/api/verificar-auth')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['autenticado'] is True
        assert 'usuario' in data
    
    def test_verificar_auth_nao_autenticado(self, client):
        """Testa verificação de autenticação quando não está autenticado"""
        response = client.get('/api/verificar-auth')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['autenticado'] is False


class TestUserController:
    """Testes para user_controller"""
    
    def test_cadastrar_usuario_como_admin(self, authenticated_client):
        """Testa cadastro de usuário como admin"""
        import uuid
        usuario_unico = f'novousuario_{uuid.uuid4().hex[:8]}'
        
        response = authenticated_client.post('/api/usuarios',
                                             json={'usuario': usuario_unico, 
                                                   'senha': 'senha123',
                                                   'tipo': 'gerente'},
                                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['sucesso'] is True
        assert data['usuario'] == usuario_unico
    
    def test_cadastrar_usuario_sem_autenticacao(self, client):
        """Testa cadastro de usuário sem autenticação"""
        response = client.post('/api/usuarios',
                              json={'usuario': 'novousuario', 
                                    'senha': 'senha123',
                                    'tipo': 'gerente'},
                              content_type='application/json')
        
        assert response.status_code == 403
    
    def test_cadastrar_usuario_como_gerente(self, authenticated_gerente):
        """Testa cadastro de usuário como gerente (deve falhar)"""
        response = authenticated_gerente.post('/api/usuarios',
                                              json={'usuario': 'novousuario', 
                                                    'senha': 'senha123',
                                                    'tipo': 'gerente'},
                                              content_type='application/json')
        
        assert response.status_code == 403
    
    def test_cadastrar_usuario_senha_curta(self, authenticated_client):
        """Testa cadastro com senha muito curta"""
        response = authenticated_client.post('/api/usuarios',
                                             json={'usuario': 'usuario1', 
                                                   'senha': '123',
                                                   'tipo': 'gerente'},
                                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'senha' in data['erro'].lower()
    
    def test_cadastrar_usuario_nome_curto(self, authenticated_client):
        """Testa cadastro com nome muito curto"""
        response = authenticated_client.post('/api/usuarios',
                                             json={'usuario': 'ab', 
                                                   'senha': 'senha123',
                                                   'tipo': 'gerente'},
                                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'usuário' in data['erro'].lower() or 'caracteres' in data['erro'].lower()
    
    def test_listar_usuarios_como_admin(self, authenticated_client):
        """Testa listagem de usuários como admin"""
        response = authenticated_client.get('/api/usuarios')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_listar_usuarios_sem_autenticacao(self, client):
        """Testa listagem sem autenticação"""
        response = client.get('/api/usuarios')
        assert response.status_code == 403
    
    def test_remover_usuario_como_admin(self, authenticated_client):
        """Testa remoção de usuário como admin"""
        # Primeiro cria um usuário
        from models.database_manager import db
        db.criar_usuario('userparaexcluir', 'senha123', 'gerente')
        
        response = authenticated_client.delete('/api/usuarios/userparaexcluir')
        assert response.status_code == 200


class TestProductController:
    """Testes para product_controller"""
    
    def test_listar_produtos_publico(self, client):
        """Testa listagem de produtos (acesso público)"""
        response = client.get('/api/produtos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_criar_produto_autenticado(self, authenticated_client):
        """Testa criação de produto autenticado"""
        response = authenticated_client.post('/api/produtos',
                                             json={'nome': 'Produto Teste',
                                                   'descricao': 'Descrição teste',
                                                   'preco': 25.50},
                                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['nome'] == 'Produto Teste'
        assert data['preco'] == 25.50
    
    def test_criar_produto_sem_autenticacao(self, client):
        """Testa criação de produto sem autenticação"""
        response = client.post('/api/produtos',
                              json={'nome': 'Produto',
                                    'descricao': 'Desc',
                                    'preco': 10.00},
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_criar_produto_dados_incompletos(self, authenticated_client):
        """Testa criação de produto com dados incompletos"""
        response = authenticated_client.post('/api/produtos',
                                             json={'nome': 'Produto'},
                                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_criar_produto_preco_negativo(self, authenticated_client):
        """Testa criação de produto com preço negativo"""
        response = authenticated_client.post('/api/produtos',
                                             json={'nome': 'Produto',
                                                   'descricao': 'Desc',
                                                   'preco': -10.00},
                                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_criar_produto_preco_invalido(self, authenticated_client):
        """Testa criação de produto com preço inválido"""
        response = authenticated_client.post('/api/produtos',
                                             json={'nome': 'Produto',
                                                   'descricao': 'Desc',
                                                   'preco': 'invalido'},
                                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_atualizar_produto(self, authenticated_client):
        """Testa atualização de produto"""
        # Primeiro cria um produto
        from models.database_manager import db
        produto_id = db.criar_produto('Produto Original', 'Desc', 10.00)
        
        response = authenticated_client.put(f'/api/produtos/{produto_id}',
                                           json={'nome': 'Produto Atualizado',
                                                 'descricao': 'Nova desc',
                                                 'preco': 15.00},
                                           content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nome'] == 'Produto Atualizado'
    
    def test_atualizar_produto_sem_autenticacao(self, client):
        """Testa atualização sem autenticação"""
        response = client.put('/api/produtos/1',
                             json={'nome': 'Produto',
                                   'descricao': 'Desc',
                                   'preco': 10.00},
                             content_type='application/json')
        
        assert response.status_code == 401
    
    def test_atualizar_produto_inexistente(self, authenticated_client):
        """Testa atualização de produto inexistente"""
        response = authenticated_client.put('/api/produtos/9999',
                                           json={'nome': 'Produto',
                                                 'descricao': 'Desc',
                                                 'preco': 10.00},
                                           content_type='application/json')
        
        assert response.status_code == 404
    
    def test_deletar_produto(self, authenticated_client):
        """Testa deleção de produto"""
        from models.database_manager import db
        produto_id = db.criar_produto('Produto Delete', 'Desc', 10.00)
        
        response = authenticated_client.delete(f'/api/produtos/{produto_id}')
        assert response.status_code == 200


class TestOrderController:
    """Testes para order_controller"""
    
    def test_criar_pedido_autenticado(self, authenticated_client):
        """Testa criação de pedido"""
        response = authenticated_client.post('/api/pedidos',
                                            json={'itens': [{'nome': 'Item 1', 'preco': 10.00, 'quantidade': 2}],
                                                  'total': 20.00},
                                            content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['sucesso'] is True
        assert 'pedido' in data
    
    def test_criar_pedido_sem_autenticacao(self, client):
        """Testa criação de pedido sem autenticação"""
        response = client.post('/api/pedidos',
                              json={'itens': [], 'total': 0},
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_criar_pedido_dados_incompletos(self, authenticated_client):
        """Testa criação de pedido com dados incompletos"""
        response = authenticated_client.post('/api/pedidos',
                                            json={'itens': []},
                                            content_type='application/json')
        
        assert response.status_code == 400
    
    def test_listar_pedidos_autenticado(self, authenticated_client):
        """Testa listagem de pedidos"""
        response = authenticated_client.get('/api/pedidos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_listar_pedidos_sem_autenticacao(self, client):
        """Testa listagem sem autenticação"""
        response = client.get('/api/pedidos')
        assert response.status_code == 401
    
    def test_atualizar_status_pedido(self, authenticated_client):
        """Testa atualização de status de pedido"""
        # Cria um pedido primeiro
        from models.database_manager import db
        pedido = db.criar_pedido([{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}], 10.00)
        
        response = authenticated_client.put(f'/api/pedidos/{pedido["id"]}/status',
                                           json={'status': 'Preparando'},
                                           content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Preparando'
    
    def test_atualizar_status_pedido_status_invalido(self, authenticated_client):
        """Testa atualização com status inválido"""
        from models.database_manager import db
        pedido = db.criar_pedido([{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}], 10.00)
        
        response = authenticated_client.put(f'/api/pedidos/{pedido["id"]}/status',
                                           json={'status': 'StatusInvalido'},
                                           content_type='application/json')
        
        assert response.status_code == 400
    
    def test_obter_estatisticas(self, authenticated_client):
        """Testa obtenção de estatísticas"""
        response = authenticated_client.get('/api/estatisticas')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
    
    def test_obter_lucros_como_admin(self, authenticated_client):
        """Testa obtenção de lucros como admin"""
        response = authenticated_client.get('/api/lucros')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_obter_lucros_como_gerente(self, authenticated_gerente):
        """Testa obtenção de lucros como gerente (deve falhar)"""
        response = authenticated_gerente.get('/api/lucros')
        assert response.status_code == 403
    
    def test_obter_lucros_sem_autenticacao(self, client):
        """Testa obtenção de lucros sem autenticação"""
        response = client.get('/api/lucros')
        assert response.status_code == 403
    
    def test_listar_historico_autenticado(self, authenticated_client):
        """Testa listagem de histórico"""
        response = authenticated_client.get('/api/pedidos/historico')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_listar_historico_sem_autenticacao(self, client):
        """Testa listagem de histórico sem autenticação"""
        response = client.get('/api/pedidos/historico')
        assert response.status_code == 401
    
    def test_limpar_historico_como_admin(self, authenticated_client):
        """Testa limpeza de histórico como admin"""
        response = authenticated_client.delete('/api/pedidos/historico')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_limpar_historico_como_gerente(self, authenticated_gerente):
        """Testa limpeza de histórico como gerente (deve falhar)"""
        response = authenticated_gerente.delete('/api/pedidos/historico')
        assert response.status_code == 403
    
    def test_resetar_contadores_como_admin(self, authenticated_client):
        """Testa reset de contadores como admin"""
        response = authenticated_client.post('/api/resetar-ids')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_resetar_contadores_como_gerente(self, authenticated_gerente):
        """Testa reset de contadores como gerente (deve falhar)"""
        response = authenticated_gerente.post('/api/resetar-ids')
        assert response.status_code == 403
    
    def test_deletar_pedido_como_admin(self, authenticated_client):
        """Testa deleção de pedido como admin"""
        from models.database_manager import db
        pedido = db.criar_pedido([{'nome': 'Item', 'preco': 10.00, 'quantidade': 1}], 10.00)
        
        response = authenticated_client.delete(f'/api/pedidos/{pedido["id"]}')
        assert response.status_code == 200
    
    def test_deletar_pedido_como_gerente(self, authenticated_gerente):
        """Testa deleção de pedido como gerente (deve falhar)"""
        response = authenticated_gerente.delete('/api/pedidos/1')
        assert response.status_code == 403


class TestBackupController:
    """Testes para backup_controller"""
    
    def test_criar_backup_como_admin(self, authenticated_client):
        """Testa criação de backup como admin"""
        response = authenticated_client.post('/api/backup')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
        assert 'arquivo' in data
    
    def test_criar_backup_como_gerente(self, authenticated_gerente):
        """Testa criação de backup como gerente (deve falhar)"""
        response = authenticated_gerente.post('/api/backup')
        assert response.status_code == 403
    
    def test_criar_backup_sem_autenticacao(self, client):
        """Testa criação de backup sem autenticação"""
        response = client.post('/api/backup')
        assert response.status_code == 403
    
    def test_backup_automatico_como_admin(self, authenticated_client):
        """Testa backup automático como admin"""
        response = authenticated_client.post('/api/backup/automatico')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_restaurar_backup_sem_arquivo(self, authenticated_client):
        """Testa restauração sem arquivo"""
        response = authenticated_client.post('/api/backup/restaurar',
                                             json={},
                                             content_type='application/json')
        assert response.status_code == 400
