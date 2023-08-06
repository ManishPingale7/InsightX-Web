const row = document.querySelectorAll(".row");
const optionBtn = document.querySelectorAll(".options-btn");

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length) === name) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

optionBtn.forEach((e) => {
  e.addEventListener("click", () => {
    id = e.id.split("_")[2];
    $.ajax({
      url: "/delete-record/" + id,
      type: "DELETE",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (response) {
        if (response == "true") window.location.reload();
        else if (response == "false") alert("Failed to delete a record");
      },
      error: function (xhr, status, error) {
        alert("Failed to delete a record");
      },
    });
  });
});

// row.forEach((e) => {
//   e.addEventListener("click", () => {
//     id = e.firstElementChild.id.split("_")[1];
//     window.open(location.origin + "/dashboard/" + id, "_self");
//   });
// });

function sortTable(n) {
  var table,
    rows,
    switching,
    i,
    x,
    y,
    shouldSwitch,
    dir,
    switchcount = 0;
  table = document.getElementById("myTable");
  switching = true;
  dir = "asc";
  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < rows.length - 1; i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      console.log(`I is: ${i} x is ${x.innerHTML} and y is ${y.innerHTML}\n`);
      if (
        dir == "asc" &&
        x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()
      ) {
        shouldSwitch = true;
        break;
      } else if (
        dir == "desc" &&
        x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()
      ) {
        shouldSwitch = true;
        break;
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function searchTable() {
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("search");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[1];
    td1 = tr[i].getElementsByTagName("td")[2];
    td2 = tr[i].getElementsByTagName("td")[3];
    if (td) {
      txtValue = td.textContent || td.innerText;
      txtValue1 = td1.textContent || td1.innerText;
      txtValue2 = td2.textContent || td2.innerText;
      if (
        txtValue.toUpperCase().indexOf(filter) > -1 ||
        txtValue1.toUpperCase().indexOf(filter) > -1 ||
        txtValue2.toUpperCase().indexOf(filter) > -1
      ) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}
