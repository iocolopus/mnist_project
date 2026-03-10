/** @type {HTMLCanvasElement} */
const canvas = document.getElementById('canvas');
const debug_p = document.querySelector("#debug");

let clicked_canvas = false;
let ctx = canvas.getContext("2d");

function config_ctx(){
    ctx.reset();
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineCap = "round";
    ctx.lineWidth = 30;
}

function load_models(){
    fetch("http://localhost:8000/models")
    .then(response => response.json())
    .then(data => {
        const model_select = document.querySelector("#model_select");
        data.forEach(model => {
            const option = document.createElement("option");
            option.value = model;
            option.textContent = model;
            model_select.appendChild(option);
        });
    });
}

load_models()

config_ctx()



// Eventos del canvas

const pencil = document.getElementById('pencil')
const erase = document.getElementById('erase')

canvas.addEventListener("mouseover", (e) => {
    ctx.moveTo(x,y)
    ctx.beginPath()
})

canvas.addEventListener("mouseenter", () => {
    if (pencil.classList.contains("active")){
        ctx.strokeStyle = "black";
        ctx.lineWidth = 30;
    }else {
        ctx.strokeStyle = "white";
        ctx.lineWidth = 60;
    }
})

canvas.addEventListener("mouseleave", (e) => {
    debug_p.textContent = "tranquilito"
})

canvas.addEventListener("mousedown", () => {
    clicked_canvas = true
})

canvas.addEventListener("mouseup", () => {
    clicked_canvas = false
})

canvas.addEventListener("mousemove", (e) => {
    x = e.offsetX
    y = e.offsetY

    if (clicked_canvas) {

        ctx.lineTo(x,y);
        ctx.stroke()
    }


    debug_p.textContent = clicked_canvas
    debug_p.textContent += "\n Cord X: " + x + " Cord Y: " + y;
})



// Eventos botones.

const del_buton = document.querySelector("#clean_button")
const send_button = document.querySelector("#send_button")

del_buton.addEventListener("click", config_ctx)

function plot_results(data){
    probs = data.prediction[0]

    let result_container = document.querySelector('.results_container')
    result_container.innerHTML = ""
    
    
    for (i = 0; i < 10; i++){

        let result = document.createElement("div");
        result.classList.add(["result"]);

        let label = document.createElement("p");
        label.classList.add("label");
        label.textContent = "Digito " + i + ": " + (probs[i]).toFixed(2) + "%";

        result.appendChild(label);

        let bar_container = document.createElement("div")
        bar_container.classList.add("bar_container")
        
        let bar = document.createElement('div')
        bar.classList.add("bar")
        bar.style.width = (probs[i]).toFixed(2) + "%"

        bar_container.appendChild(bar)

        result.appendChild(bar_container)


        result_container.appendChild(result)
    }


}

send_button.addEventListener("click", () => {
    debug_p.textContent = "Enviando a la API..."
    model = document.querySelector("#model_select").value
    
    canvas.toBlob((blob) => {
        const formdata = new FormData();
        formdata.append("model_name", model);
        formdata.append("img", blob, "drawing.png");

        fetch("http://localhost:8000/content", {
            method: "POST",
            body: formdata
    })
    .then(response => response.json())
    .then(data => {
        debug_p.textContent = "Respuesta de la API: " + JSON.stringify(data);
        plot_results(data);
    })

    
})
})


// Eventos herramientas

const tools = document.querySelectorAll(".tool")

tools.forEach((tool) => {
    tool.addEventListener("click", (e) => {
        target = e.currentTarget
        pencil.classList = ['tool']
        erase.classList = ['tool']
        target.classList.add("active")
    })
})
