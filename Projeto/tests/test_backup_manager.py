import pytest
import os
import tempfile
import shutil
import json
from models.backup_manager import BackupManager
from models.database_manager import DatabaseManager

@pytest.fixture
def temp_backup_manager():
    """Cria um BackupManager temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    backup_dir = os.path.join(temp_dir, 'backups_test')
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Cria banco de dados de teste
    schema_original = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_schema.sql')
    if os.path.exists(schema_original):
        schema_temp = os.path.join(temp_dir, 'database_schema.sql')
        shutil.copy(schema_original, schema_temp)
    
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    # Inicializa o banco
    db = DatabaseManager(db_path=db_path)
    
    # Cria backup manager
    bm = BackupManager(backup_dir=backup_dir, db_path=db_path)
    
    yield bm, db
    
    os.chdir(original_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestBackupManager:
    """Testes para BackupManager"""
    
    def test_init_backup_manager(self, temp_backup_manager):
        """Testa inicialização do BackupManager"""
        bm, _ = temp_backup_manager
        assert os.path.exists(bm.backup_dir)
    
    def test_exportar_para_json(self, temp_backup_manager):
        """Testa exportação para JSON"""
        bm, db = temp_backup_manager
        
        # Adiciona alguns dados
        db.criar_usuario('user1', 'pass1', 'admin')
        db.criar_produto('Produto 1', 'Desc 1', 10.00)
        
        arquivo, stats = bm.exportar_para_json()
        
        assert os.path.exists(arquivo)
        assert stats['usuarios'] >= 1
        assert stats['produtos'] >= 1
        
        # Verifica conteúdo do arquivo
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        assert 'metadata' in dados
        assert 'usuarios' in dados
        assert 'produtos' in dados
        assert len(dados['usuarios']) >= 1
        assert len(dados['produtos']) >= 1
    
    def test_backup_automatico(self, temp_backup_manager):
        """Testa backup automático"""
        bm, db = temp_backup_manager
        
        # Adiciona dados
        db.criar_produto('Produto Backup', 'Desc', 20.00)
        
        arquivo = bm.backup_automatico()
        assert os.path.exists(arquivo)
        assert 'backup_' in arquivo
    
    def test_backup_automatico_limpeza(self, temp_backup_manager):
        """Testa limpeza automática de backups antigos"""
        bm, db = temp_backup_manager
        
        # Cria vários backups
        for i in range(12):
            bm.exportar_para_json()
        
        # Executa backup automático que deve limpar antigos
        bm.backup_automatico(max_backups=5)
        
        # Verifica quantidade de backups
        backups = [f for f in os.listdir(bm.backup_dir) 
                  if f.startswith('backup_') and f.endswith('.json')]
        assert len(backups) <= 5
    
    def test_importar_de_json(self, temp_backup_manager):
        """Testa importação de JSON"""
        bm, db = temp_backup_manager
        
        # Cria dados e backup
        db.criar_usuario('user_backup', 'pass123', 'gerente')
        db.criar_produto('Produto Backup', 'Desc Backup', 15.00)
        
        arquivo, _ = bm.exportar_para_json()
        
        # Limpa dados
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos")
        conn.commit()
        conn.close()
        
        # Restaura backup
        resultado = bm.importar_de_json(arquivo)
        assert resultado is True
        
        # Verifica se dados foram restaurados
        produtos = db.listar_produtos(apenas_ativos=False)
        assert len(produtos) >= 1
        assert any(p['nome'] == 'Produto Backup' for p in produtos)
    
    def test_importar_arquivo_inexistente(self, temp_backup_manager):
        """Testa importação de arquivo inexistente"""
        bm, _ = temp_backup_manager
        
        with pytest.raises(FileNotFoundError):
            bm.importar_de_json('arquivo_nao_existe.json')
    
    def test_exportar_com_pedidos(self, temp_backup_manager):
        """Testa exportação incluindo pedidos"""
        bm, db = temp_backup_manager
        
        # Cria pedido
        itens = [{'nome': 'Item 1', 'preco': 10.00, 'quantidade': 1}]
        db.criar_pedido(itens, 10.00)
        
        arquivo, stats = bm.exportar_para_json()
        
        assert os.path.exists(arquivo)
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        assert 'pedidos' in dados
        assert len(dados['pedidos']) >= 1
    
    def test_exportar_com_nome_customizado(self, temp_backup_manager):
        """Testa exportação com nome de arquivo customizado"""
        bm, db = temp_backup_manager
        
        arquivo_custom = os.path.join(bm.backup_dir, 'backup_custom.json')
        arquivo, stats = bm.exportar_para_json(arquivo=arquivo_custom)
        
        assert arquivo == arquivo_custom
        assert os.path.exists(arquivo_custom)
