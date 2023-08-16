// Add client-side validation for file inputs
document.addEventListener("DOMContentLoaded", function () {
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach((input) => {
    input.addEventListener("change", function () {
      const file = this.files[0];
      const allowedExtensions = ["csv", "xls", "xlsx"];
      const fileExtension = file.name.split(".").pop().toLowerCase();

      if (!allowedExtensions.includes(fileExtension)) {
        alert("Invalid file format. Please upload CSV or Excel files only.");
        this.value = ""; // Clear the input field to allow reselection
      }
    });
  });
});
