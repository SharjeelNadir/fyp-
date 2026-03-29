/*frontend_connected/react_frontend/src/pages/Landing.jsx*/
import { useNavigate } from 'react-router-dom';

const Landing = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-[#020617] text-white font-sans selection:bg-indigo-500/30 overflow-x-hidden">

            {/* Background Ambient Glows */}
            <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10">
                <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/20 blur-[140px] rounded-full"></div>
                <div className="absolute bottom-[10%] right-[-5%] w-[500px] h-[500px] bg-blue-500/10 blur-[120px] rounded-full"></div>
            </div>

            {/* Navbar */}
            <nav className="max-w-7xl mx-auto px-8 py-8 flex justify-between items-center bg-transparent">
                <div className="flex items-center gap-2 group cursor-pointer">
                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:rotate-12 transition-transform">
                        <span className="text-xl font-black italic">G</span>
                    </div>
                    <span className="text-2xl font-black tracking-tighter uppercase">Guide<span className="text-indigo-500">Me</span></span>
                </div>

                <div className="flex items-center gap-8">
                    <button
                        onClick={() => navigate('/login')}
                        className="text-sm font-bold text-slate-400 hover:text-white transition-colors"
                    >
                        Login
                    </button>
                    <button
                        onClick={() => navigate('/signup')}
                        className="px-6 py-2.5 rounded-full bg-white text-black text-sm font-black hover:bg-indigo-500 hover:text-white transition-all shadow-lg shadow-white/5"
                    >
                        Get Started
                    </button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="max-w-6xl mx-auto px-8 pt-24 pb-32 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-black uppercase tracking-widest mb-8 animate-fade-in">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                    </span>
                    Powered by Llama 3.1
                </div>

                <h1 className="text-7xl md:text-8xl font-black tracking-tight mb-8 leading-[0.9]">
                    Your Career, <br />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-cyan-400 to-purple-500">
                        AI Optimized.
                    </span>
                </h1>

                <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-12 leading-relaxed font-medium">
                    Upload your resume and let our neural engine map your technical DNA to
                    real-world career paths with precision.
                </p>

                <div className="flex flex-col md:flex-row items-center justify-center gap-6">
                    <button
                        onClick={() => navigate('/signup')}
                        className="group relative px-12 py-5 bg-indigo-600 rounded-2xl font-black text-xl overflow-hidden transition-all hover:bg-indigo-500 hover:scale-105 active:scale-95 shadow-2xl shadow-indigo-500/20"
                    >
                        <span className="relative z-10 flex items-center gap-2">
                            Start Your Journey <span className="group-hover:translate-x-1 transition-transform">→</span>
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                    </button>

                    <button className="px-12 py-5 rounded-2xl border border-slate-800 font-bold text-xl hover:bg-white/5 transition-all text-slate-300">
                        View Demo
                    </button>
                </div>

                {/* Social Proof / Trust Badges */}
                <div className="mt-24 pt-12 border-t border-white/5">
                    <p className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] mb-8">Trusted by students from</p>
                    <div className="flex flex-wrap justify-center gap-12 opacity-30 grayscale hover:grayscale-0 transition-all duration-500">
                        <span className="text-2xl font-black italic">FAST</span>
                        <span className="text-2xl font-black italic">NUST</span>
                        <span className="text-2xl font-black italic">COMSATS</span>
                        <span className="text-2xl font-black italic">GIKI</span>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Landing;