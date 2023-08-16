document.addEventListener("DOMContentLoaded", function () {
  // Initialize clipboard.js
  var clipboard = new ClipboardJS("#copyToClipboard", {
    text: function (trigger) {
      var headerCells = document.querySelectorAll("#table-header th");
      var headerData = Array.from(headerCells).map((cell) => cell.innerText);
      var rows = document.querySelectorAll("#data-table tr");
      var data = [];

      // Add header data to the beginning of the data array
      data.push(headerData.join("\t"));

      for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].querySelectorAll("td");
        var rowData = [];
        for (var j = 0; j < cells.length; j++) {
          rowData.push(cells[j].innerText);
        }
        data.push(rowData.join("\t"));
      }

      return data.join("\n");
    },
  });

  var originalIcon = `
                <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-copy" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                <path d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"></path>
                <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"></path>
                </svg>
            `;

  // Change the button color on success
  clipboard.on("success", function (e) {
    e.clearSelection();
    var copyButton = document.getElementById("copyToClipboard");

    // Add a class for the transition effect
    copyButton.classList.add("btn-transition");

    // Update button style and text
    copyButton.classList.remove("btn-secondary");
    copyButton.classList.add("btn-success");
    copyButton.innerHTML = "Copied!";

    // Restore the original icon and style after a delay
    setTimeout(function () {
      copyButton.innerHTML = originalIcon + "Copy to Clipboard";
      copyButton.classList.remove("btn-success");
      copyButton.classList.add("btn-secondary");

      // Remove the transition class
      copyButton.classList.remove("btn-transition");
    }, 1000);
  });

  clipboard.on("error", function (e) {
    e.clearSelection();
    var copyButton = document.getElementById("copyToClipboard");

    // Add a class for the transition effect
    copyButton.classList.add("btn-transition");

    // Update button style and text
    copyButton.classList.remove("btn-secondary");
    copyButton.classList.add("btn-danger");
    copyButton.innerHTML = "Copy Error!";
    setTimeout(function () {
      copyButton.innerHTML = "Copy to Clipboard";
      copyButton.classList.remove("btn-danger");
      copyButton.classList.add("btn-secondary");

      // Remove the transition class
      copyButton.classList.remove("btn-transition");
    }, 1000);
  });
});
