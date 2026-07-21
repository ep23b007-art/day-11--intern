(function () {

    const CHATBOT_URL = "http://127.0.0.1:8000/docs";


    // Create chatbot button
    const button = document.createElement("button");

    button.innerHTML = "💬 Plan My Trip";

    button.id = "travelkeet-chat-button";


    button.style.position = "fixed";
    button.style.bottom = "20px";
    button.style.right = "20px";
    button.style.padding = "15px";
    button.style.borderRadius = "50px";
    button.style.background = "#0066ff";
    button.style.color = "white";
    button.style.border = "none";
    button.style.cursor = "pointer";


    document.body.appendChild(button);



    // Create chatbot window

    const iframe = document.createElement("iframe");

    iframe.src = CHATBOT_URL;

    iframe.style.position="fixed";
    iframe.style.bottom="80px";
    iframe.style.right="20px";
    iframe.style.width="400px";
    iframe.style.height="600px";
    iframe.style.border="none";
    iframe.style.display="none";


    document.body.appendChild(iframe);



    // Open chatbot

    button.onclick=function(){

        if(iframe.style.display==="none")
        {
            iframe.style.display="block";
        }

        else
        {
            iframe.style.display="none";
        }

    };


})();