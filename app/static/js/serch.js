function search() {
  var searchText = document.getElementById("searchInput").value.toLowerCase();
  var elements = document.querySelectorAll("p, h1, h2, h3, h4, strong");

  for (var i = 0; i < elements.length; i++) {
    var element = elements[i];
    var text = element.textContent.toLowerCase();

    if (text.includes(searchText)) {
      element.style.display = "block";
    } else {
      element.style.display = "none";
    }
  }
}

var searchInput = document.getElementById("searchInput");

searchInput.addEventListener("input", search);
