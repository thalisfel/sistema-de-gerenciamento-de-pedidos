# Sistema de Gerenciamento de Restaurante

[![Testes](https://img.shields.io/badge/testes-99%20passando-success)](tests/)
[![Cobertura](https://img.shields.io/badge/cobertura-91.63%25-brightgreen)](RELATORIO_TESTES.md)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-lightgrey)](https://flask.palletsprojects.com/)

Sistema completo de gerenciamento para restaurantes com controle de cardápio, pedidos e usuários.

## 📁 Estrutura do Projeto

```
projeto/
├── app.py                      # Aplicação principal Flask
├── requirements.txt            # Dependências Python
├── database_schema.sql         # Schema do banco de dados
├── cardapio.db                 # Banco de dados SQLite
│
├── controllers/               # 🎮 Lógica de negócio (MVC - Controller)
│   ├── auth_controller.py     # Autenticação
│   ├── user_controller.py     # Gestão de usuários
│   ├── product_controller.py  # Gestão de produtos
│   ├── order_controller.py    # Gestão de pedidos
│   └── backup_controller.py   # Backups do sistema
│
├── models/                    # 💾 Camada de dados (MVC - Model)
│   ├── database_manager.py    # Operações no banco
│   └── backup_manager.py      # Gestão de backups
│
├── views/                     # 🎨 Interface web (MVC - View)
│   ├── templates/            # HTML
│   └── static/               # CSS e JavaScript
│
├── tests/                     # 🧪 Testes automatizados (91.63% cobertura)
│   ├── conftest.py           # Fixtures compartilhadas
│   ├── test_app.py           # Testes de rotas
│   ├── test_controllers.py   # Testes dos controllers
│   ├── test_database_manager.py  # Testes do DB
│   └── test_backup_manager.py    # Testes de backup
│
└── backups_json/             # 💾 Backups automáticos
```

## 🚀 Como Executar

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Executar aplicação:**
   ```bash
   python app.py
   ```

3. **Acessar sistema:**
   - URL: http://127.0.0.1:5000
   - Login padrão: `admin` / `admin123`

## ⚙️ Funcionalidades

### ✅ Gestão de Produtos
- Cadastrar, editar e remover produtos
- Sistema automático de reset de IDs ao zerar tabela
- Controle de disponibilidade

### ✅ Gestão de Pedidos
- Criar pedidos com múltiplos itens
- Atualizar status: Pendente → Preparando → Pronto → Entregue
- Histórico de pedidos entregues
- Limpar histórico (apenas admin)

### ✅ Gestão de Usuários
- Criar usuários (admin ou gerente)
- Remover usuários
- Controle de permissões

### ✅ Backups
- Backup automático do banco de dados
- Exportação em JSON
- Restauração de backups

## 🔧 Utilitários

### resetar_ids.py (Opcional)
Utilitário para reorganizar tabelas:
- Produtos
- Usuários
- Pedidos
- Histórico

```bash
python resetar_ids.py
```

## 📝 Notas

- **Reset Automático:** Ao apagar todos os produtos, o sistema automaticamente reseta o sistema
- **Autenticação:** Todas as rotas da API requerem autenticação via session
- **Permissões:** Algumas ações (criar backups, limpar histórico) são exclusivas do admin

## 🧪 Testes

O projeto possui uma suíte completa de testes automatizados com **91.63% de cobertura**.

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=. --cov-report=term-missing

# Gerar relatório HTML
pytest tests/ --cov=. --cov-report=html
```

### Estatísticas de Testes

- **Total de Testes:** 99
- **Testes Passando:** 99 ✅
- **Cobertura de Código:** 91.63%
- **Tempo de Execução:** ~15 segundos

## 📊 Documentação da API

Para documentação completa da API no Postman, veja a descrição na collection:
https://thalisfel-7112172.postman.co/workspace/Thalis-Felipe's-Workspace~f5d46bb1-45e0-4e52-81ee-c9e9788846b1/collection/49341878-553d17db-cc43-4bcf-8bc1-58f3d7587acc?action=share&creator=49341878&active-environment=49341878-207374d2-430c-4caf-abee-4af6f0c0713a

**Base URL:** `http://127.0.0.1:5000`

### Principais Endpoints

- **POST** `/api/login` - Autenticação
- **GET** `/api/produtos` - Listar produtos
- **POST** `/api/produtos` - Criar produto
- **GET** `/api/pedidos` - Listar pedidos
- **POST** `/api/pedidos` - Criar pedido
- **PUT** `/api/pedidos/{id}/status` - Atualizar status
- **GET** `/api/estatisticas` - Estatísticas gerais
- **POST** `/api/backup` - Criar backup

Consulte o arquivo de descrição do Postman para documentação completa de todos os endpoints.
