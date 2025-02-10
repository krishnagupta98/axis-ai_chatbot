document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    chatForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        // Display user message in chat
        chatBox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;
        userInput.value = "";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage })
            });

            // Handle non-JSON responses
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${errorText}`);
            }

            const data = await response.json();

            // Display bot response
            chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.reply || data.error}</p>`;
        } catch (error) {
            console.error("Error:", error);
            chatBox.innerHTML += `<p style="color:red;"><strong>Bot:</strong> Something went wrong!</p>`;
        }
    });
});
