
function getInfiniteImageIterator(batch_size) {
    const url = "/api/search/infinity";

    let skip = 0;
    let limit = batch_size;

    let seed = undefined;

    async function getImages() {
        result = await fetch(url, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: JSON.stringify(
                { "seed": seed, "skip": skip, "limit": limit }
            )
        })

        return result.json()

    }


    return async function () {
        if (skip == undefined) {
            return []
        }

        let result = await getImages();

        seed = result.seed;
        skip = result.cursor;

        return result.artifacts;
    }
}

function getPromptImageIterator(prompt, batch_size) {
    const url = "/api/search/prompt";

    let skip = 0;
    let limit = batch_size;


    async function getImages() {
        result = await fetch(url, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            },
            redirect: 'follow',
            referrerPolicy: 'no-referrer',
            body: JSON.stringify(
                { "prompt": prompt, "skip": skip, "limit": limit }
            )
        })

        return result.json()

    }

    return async function () {
        if (skip == undefined) {
            return []
        }

        let result = await getImages();
        skip = result.cursor;

        return result.artifacts;
    }
}


function createPopup(image) {
    let block = document.createElement("div");
    block.className = "popup";
    block.id = `popup-${image.id}`;

    block.onclick = function (event) {
        if (event.target.tagName === "DIV" && event.target.className === "popup") {
            event.target.remove();

            document.body.style.overflow = "auto";
        }
    };


    let popup_inner = document.createElement("div");
    popup_inner.className = "popup-inner";

    // left side
    let left_inner = document.createElement("div");
    left_inner.className = "left-inner";
    let prompt = document.createElement("p");
    prompt.className = "prompt";
    prompt.textContent = image.payload.prompt;
    let promptbox = document.createElement("div");
    promptbox.className = "prompt-box";
    promptbox.appendChild(prompt);

    // comments container
    let comments_container = document.createElement("div");
    comments_container.className = "comments-container";
    comments_container.style.display = "none";


    // buttons
    let copy_prompt_btn = document.createElement("button");
    copy_prompt_btn.textContent = "Copy";
    copy_prompt_btn.className = "copy-button margin-right";
    copy_prompt_btn.onclick = function (event) {
        let text = prompt.textContent;
        navigator.clipboard.writeText(text);
    };

    let like_btn = document.createElement("button");
    like_btn.textContent = "Like";
    like_btn.className = "like-button margin-right";
    like_btn.onclick = function (event) {
        let like_btn = event.target;
        if (like_btn.textContent === "Like") {
            like_btn.textContent = "Liked";
        } else {
            like_btn.textContent = "Like";
        }
    };

    let comments_btn = document.createElement("button");
    comments_btn.textContent = "Comments";
    comments_btn.className = "comments-button";
    comments_btn.onclick = function (event) {

        let comments_btn = event.target;

        if (comments_container.style.display === "none") {
            comments_container.style.display = "block";
            comments_btn.textContent = "Image";
            // hide right side
            right_inner.style.display = "none";
        } else {
            comments_container.style.display = "none";
            comments_btn.textContent = "Comments";

            // show right side
            right_inner.style.display = "block";
        }

    };


    // comments bar
    let comment_input = document.createElement("input");
    comment_input.className = "comment-input";
    comment_input.placeholder = "Write a comment...";
    let comment_send_btn = document.createElement("button");
    comment_send_btn.className = "comment-send-btn";
    comment_send_btn.textContent = "Send";
    let comments_bar = document.createElement("div");
    comments_bar.className = "comments-bar";
    let comments_bar_anchor = document.createElement("div");
    comments_bar_anchor.className = "comments-bar-anchor";

    comments_bar.appendChild(comments_bar_anchor);
    comment_send_btn.onclick = function (event) {
        let user_text = "User";
        let date_text = new Date().toLocaleString();

        let comment_text = comment_input.value;
        if (comment_text === "") {
            return;
        }

        let comment = document.createElement("textarea");
        comment.setAttribute("readonly", "");
        comment.className = "comment";
        comment.value = `User: ${user_text}\nDate: ${date_text}\nComment: ${comment_text}`;


        // comments_bar.appendChild(comment);
        comments_bar.insertBefore(comment, comments_bar_anchor);
        comment_input.value = "";

    };


    comments_container.appendChild(comment_input);
    comments_container.appendChild(comment_send_btn);
    comments_container.appendChild(comments_bar);


    // buttons container
    let btn_container = document.createElement("div");
    btn_container.className = "btn-container";
    btn_container.appendChild(copy_prompt_btn);
    btn_container.appendChild(like_btn);
    btn_container.appendChild(comments_btn);


    // model info
    let model_type_prompt = document.createElement("p");
    model_type_prompt.textContent = "Model type: ";
    model_type_prompt.className = "model-info-prompt";
    let model_type = document.createElement("span");
    model_type.className = "model-ingredient";
    model_type.textContent = "Stable Diffusion 1.4";
    model_type_prompt.appendChild(model_type);

    let img_size_prompt = document.createElement("p");
    img_size_prompt.textContent = "Image size: ";
    img_size_prompt.className = "model-info-prompt";
    let img_size = document.createElement("span");
    img_size.className = "model-ingredient";
    img_size.textContent = `${image.payload.height}x${image.payload.width}`;
    img_size_prompt.appendChild(img_size);

    let seed_prompt = document.createElement("p");
    seed_prompt.textContent = "Seed: ";
    seed_prompt.className = "model-info-prompt";
    let seed = document.createElement("span");
    seed.className = "model-ingredient";
    seed.textContent = image.payload.seed;
    seed_prompt.appendChild(seed);

    let guidance_prompt = document.createElement("p");
    guidance_prompt.textContent = "Guidance scale: ";
    guidance_prompt.className = "model-info-prompt";
    let guidance = document.createElement("span");
    guidance.className = "model-ingredient";
    guidance.textContent = image.payload.guidance_scale;
    guidance_prompt.appendChild(guidance);



    // append to left inner
    left_inner.appendChild(promptbox);
    left_inner.appendChild(btn_container);
    left_inner.appendChild(model_type_prompt);
    left_inner.appendChild(img_size_prompt);
    left_inner.appendChild(seed_prompt);
    left_inner.appendChild(guidance_prompt);
    popup_inner.appendChild(left_inner);

    // right side
    let right_inner = document.createElement("div");
    right_inner.className = "right-inner";

    let img = document.createElement("img");
    img.className = "popup-img";
    img.alt = image.id;
    img.src = `/images/${image.filename}`

    right_inner.appendChild(img);
    popup_inner.appendChild(right_inner);
    popup_inner.appendChild(comments_container);

    block.appendChild(popup_inner);


    document.body.appendChild(block);

    //block scroll
    document.body.style.overflow = "hidden";

    return block;

}

function addImg(image) {
    let container = document.getElementById("masonry");
    let item = document.createElement("div");

    item.className = "item";
    item.id = image.id;

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
        createPopup(image);
    };

    let img = document.createElement("img");
    img.src = `/images/${image.filename}`;


    item.appendChild(img);
    container.appendChild(item);


}

function infinityScrollStateHolder() {
    const batch_size = 10;
    const image_iterator = getInfiniteImageIterator(batch_size);

    let loading = false;

    return async () => {
        if (window.scrollY + window.innerHeight >= document.body.offsetHeight * 0.9) {
            if (!loading) {
                loading = true;

                images = await image_iterator();
                images.forEach(img => {
                    addImg(img)
                });

                loading = false;
            }
        }
    };
}

function promptScrollStateHolder(prompt) {
    const batch_size = 10;
    const image_iterator = getPromptImageIterator(prompt, batch_size);

    let loading = false;

    return async () => {
        if (window.scrollY + window.innerHeight >= document.body.offsetHeight * 0.9) {
            if (!loading) {
                loading = true;

                images = await image_iterator();
                images.forEach(img => {
                    addImg(img)
                });

                loading = false;
            }
        }
    };

}

function index() {

    const scrollState = infinityScrollStateHolder();

    window.onload = function () {
        scrollState();
    };

    document.addEventListener('scroll', scrollState);
}

function find() {
    document.getElementById("find-btn").onclick = function () {
        let prompt = document.getElementById("prompt").value;

        let container = document.getElementById("masonry");
        container.innerHTML = "";

        const scrollState = promptScrollStateHolder(prompt);

        document.addEventListener('scroll', scrollState);

        scrollState()
    }
}
