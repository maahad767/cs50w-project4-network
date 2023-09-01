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

function CreatePost(props) {
  const { posts, setPosts } = props;
  const [postContent, setPostContent] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const csrftoken = getCookie("csrftoken");

  const handleSubmit = (e) => {
    e.preventDefault();
    async function submitData() {
      const res = await fetch("posts/create", {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        mode: "same-origin",
        body: JSON.stringify({ content: postContent }),
      });
      const post = await res.json();
      console.log(post);
      setPosts([post, ...posts]);
    }
    setIsSubmitting(true);
    submitData();
    setPostContent("");
    setIsSubmitting(false);
  };

  return (
    <div className="p-3 m-2 card rounded">
      <form onSubmit={handleSubmit}>
        <h2>New Post</h2>
        <textarea
          className="form-control mb-3"
          onChange={(e) => setPostContent(e.target.value)}
          value={postContent}
        ></textarea>
        <button className="btn btn-primary" disabled={isSubmitting}>
          Post
        </button>
      </form>
    </div>
  );
}

function AllPostList() {
  const [posts, setPosts] = React.useState([]);
  return (
    <>
      <h1>All Posts</h1>
      <CreatePost posts={posts} setPosts={setPosts} />
      <PostList posts={posts} setPosts={setPosts} />
    </>
  );
}

function PostList(props) {
  const { posts, setPosts } = props;
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    async function fetchData() {
      const resp = await fetch("posts/all");
      const postsResp = await resp.json();
      setPosts(postsResp.data);
      setIsLoading(false);
    }
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="spinner-border" role="status">
        <span className="sr-only">Loading...</span>
      </div>
    );
  }
  console.log(posts);
  return (
    <div>
      {posts.map((post) => {
        return <Post {...post} key={post.id} />;
      })}
    </div>
  );
}

function Post(props) {
  const { author, content, created_at, likes } = props;

  return (
    <div className="p-3 m-2 card rounded">
      <h5>{author.username}</h5>
      <p className="mb-0">
        <a href="">Edit</a>
      </p>
      <p className="mb-0">{content}</p>
      <p className="mb-0">{created_at}</p>
      <p className="mb-0">
        <button className="text-danger btn btn-bg-none outline-0 p-0 w-0">
          &hearts;
        </button>
        {likes}
      </p>
      <p className="mb-0">Comments</p>
    </div>
  );
}

function MyApp() {
  return (
    <div>
      <AllPostList />
    </div>
  );
}

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);
root.render(<MyApp />);
