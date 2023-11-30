var showFiltersCheckbox = document.getElementById("showFilters");
var filterInputGroups = document.querySelectorAll(".filter-input-group");

showFiltersCheckbox.addEventListener("click", toggleFilters);

function toggleFilters() {
  for (var i = 0; i < filterInputGroups.length; i++) {
    var filterInputGroup = filterInputGroups[i];
    if (showFiltersCheckbox.checked) {
      filterInputGroup.style.display = "block";
    } else {
      filterInputGroup.style.display = "none";
    }
  }
}