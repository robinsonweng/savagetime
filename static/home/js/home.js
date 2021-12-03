// init not found message
let text = document.createTextNode("Keyword not found");
let para = document.createElement("p");
para.appendChild(text);
let block = document.createElement("div");
block.appendChild(para);
let li = document.createElement("li");
li.appendChild(block);
li.className = "table-row not-found";
li.style.display = "none";
document.getElementById("main-table").appendChild(li);

let input = document.getElementById("table-filter");
key_listener = (e)=> {
    let table = document.getElementById("main-table");
    let row = table.getElementsByClassName("table-row");
    // iterate all series name
    let counter = 0;
    for (i = 0; i < row.length; i ++){
        title_text = row[i].querySelectorAll("div")[0].firstChild.innerText;
        console.log(input.innerText)
        result = title_text.indexOf(input.value)
        if (result > -1){
            row[i].style.display = "";
            li.style.display = "none"
        } else {
            counter += 1;
            row[i].style.display = "none";
        }

    }
    if (counter == row.length) {
        // if loop set every display to none, it means no keyword match
        li.style.display = "";
    }
}
input.oninput = key_listener;