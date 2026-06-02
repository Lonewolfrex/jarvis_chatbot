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
        const response = await fetch("/api/chat/sessions/", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        const sessions = await response.json();

        if (!sessions.length) {
            const createResponse = await fetch("/api/chat/sessions/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    title: "Welcome Chat"
                })
            });

            const newSession = await createResponse.json();
            currentSessionId = newSession.id;
        } else {
            currentSessionId = sessions[0].id;
        }

        const sessionInfo = document.getElementById("sessionInfo");

        if (sessionInfo) {
            sessionInfo.innerText = `Session #${currentSessionId}`;
        }

        console.log("Active Session:", currentSessionId);

    } catch (error) {
        console.error("Session Load Error:", error);

        appendMessage(
            "jarvis",
            "Unable to load chat session."
        );
    }
};

async function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();

    if (!message) return;

    if (!currentSessionId) {
        appendMessage(
            "jarvis",
            "No active session."
        );
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

        if (response.status === 401) {
            logout();
            return;
        }

        const data = await response.json();

        thinkingBubble.remove();

        appendMessage(
            "jarvis",
            data.response || "No response received."
        );

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
    div.innerText = text;

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

function logout() {
    localStorage.clear();
    sessionStorage.clear();

    window.history.pushState(null, "", "/");
    window.location.replace("/");
}