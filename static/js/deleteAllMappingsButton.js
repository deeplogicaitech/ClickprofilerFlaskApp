// JavaScript to update the text on hover
const divider = document.querySelector(".hr-text");
const dividerContent = document.querySelector(".divider-content");
const dividerText = dividerContent.querySelector(".divider-text");

const originalText = "Saved Mappings";
const hoverText = "Delete all mappings";

dividerContent.addEventListener("mouseover", () => {
  dividerText.textContent = hoverText;
});

dividerContent.addEventListener("mouseout", () => {
  dividerText.textContent = originalText;
  // Add underline to the text
  dividerText.style.textDecoration = "underline";
  dividerText.style.textUnderlinePosition = "under";
  dividerText.style.textDecorationStyle = "dotted";
});
