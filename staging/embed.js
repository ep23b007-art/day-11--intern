(function () {

    // Configuration
    const CONFIG = {
        apiUrl: "http://127.0.0.1:8000"
    };

    // Create chatbot button
    const button = document.createElement("button");

    button.innerHTML = "💬 Plan My Trip";
    button.id = "travelkeet-chat-button";

    button.style.position = "fixed";
    button.style.bottom = "20px";
    button.style.right = "20px";
    button.style.padding = "15px 20px";
    button.style.borderRadius = "50px";
    button.style.background = "#0066ff";
    button.style.color = "white";
    button.style.border = "none";
    button.style.cursor = "pointer";
    button.style.boxShadow = "0px 4px 12px rgba(0,0,0,0.2)";
    button.style.fontSize = "16px";
    button.style.fontWeight = "bold";
    button.style.zIndex = "9999";

    document.body.appendChild(button);

    // Create iframe
    const iframe = document.createElement("iframe");

    iframe.src = "http://localhost:5500/chat.html";

    iframe.style.position = "fixed";
    iframe.style.bottom = "80px";
    iframe.style.right = "20px";
    iframe.style.width = "400px";
    iframe.style.height = "600px";
    iframe.style.maxWidth = "95vw";
    iframe.style.maxHeight = "90vh";
    iframe.style.border = "1px solid #ccc";
    iframe.style.borderRadius = "10px";
    iframe.style.background = "#fff";
    iframe.style.display = "none";
    iframe.style.zIndex = "9998";

    document.body.appendChild(iframe);

    // Toggle iframe
    button.onclick = function () {

        if (iframe.style.display === "none") {

            button.innerHTML = "Loading...";

            iframe.style.display = "block";

        } else {

            iframe.style.display = "none";

            button.innerHTML = "💬 Plan My Trip";

        }

    };

    iframe.onload = function () {

        button.innerHTML = "💬 Plan My Trip";

    };

    iframe.onerror = function () {

        alert("Unable to connect to TravelKeet server.");

        button.innerHTML = "💬 Plan My Trip";

    };

})();