/* GSF Jubileum — Intervju-frontend */
(function () {
    "use strict";

    const root       = document.querySelector(".gsf-interview-root");
    if (!root) return;

    const token      = root.dataset.token;
    const submitted  = root.dataset.submitted === "true";
    const LS_KEY     = "gsf_jubileum_draft_" + token;
    if (submitted) {
        localStorage.removeItem(LS_KEY);
        return;
    }

    const chatWindow = document.getElementById("gsf-chat-window");
    const input      = document.getElementById("gsf-input");
    const sendBtn    = document.getElementById("gsf-send-btn");
    const submitBtn  = document.getElementById("gsf-submit-btn");
    const typing     = document.getElementById("gsf-typing");
    const summaryPanel   = document.getElementById("gsf-summary-panel");
    const consentPublish = document.getElementById("gsf-consent-publish");
    const consentContact = document.getElementById("gsf-consent-contact");
    const consentComment = document.getElementById("gsf-consent-comment");
    const confirmBtn     = document.getElementById("gsf-confirm-submit-btn");

    if (!chatWindow || !input || !sendBtn) return;

    // ── Hjälpfunktioner ──────────────────────────────────────────────────

    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function appendBubble(role, content) {
        const wrap = document.createElement("div");
        wrap.className = "gsf-bubble gsf-bubble-" + role;
        const sender = document.createElement("span");
        sender.className = "gsf-bubble-sender";
        sender.textContent = role === "assistant" ? "Clio" : "Du";
        const p = document.createElement("p");
        p.textContent = content;
        wrap.appendChild(sender);
        wrap.appendChild(p);
        chatWindow.insertBefore(wrap, typing);
        scrollToBottom();
    }

    function setLoading(on) {
        sendBtn.disabled = on;
        input.disabled   = on;
        if (typing) typing.style.display = on ? "block" : "none";
        scrollToBottom();
    }

    async function jsonRpc(path, params) {
        const resp = await fetch(path, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                id: Date.now(),
                params: params,
            }),
        });
        const data = await resp.json();
        if (data.error) throw new Error(data.error.data?.message || data.error.message || "Fel");
        return data.result;
    }

    // ── Skicka meddelande ─────────────────────────────────────────────────

    async function sendMessage() {
        const message = (input.value || "").trim();
        if (!message) return;

        appendBubble("user", message);
        input.value = "";
        setLoading(true);

        try {
            const result = await jsonRpc("/jubileum/" + token + "/chat", { message });
            if (result.error) {
                appendBubble("assistant", "⚠️ " + result.error);
            } else {
                appendBubble("assistant", result.reply);
                // Visa "Skicka in"-knapp om Clio nämner slutet av intervjun
                const replyLower = (result.reply || "").toLowerCase();
                if (replyLower.includes("skicka in") || replyLower.includes("färdig") || replyLower.includes("klicka")) {
                    if (submitBtn) submitBtn.style.display = "inline-block";
                }
            }
        } catch (e) {
            appendBubble("assistant", "⚠️ Något gick fel. Försök igen om en stund.");
            console.error("gsf_jubileum chat error:", e);
        } finally {
            setLoading(false);
            input.focus();
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Alltid synlig submit-knapp via manuell trigger (Shift+Enter skickar radbrytning)
    if (submitBtn) {
        submitBtn.addEventListener("click", function () {
            if (summaryPanel) summaryPanel.style.display = "block";
            summaryPanel.scrollIntoView({ behavior: "smooth" });
        });
    }

    // ── Bekräfta och skicka in ────────────────────────────────────────────

    if (confirmBtn) {
        confirmBtn.addEventListener("click", async function () {
            confirmBtn.disabled = true;
            confirmBtn.textContent = "Skickar…";
            try {
                const result = await jsonRpc("/jubileum/" + token + "/submit", {
                    samtycke: {
                        godkand_publicering:    consentPublish ? consentPublish.checked : false,
                        vill_bli_kontaktad_igen: consentContact ? consentContact.checked : false,
                        kommentar:               consentComment ? consentComment.value : "",
                    },
                });
                if (result && result.ok) {
                    localStorage.removeItem(LS_KEY);
                    // Ladda om sidan — servern visar tackvyn
                    window.location.reload();
                } else {
                    alert("Något gick fel vid inlämningen. Försök igen.");
                    confirmBtn.disabled = false;
                    confirmBtn.textContent = "Bekräfta och skicka in";
                }
            } catch (e) {
                alert("Nätverksfel. Försök igen.");
                confirmBtn.disabled = false;
                confirmBtn.textContent = "Bekräfta och skicka in";
                console.error("gsf_jubileum submit error:", e);
            }
        });
    }

    // ── localStorage-backup av pågående inmatning ─────────────────────────
    const saved  = localStorage.getItem(LS_KEY);
    if (saved && input) input.value = saved;

    let saveTimer;
    if (input) {
        input.addEventListener("input", function () {
            clearTimeout(saveTimer);
            saveTimer = setTimeout(function () {
                localStorage.setItem(LS_KEY, input.value);
            }, 1500);
        });
    }

    // Scrolla till botten vid sidladdning om konversation finns
    scrollToBottom();

    // Visa submit-knapp om konversation redan påbörjats (>2 meddelanden)
    const existingBubbles = chatWindow.querySelectorAll(".gsf-bubble").length;
    if (existingBubbles >= 4 && submitBtn) {
        submitBtn.style.display = "inline-block";
    }

}());
