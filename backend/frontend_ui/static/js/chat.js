let currentSessionId=null;
let sessionsCache=[];
let generationStopped=false;

async function refreshAccessToken(){
    const refresh=localStorage.getItem("refresh");

    if(!refresh){
        logout();
        return null;
    }

    try{
        const response=await fetch("/api/refresh/",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({refresh})
        });

        if(!response.ok){
            logout();
            return null;
        }

        const data=await response.json();

        localStorage.setItem("access",data.access);

        return data.access;

    }catch{
        logout();
        return null;
    }
}

async function getAccessToken(){
    let token=localStorage.getItem("access");

    if(!token){
        token=await refreshAccessToken();
    }

    return token;
}

window.addEventListener("pageshow",()=>{
    if(!localStorage.getItem("access")){
        window.location.replace("/");
    }
});

window.onload=async()=>{
    try{
        const token=await getAccessToken();

        if(!token){
            window.location.replace("/");
            return;
        }

        const sessions=await loadSessions();

        if(sessions.length){
            currentSessionId=sessions[0].id;

            document.getElementById("sessionInfo").innerText=
                sessions[0].title;

            await loadMessages(currentSessionId);
        }else{
            await createNewChat();
        }

    }catch(error){
        console.error(error);
        appendMessage("jarvis","Unable to load chat session.");
    }
};

async function loadSessions(){

    const token=await getAccessToken();

    const response=await fetch("/api/chat/sessions/",{
        headers:{
            Authorization:`Bearer ${token}`
        }
    });

    if(response.status===401){
        logout();
        return [];
    }

    const sessions=await response.json();

    sessionsCache=sessions;

    const container=document.getElementById("sessionsList");

    container.innerHTML="";

    sessions.forEach(session=>{

        const item=document.createElement("div");

        item.className=
            `session-item ${
                session.id===currentSessionId
                ?"active-session"
                :""
            }`;

        item.innerHTML=`
        <div class="session-title">
            ${session.title}
        </div>

        <div class="session-menu-btn">
            ⋮
        </div>

        <div class="session-dropdown">
            <div class="rename-action">
                ✏ Rename
            </div>

            <div class="delete-action">
                🗑 Delete
            </div>
        </div>
        `;

        item.querySelector(".session-title")
            .onclick=()=>switchSession(session.id, session.title);

        item.querySelector(".session-menu-btn")
            .onclick=(e)=>{
                e.stopPropagation();

                document
                .querySelectorAll(".session-dropdown")
                .forEach(d=>{

                    if(
                        d!==item.querySelector(".session-dropdown")
                    ){
                        d.style.display="none";
                    }
                });

                const dropdown=
                    item.querySelector(".session-dropdown");

                dropdown.style.display=
                    dropdown.style.display==="block"
                    ?"none"
                    :"block";
            };

        item.querySelector(".rename-action")
            .onclick=()=>renameChat(session.id);

        item.querySelector(".delete-action")
            .onclick=()=>deleteChat(session.id);

        container.appendChild(item);
    });

    return sessions;
}

async function loadMessages(sessionId){

    const token=await getAccessToken();

    const response=await fetch(
        `/api/chat/sessions/${sessionId}/messages/`,
        {
            headers:{
                Authorization:`Bearer ${token}`
            }
        }
    );

    const messages=await response.json();

    const container=document.getElementById("messages");

    container.innerHTML="";

    messages.forEach(msg=>{
        appendMessage(
            msg.role==="assistant"
                ? "jarvis"
                : "user",
            msg.content
        );
    });
}

async function switchSession(sessionId,title){

    currentSessionId=sessionId;

    document.getElementById("sessionInfo")
        .innerText=title;

    await loadMessages(sessionId);

    await loadSessions();
}

async function createNewChat(){

    const token=await getAccessToken();

    const response=await fetch("/api/chat/sessions/",{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            Authorization:`Bearer ${token}`
        },
        body:JSON.stringify({
            title:"New Chat"
        })
    });

    const session=await response.json();

    currentSessionId=session.id;

    document.getElementById("messages")
        .innerHTML="";

    document.getElementById("sessionInfo")
        .innerText=session.title;

    await loadSessions();
}

async function sendMessage(){

    generationStopped=false;

    const input=document.getElementById("messageInput");

    const message=input.value.trim();

    if(!message || !currentSessionId){
        return;
    }

    appendMessage("user",message);

    input.value="";

    const thinkingBubble=showThinkingAnimation();

    try{

        thinkingBubble.remove();

        await streamMessage(message);

        await loadSessions();

    }catch(error){

        console.error(error);

        thinkingBubble.remove();

        appendMessage(
            "jarvis",
            "Unable to contact Jarvis."
        );
    }
}

function appendMessage(sender,text){

    const messages=document.getElementById("messages");

    const div=document.createElement("div");

    div.className=`message ${sender}`;

    if(sender==="jarvis"){

        div.innerHTML=`
            <div class="message-actions">
                <button onclick="copyMessage(this)">
                    📋
                </button>
                <button onclick="regenerateResponse()">
                    🔄
                </button>
            </div>
            ${marked.parse(text)}
            `;

        if(window.hljs){
            div.querySelectorAll("pre code")
            .forEach(block=>{
                hljs.highlightElement(block);
            });
        }

    }else{
        div.textContent=text;
    }

    messages.appendChild(div);

    messages.scrollTop=messages.scrollHeight;

    return div;
}

function typeJarvisResponse(text){

    const messages=
        document.getElementById("messages");

    const div=
        document.createElement("div");

    div.className="message jarvis";

    messages.appendChild(div);

    let index=0;

    const timer=setInterval(()=>{

        div.textContent+=text[index];

        index++;

        if(generationStopped || index>=text.length){

            clearInterval(timer);

            div.innerHTML=
                marked.parse(text);

            if(window.hljs){

                div.querySelectorAll(
                    "pre code"
                ).forEach(block=>{

                    hljs.highlightElement(
                        block
                    );

                });
            }
        }

        requestAnimationFrame(()=>{
            messages.scrollTop=
                messages.scrollHeight;
        });

    },8);
}

function showThinkingAnimation(){

    const messages=document.getElementById("messages");

    const div=document.createElement("div");

    div.className="message jarvis typing";

    div.innerHTML=`
        <span></span>
        <span></span>
        <span></span>
    `;

    messages.appendChild(div);

    messages.scrollTop=messages.scrollHeight;

    return div;
}

function filterChats(){

    const value=
        document
        .getElementById("chatSearch")
        .value
        .toLowerCase();

    document
    .querySelectorAll(".session-item")
    .forEach(chat=>{

        const title=
            chat
            .querySelector(".session-title")
            .innerText
            .toLowerCase();

        chat.style.display=
            title.includes(value)
            ?"flex"
            :"none";
    });
}

function toggleSessionMenu(event){

    event.stopPropagation();

    document.querySelectorAll(".session-dropdown")
        .forEach(menu=>{
            menu.style.display="none";
        });

    const menu=
        event.currentTarget
            .querySelector(".session-dropdown");

    menu.style.display="block";
}

async function renameChat(sessionId){

    const title=prompt(
        "Rename chat"
    );

    if(!title)return;

    const token=await getAccessToken();

    await fetch(
        `/api/chat/sessions/${sessionId}/`,
        {
            method:"PATCH",
            headers:{
                "Content-Type":"application/json",
                Authorization:`Bearer ${token}`
            },
            body:JSON.stringify({
                title:title
            })
        }
    );

    await loadSessions();
}

async function deleteChat(sessionId){

    if(
        !confirm(
            "Delete this chat?"
        )
    ){
        return;
    }

    const token=
        await getAccessToken();

    await fetch(
        `/api/chat/sessions/${sessionId}/`,
        {
            method:"DELETE",
            headers:{
                Authorization:
                `Bearer ${token}`
            }
        }
    );

    if(currentSessionId===sessionId){

        currentSessionId=null;

        document
            .getElementById(
                "messages"
            )
            .innerHTML="";
    }

    await loadSessions();
}

function escapeHtml(text){

    const div=document.createElement("div");

    div.textContent=text;

    return div.innerHTML;
}

function logout(){

    localStorage.clear();
    sessionStorage.clear();

    window.location.replace("/");
}

document.addEventListener(
    "click",
    ()=>{
        document
        .querySelectorAll(".session-dropdown")
        .forEach(
            d=>d.style.display="none"
        );
    }
);

function copyMessage(button){

    const text=
        button.parentElement
        .parentElement
        .innerText;

    navigator.clipboard.writeText(
        text
    );
}

async function regenerateResponse(){

    if(!currentSessionId){
        return;
    }

    const thinkingBubble=
        showThinkingAnimation();

    try{

        const token=
            await getAccessToken();

        const response=
            await fetch(
                "/api/chat/regenerate/",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json",
                        Authorization:`Bearer ${token}`
                    },
                    body:JSON.stringify({
                        session_id:currentSessionId
                    })
                }
            );

        const data=
            await response.json();

        thinkingBubble.remove();

        typeJarvisResponse(
            data.response
        );

    }catch(err){

        thinkingBubble.remove();

        appendMessage(
            "jarvis",
            "Failed to regenerate response."
        );
    }
}

function stopGeneration(){

    generationStopped=true;

    const btn=
        document.getElementById(
            "sendButton"
        ).innerHTML="■ Stop";

        document.getElementById(
            "sendButton"
        ).onclick=stopGeneration;

    btn.innerHTML="➤ Send";

    btn.onclick=sendMessage;
}

async function streamMessage(message){

    const token=
        await getAccessToken();

    const response=
        await fetch(
            "/api/chat/stream/",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                    Authorization:`Bearer ${token}`
                },
                body:JSON.stringify({
                    session_id:currentSessionId,
                    message:message
                })
            }
        );

    const reader=
        response.body.getReader();

    const decoder=
        new TextDecoder();

    const div=
        appendMessage(
            "jarvis",
            ""
        );

    let fullText="";

    while(true){

        const {
            done,
            value
        }=
        await reader.read();

        if(done){
            break;
        }

        const chunk=
            decoder.decode(value);

        fullText+=chunk;

        div.innerHTML=
            marked.parse(fullText);

        document
            .getElementById("messages")
            .scrollTop=
            document
            .getElementById("messages")
            .scrollHeight;
    }
}

