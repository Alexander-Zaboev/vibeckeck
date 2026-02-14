import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import LoginPage from "@/pages/LoginPage";
import WrappedPage from "@/pages/WrappedPage";
import DashboardPage from "@/pages/DashboardPage";
import YouTubeExplorerPage from "@/pages/YouTubeExplorerPage";
import { readProfile } from "@/lib/api";

const RequireVibeData = ({ children }: { children: JSX.Element }) => {
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    const stored = readProfile();
    if (!stored) {
      navigate("/", { replace: true, state: { from: location.pathname } });
    }
  }, [location.pathname, navigate]);
  return children;
};

function App() {
  return (
    <div className="min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))] font-body">
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route
          path="/wrapped"
          element={
            <RequireVibeData>
              <WrappedPage />
            </RequireVibeData>
          }
        />
        <Route
          path="/dashboard"
          element={
            <RequireVibeData>
              <DashboardPage />
            </RequireVibeData>
          }
        />
        <Route path="/youtube-explorer" element={<YouTubeExplorerPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
