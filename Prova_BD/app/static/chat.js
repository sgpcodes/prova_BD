// Nome da sala de chat
const room = "sala1";

// Cria conexão WebSocket com o backend na sala especificada
const ws = new WebSocket(`ws://localhost:8000/ws/${room}`);

// Seletores dos elementos da interface
const chat = document.getElementById('chat'); // Área de mensagens
const msg = document.getElementById('msg');   // Input de mensagem
const send = document.getElementById('send'); // Botão de envio

// Nome do usuário (pode ser customizado)
const username = "Você";

// Evento de clique no botão de envio
send.onclick = function() {
  if (msg.value.trim() !== "") {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ username: username, content: msg.value }));
      msg.value = "";
    } else {
      alert("Conexão com o chat foi perdida. Recarregue a página.");
    }
  }
};

// Evento de conexão aberta no WebSocket
ws.onopen = () => {
    console.log("Conectado ao WebSocket!");
};

// Evento de recebimento de mensagem do servidor
ws.onmessage = function(event) {
  try {
    const data = JSON.parse(event.data);

    if (data.type === "history") {
      // Exibe histórico de mensagens
      for (const msg of data.items) {
        addMessage(msg);
      }
    } else if (data.type === "message") {
      // Exibe nova mensagem
      addMessage(data.item);
    }
  } catch {
    // Mensagem de sistema ou erro
    const div = document.createElement('div');
    div.style.color = 'gray';
    div.textContent = event.data;
    chat.appendChild(div);
  }
  // Scroll automático para a última mensagem
  chat.scrollTop = chat.scrollHeight;
};

// Função para adicionar mensagem na interface
function addMessage(msg) {
  const time = new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  const cssClass = msg.username === username ? "user" : "other";
  const div = document.createElement('div');
  div.classList.add('message', cssClass);
  div.innerHTML = `<b>${msg.username}</b><div>${msg.content}</div><span class="msg-time">${time}</span>`;
  chat.appendChild(div);
}

// Permite envio de mensagem ao pressionar Enter
msg.addEventListener("keyup", function(e) {
  if (e.key === "Enter") send.onclick();
});