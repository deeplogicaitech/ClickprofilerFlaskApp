const saveCheckbox = document.getElementById("saveFilesCheckbox");
const saveMappingInput = document.getElementById("saveMappingInput");

saveCheckbox.addEventListener("change", function () {
  if (saveCheckbox.checked) {
    saveMappingInput.style.display = 'flex';
  } else {
    saveMappingInput.classList.add("animate__flipOutX");
      setTimeout(function () {
        saveMappingInput.classList.remove("animate__flipOutX");
        saveMappingInput.style.display = "none";
      }, 500);
  }
});
