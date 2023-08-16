// Function to check if the page is refreshed
function isPageRefreshed() {
  return performance.navigation.type === 1;
}

// Redirect to the home page if the page is refreshed
if (isPageRefreshed()) {
  window.location.href = "/"; // Replace "/" with the URL of your home page
}
