import { Link } from "react-router-dom";

export default function Page404() {
  return (
    <main>
      <div>Page not found. Go back to <Link to="/home">Home</Link> page.</div>
    </main>
  )
}
