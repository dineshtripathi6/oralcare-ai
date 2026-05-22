import gradio as gr

# -------------------------------
# AI LOGIC
# -------------------------------
knowledge = [
    "White patch in mouth may indicate leukoplakia.",
    "Persistent ulcers can indicate oral cancer.",
    "Smoking increases oral cancer risk.",
    "Difficulty swallowing may indicate serious condition."
]

def rag(query):
    q = query.lower()
    for k in knowledge:
        if any(word in k for word in q.split()):
            return k
    return knowledge[0]

def tools(query):
    q = query.lower()

    if "white patch" in q:
        return "Possible leukoplakia", "moderate"
    if "ulcer" in q:
        return "Possible oral lesion", "high"
    if "pain" in q:
        return "Possible condition", "moderate"

    return "General oral condition", "low"

# ✅ API FUNCTION
def api_predict(text):
    insight = rag(text)
    condition, severity = tools(text)

    return {
        "condition": condition,
        "severity": severity,
        "insight": insight,
        "recommendation": "Consult a healthcare professional"
    }

# -------------------------------
# PURE EHR UI (NO GRADIO UI)
# -------------------------------
html_code = """
<div style="display:flex;font-family:Arial;margin:0;">

<div style="width:250px;background:#2c3e50;color:white;padding:20px;">
    <h3>EHR System</h3>
    <div id="agent-btn" style="margin-top:40px;padding:12px;background:#3498db;cursor:pointer;text-align:center;">
        🧠 OralCare AI
    </div>
</div>

<div style="flex:1;padding:20px;">
    <h2>Patient Record</h2>
    <p>Name: John Doe</p>
    <p>Age: 45</p>
    <p>Symptoms: TBD</p>
</div>

<div id="chatbox" style="
    position:fixed;right:20px;bottom:20px;width:320px;height:420px;
    background:white;border:1px solid #ccc;display:none;flex-direction:column;
">
    <div style="background:#3498db;color:white;padding:10px;">OralCare AI Assistant</div>
    <div id="chatBody" style="flex:1;overflow-y:auto;padding:10px;"></div>

    <div style="display:flex;">
        <input id="inputBox" style="flex:1;padding:6px;" placeholder="Enter symptoms">
        <button id="sendBtn">Send</button>
    </div>
</div>

</div>

<script>
setTimeout(() => {

    const btn = document.getElementById("agent-btn");
    const chatbox = document.getElementById("chatbox");
    const sendBtn = document.getElementById("sendBtn");

    btn.onclick = () => {
        chatbox.style.display = (chatbox.style.display === "flex") ? "none" : "flex";
    };

    sendBtn.onclick = async () => {

        const inputBox = document.getElementById("inputBox");
        const text = inputBox.value;

        const res = await fetch("/run/predict", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ data: [text] })
        });

        const data = (await res.json()).data[0];
        const chat = document.getElementById("chatBody");

        chat.innerHTML += `<b>You:</b> ${text}<br>`;
        chat.innerHTML += `<b>AI:</b> ${data.condition}<br>`;
        chat.innerHTML += `Risk: ${data.severity}<br>`;
        chat.innerHTML += `Insight: ${data.insight}<br>`;
        chat.innerHTML += `Advice: ${data.recommendation}<br><hr>`;

        inputBox.value = "";
    };

}, 500);
</script>
"""

# -------------------------------
# FINAL APP
# -------------------------------
with gr.Blocks() as demo:

    gr.HTML(html_code)

    # ✅ HIDDEN API ENDPOINT (NO UI CREATED)
    demo.queue()
    demo.fn = api_predict

demo.launch()
