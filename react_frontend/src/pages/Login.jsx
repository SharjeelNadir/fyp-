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

                credentials: 'include'

            });

            const data = await res.json();

            if (data.success) {

                navigate(data.redirect_to);

            } else {

                alert("Invalid Credentials");

            }

        } catch {

            alert("Backend is offline. Please check FastAPI.");

        }

    };

    return (

        <div className="min-h-screen bg-[#020617] flex items-center justify-center px-6 relative overflow-hidden">

            {/* Background glows */}
            <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/20 blur-[160px] rounded-full"></div>

            <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 blur-[150px] rounded-full"></div>


            {/* Main container */}
            <div className="w-full max-w-5xl grid md:grid-cols-2 bg-slate-900/40 backdrop-blur-xl border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden">

                {/* Left AI panel */}
                <div className="hidden md:flex flex-col justify-center p-14 border-r border-white/10">

                    <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mb-8 shadow-xl shadow-indigo-500/20">

                        <span className="font-black text-2xl">G</span>

                    </div>

                    <h1 className="text-4xl font-black leading-tight mb-6">

                        Continue Your <br />

                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">

                            AI Career Journey

                        </span>

                    </h1>

                    <p className="text-slate-400 leading-relaxed">

                        Resume analysis.
                        Skill verification.
                        Career intelligence.

                    </p>

                    <div className="mt-10 space-y-4 text-sm text-slate-500">

                        <p>✓ AI powered career mapping</p>

                        <p>✓ Technical skill validation</p>

                        <p>✓ Personality career matching</p>

                    </div>

                </div>


                {/* Right form */}
                <div className="p-12">

                    <div className="text-center mb-10">

                        <h2 className="text-3xl font-black mb-2">

                            Welcome Back

                        </h2>

                        <p className="text-slate-400">

                            Sign in to continue

                        </p>

                    </div>


                    <form
                        onSubmit={handleLogin}
                        className="space-y-6"
                    >

                        <div>

                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">

                                Email

                            </label>

                            <input

                                type="email"

                                required

                                className="w-full bg-slate-800/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/60 transition placeholder:text-slate-600"

                                placeholder="name@example.com"

                                value={email}

                                onChange={(e) => setEmail(e.target.value)}

                            />

                        </div>


                        <div>

                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">

                                Password

                            </label>

                            <input

                                type="password"

                                required

                                className="w-full bg-slate-800/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/60 transition placeholder:text-slate-600"

                                placeholder="••••••••"

                                value={password}

                                onChange={(e) => setPassword(e.target.value)}

                            />

                        </div>


                        <button

                            type="submit"

                            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 py-4 rounded-2xl font-bold text-lg hover:scale-[1.02] active:scale-95 transition shadow-xl shadow-indigo-500/30"

                        >

                            Sign In

                        </button>

                    </form>


                    <div className="mt-10 text-center border-t border-white/5 pt-8">

                        <p className="text-slate-500 text-sm">

                            New here?

                            <button

                                onClick={() => navigate('/signup')}

                                className="text-indigo-400 font-bold ml-2 hover:text-indigo-300 transition"

                            >

                                Create account

                            </button>

                        </p>

                    </div>


                    {/* Back link */}
                    <div className="mt-6 text-center">

                        <button

                            onClick={() => navigate('/')}

                            className="text-xs text-slate-600 hover:text-slate-400 transition"

                        >

                            ← Back to Home

                        </button>

                    </div>

                </div>

            </div>

        </div>

    );

};

export default Login;