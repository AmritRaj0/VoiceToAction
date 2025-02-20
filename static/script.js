document.getElementById("uploadForm").addEventListener("submit", function (event) {
    event.preventDefault();

    let formData = new FormData();
    formData.append("email", document.getElementById("email").value);
    formData.append("audio_file", document.getElementById("audio_file").files[0]);

    let loadingDiv = document.getElementById("loading");
    let responseDiv = document.getElementById("response");

    // Show loading message and hide response
    loadingDiv.style.display = "block";
    responseDiv.classList.add("hidden");

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/", true);

    xhr.onload = function () {
        loadingDiv.style.display = "none"; // Hide loading after processing

        if (xhr.status === 200) {
            let result = JSON.parse(xhr.responseText);

            if (result.error) {
                alert("Error: " + result.error);
            } else {
                document.getElementById("transcription").innerText = result.transcribed_text;
                document.getElementById("tasks").innerText = result.extracted_report;
                document.getElementById("emailStatus").innerText = result.message;
                responseDiv.classList.remove("hidden"); // Show response
            }
        } else {
            alert("Failed to upload the file.");
        }
    };

    xhr.send(formData);
});
