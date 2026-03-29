/*frontend_connected/react_frontend/src/pages/Login.jsx*/
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch('http://localhost:8000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
                credentials: 'include'   // 🔥 THIS LINE
            });


            const data = await res.json();
            if (data.success) {
                // Respects your backend's decision on where the user goes next
                navigate(data.redirect_to);
            } else {
                alert("Invalid Credentials");
            }
        } catch (err) {
            alert("Backend is offline. Please check your FastAPI terminal.");
        }
    };

    return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Ambient Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/10 blur-[120px] rounded-full -z-10"></div>

            <div className="w-full max-w-md bg-slate-900/50 backdrop-blur-xl border border-white/10 p-10 rounded-[2.5rem] shadow-2xl">
                <header className="text-center mb-10">
                    <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/20 group">
                        <span className="text-white font-black italic text-xl">G</span>
                    </div>
                    <h2 className="text-3xl font-black text-white tracking-tight">Welcome Back</h2>
                    <p className="text-slate-400 mt-2 font-medium">Continue your career journey</p>
                </header>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Email Address</label>
                        <input
                            type="email"
                            required
                            className="w-full bg-slate-800/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600"
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Password</label>
                        <input
                            type="password"
                            required
                            className="w-full bg-slate-800/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-white text-black py-4 rounded-2xl font-black text-lg hover:bg-indigo-500 hover:text-white transition-all active:scale-95 shadow-xl shadow-white/5"
                    >
                        Sign In
                    </button>
                </form>

                <footer className="mt-8 text-center border-t border-white/5 pt-8">
                    <p className="text-slate-500 text-sm font-medium">
                        New here?
                        <button onClick={() => navigate('/signup')} className="text-indigo-400 font-bold ml-1 hover:text-indigo-300 transition-colors">
                            Create an account
                        </button>
                    </p>
                </footer>
            </div>
        </div>
    );
};

export default Login;