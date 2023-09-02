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

async function submitData() {
  const csrftoken = getCookie("csrftoken");
  const res = await fetch("posts/create", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify({ content: postContent }),
  });
}

async function fetchData() {
  const resp = await fetch("posts/all");
  const postsResp = await resp.json();
}
