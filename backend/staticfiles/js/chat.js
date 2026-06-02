async function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value;

    if (!message) return;

    addMessage(message, "user");

    input.value = "";

    const token = localStorage.getItem("access");

    const res = await fetch("/api/chat/prompt/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            session_id: 1,
            message: message
        })
    });

    const data = await res.json();

    addMessage(data.response, "bot");
}

function addMessage(text, type) {
    const div = document.createElement("div");
    div.classList.add("message", type);
    div.innerText = text;

    document.getElementById("messages").appendChild(div);

    document.getElementById("messages").scrollTop =
        document.getElementById("messages").scrollHeight;
}

function logout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    window.location.href = "/login/";
}