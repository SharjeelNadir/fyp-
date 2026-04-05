import { useNavigate } from 'react-router-dom';

const Landing = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-[#020617] text-white font-sans selection:bg-indigo-500/30 overflow-x-hidden">

            {/* Ambient background */}
            <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10">
                <div className="absolute top-[-10%] left-[-10%] w-[700px] h-[700px] bg-indigo-600/20 blur-[160px] rounded-full"></div>
                <div className="absolute bottom-[5%] right-[-5%] w-[600px] h-[600px] bg-cyan-500/10 blur-[150px] rounded-full"></div>
            </div>

            {/* Navbar */}
            <nav className="max-w-7xl mx-auto px-8 py-8 flex justify-between items-center backdrop-blur-sm">

                <div className="flex items-center gap-3 cursor-pointer">
                    <div className="w-11 h-11 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-xl shadow-indigo-500/20 transition hover:rotate-12">
                        <span className="text-xl font-black">G</span>
                    </div>

                    <span className="text-2xl font-black tracking-tight">
                        Guide<span className="text-indigo-500">Me</span>
                    </span>
                </div>

                <div className="flex items-center gap-10">

                    <button
                        onClick={() => navigate('/login')}
                        className="text-sm font-semibold text-slate-400 hover:text-white transition"
                    >
                        Login
                    </button>

                    <button
                        onClick={() => navigate('/signup')}
                        className="px-7 py-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 text-sm font-bold hover:scale-105 transition shadow-lg shadow-indigo-500/20"
                    >
                        Get Started
                    </button>

                </div>
            </nav>

            {/* Hero */}
            <main className="max-w-6xl mx-auto px-8 pt-24 pb-24 text-center">

                {/* AI Badge */}
                <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-widest mb-10">

                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                    </span>

                    AI Career Intelligence Engine

                </div>

                {/* Heading */}
                <h1 className="text-6xl md:text-8xl font-black tracking-tight mb-10 leading-[0.95]">

                    Your Career <br />

                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-cyan-400 to-purple-500">
                        Reimagined with AI
                    </span>

                </h1>

                {/* Description */}
                <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-14 leading-relaxed">

                    GuideMe analyzes your resume, verifies your skills, evaluates your personality,
                    and maps you to the most suitable tech careers using intelligent assessment.

                </p>

                {/* CTA */}
                <div className="flex flex-col md:flex-row items-center justify-center gap-6">

                    <button
                        onClick={() => navigate('/signup')}
                        className="group relative px-14 py-5 bg-indigo-600 rounded-2xl font-bold text-xl overflow-hidden transition hover:scale-105 active:scale-95 shadow-2xl shadow-indigo-500/30"
                    >

                        <span className="relative z-10 flex items-center gap-3">

                            Start Assessment →

                        </span>

                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition duration-700"></div>

                    </button>

                    <button className="px-14 py-5 rounded-2xl border border-slate-800 font-semibold text-xl hover:bg-white/5 transition text-slate-300">

                        How it Works

                    </button>

                </div>

                {/* Feature cards */}
                <div className="grid md:grid-cols-3 gap-8 mt-28">

                    <div className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur hover:bg-white/10 transition">

                        <h3 className="font-bold text-lg mb-3">
                            Resume Intelligence
                        </h3>

                        <p className="text-slate-400 text-sm">
                            Extracts technical skills automatically using NLP analysis.
                        </p>

                    </div>

                    <div className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur hover:bg-white/10 transition">

                        <h3 className="font-bold text-lg mb-3">
                            Skill Verification
                        </h3>

                        <p className="text-slate-400 text-sm">
                            AI generated quizzes validate your actual knowledge level.
                        </p>

                    </div>

                    <div className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur hover:bg-white/10 transition">

                        <h3 className="font-bold text-lg mb-3">
                            Career Matching
                        </h3>

                        <p className="text-slate-400 text-sm">
                            Hybrid AI scoring recommends the best career paths.
                        </p>

                    </div>

                </div>

                {/* Trust */}
                <div className="mt-28 pt-12 border-t border-white/5">

                    <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.3em] mb-8">

                        Built for students from

                    </p>

                    <div className="flex flex-wrap justify-center gap-14 opacity-40 grayscale hover:grayscale-0 transition">

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