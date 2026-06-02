let currentSessionId = null;

window.onload = async function () {

    try {

        const token =
            localStorage.getItem("access");

        if (!token) {

            window.location.href =
                "/login/";

            return;
        }

        // Load existing sessions

        const response =
            await fetch(
                "/api/chat/sessions/",
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            "Bearer " + token
                    }
                }
            );

        if (!response.ok) {

            console.error(
                "Failed to load sessions:",
                response.status
            );

            return;
        }

        const sessions =
            await response.json();

        console.log(
            "Loaded sessions:",
            sessions
        );

        // Existing session found

        if (
            Array.isArray(sessions) &&
            sessions.length > 0
        ) {

            currentSessionId =
                sessions[0].id;

            updateSessionInfo();

            console.log(
                "Using existing session:",
                currentSessionId
            );
        }

        // No session exists → create one automatically

        else {

            console.log(
                "No sessions found. Creating one..."
            );

            const createResponse =
                await fetch(
                    "/api/chat/sessions/",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json",
                            "Authorization":
                                "Bearer " + token
                        },
                        body: JSON.stringify({
                            title: "New Chat"
                        })
                    }
                );

            const newSession =
                await createResponse.json();

            currentSessionId =
                newSession.id;

            updateSessionInfo();

            console.log(
                "Created session:",
                currentSessionId
            );
        }

    } catch (error) {

        console.error(
            "Session Load Error:",
            error
        );
    }
};


async function sendMessage() {

    try {

        const input =
            document.getElementById(
                "messageInput"
            );

        if (!input) {

            console.error(
                "messageInput not found"
            );

            return;
        }

        const message =
            input.value.trim();

        if (!message) {
            return;
        }

        if (!currentSessionId) {

            appendMessage(
                "jarvis",
                "No active session available."
            );

            return;
        }

        appendMessage(
            "user",
            message
        );

        input.value = "";

        const token =
            localStorage.getItem(
                "access"
            );

        const response =
            await fetch(
                "/api/chat/prompt/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                        "Authorization":
                            "Bearer " + token
                    },
                    body: JSON.stringify({
                        session_id:
                            currentSessionId,
                        message:
                            message
                    })
                }
            );

        console.log(
            "HTTP Status:",
            response.status
        );

        const text =
            await response.text();

        console.log(
            "Raw Response:",
            text
        );

        let data;

        try {

            data =
                JSON.parse(text);

        } catch (error) {

            console.error(
                "JSON Parse Error:",
                error
            );

            appendMessage(
                "jarvis",
                "Invalid response received from backend."
            );

            return;
        }

        console.log(
            "Prompt Response:",
            data
        );

        if (data.detail) {

            appendMessage(
                "jarvis",
                "Authentication failed. Please login again."
            );

            console.error(data);

            return;
        }

        appendMessage(
            "jarvis",
            data.response ||
            "No response received."
        );

    } catch (error) {

        console.error(
            "SEND ERROR:",
            error
        );

        appendMessage(
            "jarvis",
            "Unable to contact Jarvis."
        );
    }
}


function appendMessage(sender, text) {

    const messagesDiv =
        document.getElementById(
            "messages"
        );

    const messageDiv =
        document.createElement(
            "div"
        );

    messageDiv.classList.add(
        "message"
    );

    messageDiv.classList.add(
        sender
    );

    messageDiv.innerText =
        text;

    messagesDiv.appendChild(
        messageDiv
    );

    messagesDiv.scrollTop =
        messagesDiv.scrollHeight;
}


function updateSessionInfo() {

    const sessionInfo =
        document.getElementById(
            "sessionInfo"
        );

    if (
        sessionInfo &&
        currentSessionId
    ) {

        sessionInfo.innerText =
            "Session #" +
            currentSessionId;
    }
}


function logout() {

    localStorage.removeItem(
        "access"
    );

    localStorage.removeItem(
        "refresh"
    );

    window.location.href =
        "/login/";
}