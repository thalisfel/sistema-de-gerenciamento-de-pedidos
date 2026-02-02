document.getElementById('form-login').addEventListener('submit', async (e) => {
    e.preventDefault();

    const usuario = document.getElementById('usuario').value;
    const senha = document.getElementById('senha').value;
    const errorDiv = document.getElementById('error-message');

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ usuario, senha })
        });

        const data = await response.json();

        if (response.ok) {
            alert('✅ ' + data.mensagem);
            window.location.href = '/pedidos';
        } else {
            errorDiv.textContent = '❌ ' + data.mensagem;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 3000);
        }
    } catch (error) {
        errorDiv.textContent = '❌ Erro ao conectar com o servidor!';
        errorDiv.style.display = 'block';
    }
});