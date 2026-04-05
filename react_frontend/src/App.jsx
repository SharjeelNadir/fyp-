//frontend_connected/react_frontend/src/App.jsx
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useEffect } from 'react';

// Page Imports
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import Personality from './pages/Personality';
import Quiz from './pages/Quiz';
import Profile from './pages/Profile';
import ResumeOptimizer from './pages/ResumeOptimizer';

// Helper: Makes sure every page starts at the top when you navigate
const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

function App() {
  return (
    <Router>
      <ScrollToTop />
      {/* Changed bg-slate-50 to bg-[#020617] (Dark Navy) 
          This ensures no white flickering occurs between page transitions 
      */}
      <div className="min-h-screen bg-[#020617] selection:bg-indigo-500/30">
        <Routes>
          {/* Public Landing Page */}
          <Route path="/" element={<Landing />} />

          {/* Authentication */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Assessment Flow */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/resume-upload" element={<ResumeUpload />} />
          <Route path="/personality" element={<Personality />} />
          <Route path="/quiz" element={<Quiz />} />

          {/* Final Results, Career Chatbot & Resume Optimizer */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/resume-optimizer" element={<ResumeOptimizer />} />

          {/* Fallback: Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;