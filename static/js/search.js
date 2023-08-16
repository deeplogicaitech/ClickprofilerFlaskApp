$(document).ready(function () {
  $("#search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#data-table tbody tr").filter(function () {
      // Show all rows if the search box is empty
      if (!value) {
        $(this).show();
        return;
      }
      // Otherwise, toggle row visibility based on the search value
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});
