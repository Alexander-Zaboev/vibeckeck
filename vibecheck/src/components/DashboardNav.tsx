import { Link, useNavigate } from "react-router-dom";
import { clearProfile } from "@/lib/api";

interface DashboardNavProps {
  username?: string;
}

export default function DashboardNav({ username = "guest" }: DashboardNavProps) {
  const navigate = useNavigate();
  const logout = () => {
    clearProfile();
    navigate("/");
  };

  return (
    <nav className="glass-nav fixed top-6 left-1/2 -translate-x-1/2 px-6 py-3 text-sm flex items-center gap-6 z-20">
      <Link to="/" className="font-heading text-gradient-sunset text-lg">
        VibeCheck
      </Link>
      <div className="flex items-center gap-4 text-muted-foreground">
        <span>{username}</span>
        <button onClick={logout} className="text-primary font-medium">
          Logout
        </button>
      </div>
    </nav>
  );
}
