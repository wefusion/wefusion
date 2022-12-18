
function infScrollStateHolder() {
    let x = 0;

    const batch_size = 50;
    return () => {
        console.log(1)
        if (window.scrollY + window.innerHeight >= document.body.offsetHeight * 0.9) {
            for (let i = 0; i < batch_size; i++) {
                addImg(x, randomId());
                x = (x + 1) % 10;
            }
        }

    };
}

function randomId() {
    return Math.random().toString(36).substr(2, 9);
}

function addImg(x, id) {
    let container = document.getElementById("masonry");
    let item = document.createElement("div");

    item.className = "item";
    item.id = id;

    item.onclick = function (event) {
        let div_id = undefined;

        switch (event.target.tagName) {
            case "DIV":
                div_id = event.target.id;
                break;
            case "IMG":
                div_id = event.target.parentElement.id;
                break;
            default:
                break;
        }

        createPopup(x);

    };

    let img = document.createElement("img");
    img.src = `images/${x}.webp`;

    item.appendChild(img);
    container.appendChild(item);

}

function createPopup(id) {
    let block = document.createElement("div");
    block.className = "popup";
    block.id = `popup-${id}`;

    block.onclick = function (event) {
        if (event.target.tagName === "DIV") {
            event.target.remove();

            document.body.style.overflow = "auto";
        }
    };

    let popup_inner = document.createElement("div");
    popup_inner.className = "popup-inner";

    let img = document.createElement("img");
    img.alt = id;
    img.src = `images/${id}.webp`

    popup_inner.appendChild(img);
    block.appendChild(popup_inner);


    document.body.appendChild(block);

    document.body.style.overflow = "hidden";
    return block;

}

document.addEventListener('onDOMCreate', infScrollStateHolder());
document.addEventListener('scroll', infScrollStateHolder());
