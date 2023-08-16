// Show the error card and then remove it after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
  var errorCard = document.getElementById("error-card");
  if (errorCard) {
    errorCard.style.display = "block"; // Show the error card
    setTimeout(function () {
      errorCard.classList.add("fade-out"); // Apply the fade-out class
      setTimeout(function () {
        errorCard.parentNode.removeChild(errorCard); // Remove the card from its parent node
      }, 500);
    }, 5000);
  }
});
