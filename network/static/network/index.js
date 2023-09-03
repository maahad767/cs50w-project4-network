function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function submitData(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const csrftoken = getCookie("csrftoken");
  const resp = await fetch("posts/create", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: formData,
  });
  const post = await resp.json();

  addPostToDOM(post);
  form.reset();
}

function addPostToDOM(post) {
  const postContainer = document.querySelector("#posts");
  const newPostNode = document.createElement("div");
  newPostNode.className = "p-3 m-2 card rounded";
  newPostNode.dataset.postId = post.id;
  newPostNode.innerHTML = `
      <h5>
        <a href="profile/${post.author.username}">${post.author.username}</a>
      </h5>
      <p class="mb-0">
        <a class="edit">Edit</a>
      </p>
      <p class="mb-0 content">${post.content}</p>
      <p class="mb-0">${post.created_at}</p>
      <p class="mb-0" data-is-liked="${post.is_liked}">
        <button class="text-danger btn btn-bg-none outline-0 p-0 w-0">
          &hearts;
        </button>
        ${post.likes}
      </p>
      <p class="mb-0">Comments</p>
  `;
  postContainer.prepend(newPostNode);
}

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM Loaded");
  const form = document.querySelector("form");
  if (form) {
    form.onsubmit = submitData;
  }
});

document.onclick = (event) => {
  const target = event.target;
  if (target.className === "edit") {
    handleEditPost(event);
  }
  if (target.className.includes("like")) {
    if (target.parentNode.dataset.isLiked === "true") {
      handleUnlikePost(event);
    } else {
      handleLikePost(event);
    }
  }
};

function handleEditPost(event) {
  event.preventDefault();
  const postId = target.closest("div").dataset.postId;
  const postElement = target.closest("div");
  const content = postElement.querySelector(".content");
  const textarea = document.createElement("textarea");
  const button = document.createElement("button");

  postElement.innerHTML = "";
  textarea.className = "form-control mb-3";
  textarea.name = "content";
  textarea.value = content.innerText;
  button.className = "btn btn-primary px-3 w-auto";
  button.innerText = "Save";

  postElement.appendChild(textarea);
  postElement.appendChild(button);

  button.onclick = async function (e) {
    e.preventDefault();
    const csrftoken = getCookie("csrftoken");
    const updatedContent = textarea.value.trim();

    const resp = await fetch(`posts/${postId}/edit`, {
      method: "PUT",
      headers: { "X-CSRFToken": csrftoken },
      mode: "same-origin",
      body: JSON.stringify({
        content: updatedContent,
      }),
    });
    const post = await resp.json();
    postElement.innerHTML = `
        <h5>
          <a href="profile/${post.author.username}">${post.author.username}</a>
        </h5>
        <p class="mb-0">
          <a href="" class="edit">Edit</a>
        </p>
        <p class="mb-0 content">${post.content}</p>
        <p class="mb-0">${post.created_at}</p>
        <p class="mb-0" data-is-liked="${post.is_liked}">
          <button class="text-danger btn btn-bg-none outline-0 p-0 w-0">
            &hearts;
          </button>
          ${post.likes}
        </p>
        <p class="mb-0">Comments</p>   
      `;
  };
}

async function handleLikePost(event) {
  event.preventDefault();
  const postId = event.target.closest("div").dataset.postId;
  const csrftoken = getCookie("csrftoken");
  const res = await fetch(`posts/${postId}/like`, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
  });
  const like = await res.json();
  const likeCount = like.like_count;
  event.target.parentNode.dataset.isLiked = "true";
  event.target.parentNode.innerHTML = `
        <button class="text-danger btn btn-bg-none outline-0 p-0 w-0 like">
          &hearts;
        </button>
        ${likeCount}
  `;
}

async function handleUnlikePost(event) {
  event.preventDefault();
  const postId = event.target.closest("div").dataset.postId;
  const csrftoken = getCookie("csrftoken");
  const res = await fetch(`posts/${postId}/unlike`, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
  });
  const like = await res.json();
  const likeCount = like.like_count;
  event.target.parentNode.dataset.isLiked = "false";
  event.target.parentNode.innerHTML = `
        <button class="text-secondary btn btn-bg-none outline-0 p-0 w-0 like">
          &hearts;
        </button>
        ${likeCount}
  `;
}
