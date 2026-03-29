import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

const Profile = () => {
    const [stats, setStats] = useState(null);

    // ==============================
    // Career Recommendation State
    // ==============================
    const [careers, setCareers] = useState([]);
    const [loadingCareers, setLoadingCareers] = useState(false);
    const [alreadyGenerated, setAlreadyGenerated] = useState(false);

    // ==============================
    // AI Counselor State
    // ==============================
    const [showChat, setShowChat] = useState(false);
    const [chat, setChat] = useState([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const chatRef = useRef(null);

    // ==============================
    // Fetch User Stats
    // ==============================
    useEffect(() => {
        fetch('http://localhost:8000/api/user-stats', { credentials: 'include' })
            .then(res => res.json())
            .then(data => setStats(data))
            .catch(err => console.error("Stats fetch error:", err));
    }, []);

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [chat, isTyping]);


    useEffect(() => {
        const autoFetch = async () => {
            try {
                const res = await fetch(
                    'http://localhost:8000/api/recommend-careers',
                    { credentials: 'include' }
                );
                const data = await res.json();

                if (data.recommendations && data.recommendations.length > 0) {
                    setCareers(data.recommendations);
                    setAlreadyGenerated(true);
                }
            } catch (err) {
                console.error("Auto career fetch error:", err);
            }
        };

        autoFetch();
    }, []);

    // ==============================
    // Fetch Career Recommendations
    // ==============================
    const fetchCareers = async () => {
        if (alreadyGenerated) return;

        setLoadingCareers(true);
        try {
            const res = await fetch(
                'http://localhost:8000/api/recommend-careers',
                { credentials: 'include' }
            );
            const data = await res.json();

            if (data.recommendations) {
                setCareers(data.recommendations);
                setAlreadyGenerated(true);
            }
        } catch (err) {
            console.error("Career fetch error:", err);
        } finally {
            setLoadingCareers(false);
        }
    };


    // ==============================
    // AI Counselor Handler
    // ==============================
    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const msg = input;
        setInput('');
        setChat(prev => [...prev, { role: 'user', text: msg }]);
        setIsTyping(true);

        const formData = new FormData();
        formData.append('message', msg);

        try {
            const res = await fetch(
                'http://localhost:8000/api/counsellor-chat',
                {
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                }
            );
            const data = await res.json();
            setChat(prev => [...prev, { role: 'bot', text: data.reply }]);
        } catch {
            setChat(prev => [...prev, { role: 'bot', text: "AI Counselor unavailable." }]);
        } finally {
            setIsTyping(false);
        }
    };

    // ==============================
    // Loading Screen
    // ==============================
    if (!stats) {
        return (
            <div className="h-screen flex items-center justify-center bg-[#020617] text-white">
                <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    const { master, skill_summary, claimed_skills = [] } = stats;

    // ==============================
    // UI
    // ==============================
    return (
        <div className="min-h-screen bg-[#020617] text-white p-6 md:p-12 relative">

            {/* Background Glow */}
            <div className="fixed inset-0 -z-10">
                <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/10 blur-[100px] rounded-full" />
            </div>

            <div className="max-w-7xl mx-auto space-y-12">

                {/* HEADER */}
                <header>
                    <span className="inline-block px-4 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 
                                     text-indigo-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">
                        Analysis Finalized
                    </span>
                    <h1 className="text-6xl font-black tracking-tighter mb-4">
                        Technical <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-indigo-600">Identity.</span>
                    </h1>
                    <p className="text-slate-400 text-lg max-w-2xl">
                        Your claimed skills and verified technical performance.
                    </p>
                </header>

                {/* PERFORMANCE SECTION */}
                <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-slate-900/40 border border-white/5 p-8 rounded-[2.5rem]">
                        <p className="text-xs font-black text-slate-500 uppercase mb-4">Quiz Accuracy</p>
                        <div className="flex items-baseline gap-3">
                            <span className="text-7xl font-black">{master.total_score}</span>
                            <span className="text-2xl text-slate-600">/ {master.total_questions}</span>
                        </div>
                        <div className="mt-8 w-full h-1.5 bg-slate-800 rounded-full">
                            <div
                                className="h-full bg-indigo-500"
                                style={{
                                    width: `${(master.total_score / master.total_questions) * 100}%`
                                }}
                            />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 p-8 rounded-[2.5rem] shadow-xl">
                        <p className="text-xs font-black uppercase text-white/50 mb-2">Market Standing</p>
                        <h3 className="text-4xl font-black">Career Mapping Ready</h3>
                        <p className="mt-4 text-sm font-bold uppercase text-indigo-100/70">
                            Deterministic Recommendation Engine
                        </p>
                    </div>
                </div>

                {/* CLAIMED SKILLS */}
                {claimed_skills.length > 0 && (
                    <div className="bg-slate-900/20 border border-white/5 p-10 rounded-[2.5rem]">
                        <h4 className="text-sm font-black uppercase tracking-[0.2em] text-slate-500 mb-8">
                            Claimed Skills
                        </h4>
                        <div className="flex flex-wrap gap-4">
                            {claimed_skills.map(skill => (
                                <div
                                    key={skill}
                                    className="px-5 py-3 rounded-2xl bg-slate-800/40 border border-white/5
                                               text-slate-300 text-[11px] font-black uppercase"
                                >
                                    {skill}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* VERIFIED SKILLS */}
                <div className="bg-slate-900/20 border border-white/5 p-10 rounded-[2.5rem]">
                    <h4 className="text-sm font-black uppercase tracking-[0.2em] text-slate-500 mb-8">
                        Verified Technical Skills
                    </h4>

                    <div className="flex flex-wrap gap-4">
                        {Object.entries(skill_summary).map(([skill, data]) => {
                            const strong = data.accuracy >= 60;
                            return (
                                <div
                                    key={skill}
                                    className={`flex items-center gap-3 px-5 py-3 rounded-2xl border
                                        ${strong
                                            ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300'
                                            : 'bg-slate-800/40 border-white/5 text-slate-400 opacity-70'
                                        }`}
                                >
                                    <span className={`w-2 h-2 rounded-full ${strong ? 'bg-indigo-400 animate-pulse' : 'bg-slate-600'}`} />
                                    <span className="text-[11px] font-black uppercase">{skill}</span>
                                    <span className="text-[10px] font-bold text-slate-400">
                                        {data.correct}/{data.total} ({data.accuracy}%)
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* CAREER RECOMMENDATIONS */}
                <div className="bg-slate-900/20 border border-white/5 p-10 rounded-[2.5rem]">
                    <div className="flex justify-between items-center mb-8">
                        <h4 className="text-sm font-black uppercase tracking-[0.2em] text-slate-500">
                            Career Recommendations
                        </h4>

                        <button
                            onClick={fetchCareers}
                            disabled={loadingCareers || alreadyGenerated}
                            className={`px-5 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition
        ${alreadyGenerated
                                    ? "bg-emerald-600 cursor-not-allowed"
                                    : "bg-indigo-600 hover:bg-indigo-500"
                                }`}
                        >
                            {loadingCareers
                                ? "Analyzing..."
                                : alreadyGenerated
                                    ? "Generated ✓"
                                    : "Generate"}
                        </button>

                    </div>

                    {careers.length === 0 && !loadingCareers && (
                        <p className="text-slate-500 text-sm">
                            Click Generate to analyze your profile.
                        </p>
                    )}

                    <div className="space-y-6">
                        {careers.map((career, idx) => (
                            <div key={idx} className="bg-slate-900/40 border border-white/5 p-6 rounded-2xl">
                                <h3 className="text-xl font-black mb-2">
                                    {idx + 1}. {career.title}
                                </h3>

                                <div className="text-4xl font-black text-indigo-400 mb-4">
                                    {career.final_score}%
                                </div>

                                <div className="text-sm text-slate-400 space-y-1">
                                    <p>Technical Match: {career.technical_fit}%</p>
                                    <p>Personality Match: {career.personality_fit}%</p>
                                    <p>Claimed Skills Match: {career.claimed_alignment}%</p>
                                </div>
                            </div>
                        ))}

                    </div>
                </div>
            </div>
            {/* ==============================
   FLOATING AI BUTTON
================================ */}
            {!showChat && (
                <button
                    onClick={() => setShowChat(true)}
                    className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-4 
                   bg-indigo-600 rounded-2xl shadow-2xl hover:bg-indigo-500 transition-all"
                >
                    🤖
                    <div className="text-left">
                        <p className="text-xs font-black uppercase tracking-widest opacity-80">
                            AI Counselor
                        </p>
                        <p className="text-sm">Let’s plan your career →</p>
                    </div>
                </button>
            )}

            {/* ==============================
   CHAT DRAWER
================================ */}
            {showChat && (
                <div className="fixed inset-0 z-50 bg-black/40 flex justify-end">
                    <div className="w-full max-w-md h-full bg-[#020617] border-l border-white/10 flex flex-col">

                        {/* Header */}
                        <div className="p-6 border-b border-white/10 flex justify-between items-center">
                            <div>
                                <h3 className="font-black">AI Career Counselor</h3>
                                <p className="text-[10px] uppercase text-slate-400">
                                    Llama Active
                                </p>
                            </div>
                            <button onClick={() => setShowChat(false)} className="text-xl">
                                ✕
                            </button>
                        </div>

                        {/* Messages */}
                        <div
                            ref={chatRef}
                            className="flex-1 overflow-y-auto p-6 space-y-5"
                        >
                            {chat.length === 0 && (
                                <div className="text-slate-400 text-sm">
                                    👋 Ask me about your strengths, gaps, or roadmap.
                                </div>
                            )}

                            {chat.map((msg, i) => (
                                <div
                                    key={i}
                                    className={`flex ${msg.role === 'user'
                                        ? 'justify-end'
                                        : 'justify-start'
                                        }`}
                                >
                                    <div
                                        className={`max-w-[85%] p-4 rounded-2xl text-sm
                                ${msg.role === 'user'
                                                ? 'bg-indigo-600 text-white'
                                                : 'bg-slate-800 text-slate-200 border border-white/5'
                                            }`}
                                    >
                                        {msg.role === 'bot'
                                            ? <ReactMarkdown>{msg.text}</ReactMarkdown>
                                            : msg.text}
                                    </div>
                                </div>
                            ))}

                            {isTyping && (
                                <div className="text-slate-500 text-sm">
                                    AI is thinking…
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <form onSubmit={sendMessage} className="p-4 border-t border-white/10">
                            <input
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                placeholder="Ask about your career roadmap…"
                                className="w-full bg-slate-800 text-white p-4 rounded-xl outline-none"
                            />
                        </form>
                    </div>
                </div>
            )}

        </div>
    );
};

export default Profile;
