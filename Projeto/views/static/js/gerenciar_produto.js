const apiUrl = '/api/produtos';

// Verificar autenticação ao carregar a página
async function verificarAuth() {
    try {
        const response = await fetch('/api/verificar-auth', {
            credentials: 'include'
        });

        if (!response.ok) {
            window.location.href = '/login.html';
            return false;
        }

        const data = await response.json();
        return data.autenticado;
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        window.location.href = '/login.html';
        return false;
    }
}

// Carregar produtos na seção de gerenciamento
async function carregarGerenciar() {
    const response = await fetch(apiUrl, {
        credentials: 'include'
    });
    const produtos = await response.json();
    const lista = document.getElementById('lista-gerenciar');
    lista.innerHTML = '';

    if (produtos.length === 0) {
        lista.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><h3>Nenhum produto para gerenciar</h3><p>Adicione produtos primeiro.</p></div>';
        return;
    }

    produtos.forEach(produto => {
        const div = document.createElement('div');
        div.className = 'produto';
        div.innerHTML = `
            <h3>${produto.nome}</h3>
            <p>${produto.descricao}</p>
            <p style="font-size: 1.2em; color: #28a745; font-weight: bold;">R$ ${produto.preco.toFixed(2)}</p>
            <button class="btn-warning" onclick='abrirModalEditar(${JSON.stringify(produto)})'>✏️ Editar</button>
            <button class="btn-danger" onclick="deletarProduto(${produto.id})">🗑️ Remover</button>
        `;
        lista.appendChild(div);
    });
}

// Deletar produto
async function deletarProduto(id) {
    if (!confirm('Tem certeza que deseja remover este produto?')) {
        return;
    }

    const response = await fetch(`${apiUrl}/${id}`, {
        method: 'DELETE',
        credentials: 'include'
    });

    if (response.ok) {
        alert('✅ Produto removido com sucesso!');
        carregarGerenciar();
    } else {
        alert('❌ Erro ao remover produto!');
    }
}

// Abrir modal de edição
function abrirModalEditar(produto) {
    document.getElementById('edit-id').value = produto.id;
    document.getElementById('edit-nome').value = produto.nome;
    document.getElementById('edit-descricao').value = produto.descricao;
    document.getElementById('edit-preco').value = produto.preco;
    document.getElementById('modal-editar').style.display = 'block';
}

// Fechar modal
function fecharModal() {
    document.getElementById('modal-editar').style.display = 'none';
}

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('modal-editar');
    if (event.target === modal) {
        fecharModal();
    }
}

// Atualizar produto
document.getElementById('form-editar').addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('edit-id').value;
    const nome = document.getElementById('edit-nome').value;
    const descricao = document.getElementById('edit-descricao').value;
    const preco = document.getElementById('edit-preco').value;

    const response = await fetch(`${apiUrl}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ nome, descricao, preco: parseFloat(preco) })
    });

    if (response.ok) {
        alert('✅ Produto atualizado com sucesso!');
        fecharModal();
        carregarGerenciar();
    } else {
        alert('❌ Erro ao atualizar produto!');
    }
});

// Inicializar
(async () => {
    const autenticado = await verificarAuth();
    if (autenticado) {
        carregarGerenciar();
    }
})();