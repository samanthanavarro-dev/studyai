document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const nome = document.getElementById("username").value;
    const senha = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, senha })
        });

        if (response.ok) {
            const data = await response.json();
            alert(data.message);

            // 🔹 Redireciona para o dashboard
            window.location.href = "dashboard.html";
        } else {
            alert("Usuário ou senha inválidos!");
        }
    } catch (error) {
        alert("Erro de conexão com o servidor!");
    }
});