document.addEventListener("DOMContentLoaded", function() { console.log("script.js is loaded successfully!");

    // Example: Add interactivity to an 'Adopt Now' button
    let adoptButton = document.getElementById("adopt-btn");
    if (adoptButton) {
        adoptButton.addEventListener("click", function() {
            alert("Redirecting to adoption page!");
        });
    }
    
    });