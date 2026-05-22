import gradio as gr

# -------------------------------
# KNOWLEDGE BASE
# -------------------------------
knowledge = [
    "White patch in mouth may indicate leukoplakia, a precancerous lesion.",
    "Persistent ulcers can be early signs of oral cancer.",
    "Smoking increases oral cancer risk.",
    "Difficulty swallowing may indicate serious oral conditions."
]

# -------------------------------
# RAG (Simple lightweight)
# -------------------------------
def rag(query):
    q = query.lower()

    for k in knowledge:
        if any(word in k for word in q.split()):
            return k

    return knowledge[0]

# -------------------------------
# MCP LOGIC
# -------------------------------
def tools(query):
    q = query.lower()

    if "white patch" in q:
        return "Possible leukoplakia", "moderate"

    if "ulcer" in q:
        return "Possible oral lesion", "high"

    if "pain" in q:
        return "Possible underlying condition", "moderate"

    return "General oral condition", "low"

# -------------------------------
# API FUNCTION (FOR INTEGRATION)
# -------------------------------
def api_predict(query):
    insight = rag(query)
    condition, severity = tools(query)

    return {
        "condition": condition,
        "severity": severity,
        "insight": insight,
        "recommendation": "Consult a healthcare professional"
    }

# -------------------------------
# EHR UI (HTML + JS)
# -------------------------------
html_code = """
<html>
<head>
<style>
body {
    display: flex;
    font-family: Arial;
    margin: 0;
}

.sidebar {
    width: 250px;
    background: #2c3e50;
    color: white;
    padding: 20px;
}

.main {
    flex: 1;
    padding: 20px;
}

.agent-icon {
    margin-top: 40px;
    padding: 12px;
    background: #3498db;
    cursor: pointer;
    text-align: center;
}

.chatbox {
    position: fixed;
    right: 20px;
    bottom: 20px;
    width: 320px;
    height: 420px;
    background: white;
    border: 1px solid #ccc;
    display: none;
    flex-direction: column;
}

.chat-header {
    background: #3498db;
    color: white;
    padding: 10px;
}

.chat-body {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
}

.chat-input {
    display: flex;
}

.chat-input input {
    flex: 1;
    padding: 6px;
}

.chat-input button {
    padding: 6px;
}
</style>
</head>

<body>

<div class="sidebar">
    <h3>EHR System</h3>
    <div class="agent-icon" onclick="toggleChat()">
        🧠 OralCare AI
    </div>
</div>

<div class="main">
    <h2>Patient Record</h2>
    <p>Name: John Doe</p>
    <p>Age: 45</p>
    <p>Symptoms: TBD</p>
</div>

<div class="chatbox" id="chatbox">
    <div class="chat-header">OralCare AI Assistant</div>

    <div class="chat-body" id="chatBody"></div>

    <div class="chat-input">
        <input id="input" placeholder="Enter symptoms">
        <button onclick="send()">Send</button>
    </div>
</div>

<script>

function toggleChat() {
    let box = document.getElementById("chatbox");
    box.style.display = box.style.display === "flex" ? "none" : "flex";
    box.style.flexDirection = "column";
}

async function send() {

    let text = document.getElementById("input").value;

    let res = await fetch("/run/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ data: [text] })
    });

    let response = await res.json();
    let data = response.data[0];

    let chat = document.getElementById("chatBody");

    chat.innerHTML += `<b>You:</b> ${text}<br>`;
    chat.innerHTML += `<b>AI:</b> ${data.condition}<br>`;
    chat.innerHTML += `Risk: ${data.severity}<br>`;
    chat.innerHTML += `Insight: ${data.insight}<br>`;
    chat.innerHTML += `Advice: ${data.recommendation}<br><hr>`;

    document.getElementById("input").value = "";
}

</script>

</body>
</html>
"""

# -------------------------------
# GRADIO APP
# -------------------------------
with gr.Blocks() as demo:

    gr.HTML(html_code)

    # hidden API endpoint
    gr.Interface(
        fn=api_predict,
        inputs="text",
        outputs="json",
        visible=False
    )

demo.launch()
