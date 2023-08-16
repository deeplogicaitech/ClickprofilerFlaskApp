$(document).ready(function () {
  var filterToggle = false;
  var filterButton = $("#filterButton");

  $("#filterButton").click(function () {
    filterToggle = !filterToggle;

    if (filterToggle) {
      $(this).removeClass("toggle-inactive").addClass("toggle-active");
      filterButton.find(".outline-icon").hide();
      filterButton.find(".fill-icon").show();
    } else {
      $(this).removeClass("toggle-active").addClass("toggle-inactive");
      filterButton.find(".outline-icon").show();
      filterButton.find(".fill-icon").hide();
    }

    $("#data-table tbody tr").each(function () {
      var thirdColumn = $(this).find("td:nth-child(4)").text().trim();
      var fourthColumn = $(this).find("td:nth-child(5)").text().trim();

      if (filterToggle) {
        if (thirdColumn === "" && fourthColumn === "") {
          $(this).hide();
        } else {
          $(this).show();
        }
      } else {
        $(this).show();
      }
    });
  });
});
