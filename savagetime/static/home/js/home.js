// init not found message
let text = document.createTextNode("Keyword not found");
let td = document.createElement("td");
td.appendChild(text);
message = document.createElement("tr");
message.appendChild(td);
message.style.display = "none";
document.getElementsByTagName("tbody")[0].appendChild(message);

let input = document.getElementById("table-filter");
key_listener = (e)=> {
    let table = document.getElementById("main-table");
    let a_tag = table.querySelectorAll(".table-body tr td a");
    let keyword = e.target.value;

    // iterate all series name
    let counter = 0;
    for (i = 0; i < a_tag.length; i ++){
        s_result = a_tag[i].textContent.indexOf(keyword);
        if (s_result > -1){
            a_tag[i].closest("tr").style.display = "";
            message.style.display = "none";
        } else {
            counter += 1;
            a_tag[i].closest("tr").style.display = "none";
        }
    }

    if (counter == a_tag.length) {
        // if loop set every display to none, it means no keyword match
        message.style.display = "";
    }
}
input.oninput = key_listener;