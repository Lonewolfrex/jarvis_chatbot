let currentSessionId = null;

window.addEventListener("pageshow", () => {
    if (!localStorage.getItem("access")) {
        window.location.replace("/");
    }
});

window.onload = async () => {
    const token = localStorage.getItem("access");

    if (!token) {
        window.location.replace("/");
        return;
    }

    try {
        const sessions = await loadSessions();

        if (sessions.length) {
            currentSessionId = sessions[0].id;

            document.getElementById("sessionInfo").innerText =
                sessions[0].title;

            await loadMessages(currentSessionId);
        } else {
            await createNewChat();
        }

    } catch (error) {
        console.error(error);
        appendMessage("jarvis", "Unable to load chat session.");
    }
};

async function loadSessions() {
    const token = localStorage.getItem("access");

    const response = await fetch("/api/chat/sessions/", {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (response.status === 401) {
        logout();
        return [];
    }

    const sessions = await response.json();

    const container = document.getElementById("sessionsList");

    container.innerHTML = "";

    sessions.forEach(session => {

        const item = document.createElement("div");

        item.className = "session-item";

        if (session.id === currentSessionId) {
            item.classList.add("active-session");
        }

        item.innerText = session.title;

        item.onclick = () => switchSession(session.id);

        container.appendChild(item);
    });

    return sessions;
}

async function loadMessages(sessionId) {

    const token = localStorage.getItem("access");

    const response = await fetch(
        `/api/chat/sessions/${sessionId}/messages/`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    const messages = await response.json();

    const container = document.getElementById("messages");

    container.innerHTML = "";

    messages.forEach(msg => {
        appendMessage(
            msg.role === "assistant" ? "jarvis" : "user",
            msg.content
        );
    });
}

async function switchSession(sessionId) {

    currentSessionId = sessionId;

    await loadMessages(sessionId);

    const selected = document.querySelector(
        `.session-item:nth-child(${Array.from(document.querySelectorAll(".session-item"))
        .findIndex(x => x.onclick.toString().includes(sessionId)) + 1})`
    );

    if (selected) {
        document.getElementById("sessionInfo").innerText =
            selected.innerText;
    }

    await loadSessions();
}

async function createNewChat() {

    const token = localStorage.getItem("access");

    const response = await fetch("/api/chat/sessions/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            title: "New Chat"
        })
    });

    const session = await response.json();

    currentSessionId = session.id;

    document.getElementById("messages").innerHTML = "";

    document.getElementById("sessionInfo").innerText =
        session.title;

    await loadSessions();
}

async function sendMessage() {

    const input = document.getElementById("messageInput");

    const message = input.value.trim();

    if (!message || !currentSessionId) {
        return;
    }

    appendMessage("user", message);

    input.value = "";

    const thinkingBubble = showThinkingAnimation();

    try {

        const token = localStorage.getItem("access");

        const response = await fetch("/api/chat/prompt/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        const data = await response.json();

        thinkingBubble.remove();

        typeJarvisResponse(
            data.response || "No response received."
        );

        await loadSessions();

    } catch (error) {

        console.error(error);

        thinkingBubble.remove();

        appendMessage(
            "jarvis",
            "Unable to contact Jarvis."
        );
    }
}

function appendMessage(sender, text) {

    const messages = document.getElementById("messages");

    const div = document.createElement("div");

    div.className = `message ${sender}`;

    if (sender === "jarvis") {

        div.innerHTML = marked.parse(text);

        div.querySelectorAll("pre code").forEach(block => {
            hljs.highlightElement(block);
        });

    } else {
        div.textContent = text;
    }

    messages.appendChild(div);

    messages.scrollTop = messages.scrollHeight;

    return div;
}

function showThinkingAnimation() {

    const messages = document.getElementById("messages");

    const div = document.createElement("div");

    div.className = "message jarvis typing";

    div.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    messages.appendChild(div);

    messages.scrollTop = messages.scrollHeight;

    return div;
}

function typeJarvisResponse(text) {

    const messages = document.getElementById("messages");

    const div = document.createElement("div");

    div.className = "message jarvis";

    messages.appendChild(div);

    let index = 0;

    const interval = setInterval(() => {

        div.textContent += text.charAt(index);

        messages.scrollTop = messages.scrollHeight;

        index++;

        if (index >= text.length) {

            clearInterval(interval);

            div.innerHTML = marked.parse(text);

            div.querySelectorAll("pre code").forEach(block => {
                hljs.highlightElement(block);
            });
        }

    }, 12);
}

function logout() {

    localStorage.clear();
    sessionStorage.clear();

    window.history.pushState(null, "", "/");

    window.location.replace("/");
}