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

// Cadastrar produto
document.getElementById('form-cadastro').addEventListener('submit', async (e) => {
    e.preventDefault();
    const nome = document.getElementById('nome').value;
    const descricao = document.getElementById('descricao').value;
    const preco = document.getElementById('preco').value;

    try {
        const response = await fetch('/api/produtos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ nome, descricao, preco })
        });

        if (response.ok) {
            alert('✅ Produto cadastrado com sucesso!');
            document.getElementById('form-cadastro').reset();
        } else {
            alert('❌ Erro ao cadastrar produto!');
        }
    } catch (error) {
        console.error('Erro ao cadastrar:', error);
        alert('❌ Erro ao conectar com o servidor!');
    }
});

// Inicializar
verificarAuth();