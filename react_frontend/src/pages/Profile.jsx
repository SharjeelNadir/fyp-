import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';
import { API } from "../config";

const Profile = () => {
    const [stats, setStats] = useState(null);
const navigate = useNavigate();
const logout = async () => {

try{

await fetch(`${API}/api/logout`,
{
method:"POST",
credentials:"include"
}
);

}catch(e){
console.log("Logout error");
}

navigate('/');

};
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
        fetch(`${API}/api/user-stats`, { credentials: 'include' })
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
                    `${API}/api/recommend-careers`,
                    { credentials: 'include' }
                );
                const data = await res.json();

                if (data.recommendations && data.recommendations.length > 0) {

    setCareers(data.recommendations);

    setAlreadyGenerated(true);

}else{

    setAlreadyGenerated(false);

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
    const fetchCareers = async (refresh=false) => {

    setLoadingCareers(true);

    try {

        const url = refresh
        ? `${API}/api/recommend-careers?refresh=true`
        : `${API}/api/recommend-careers`;

        const res = await fetch(

            url,

            { credentials:'include' }

        );

        const data = await res.json();

        if(data.recommendations){

            setCareers(data.recommendations);

            setAlreadyGenerated(true);

        }

    } catch(err){

        console.error("Career fetch error:",err);

    } finally{

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
                `${API}/api/counsellor-chat`,
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
                <header className="flex justify-between items-start">

<div>

<span className="inline-block px-4 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 
text-indigo-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">

Analysis Finalized

</span>

<h1 className="text-6xl font-black tracking-tighter mb-4">

Technical 

<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-indigo-600">
Identity.
</span>

</h1>

<p className="text-slate-400 text-lg max-w-2xl">

Your claimed skills and verified technical performance.

</p>

</div>

<button
onClick={logout}
className="px-6 py-3 rounded-xl 
bg-red-600/20 
border border-red-500/30 
text-red-400 
font-bold text-xs uppercase tracking-widest
hover:bg-red-600/30 transition"
>

Logout

</button>

</header>

                <div className="bg-slate-900/30 border border-white/5 p-8 rounded-[2.5rem]">

                    <h4 className="text-xs font-black uppercase text-slate-500 mb-6">

                        Assessment Pipeline

                    </h4>

                    <div className="flex flex-wrap gap-6 text-xs">

                        <span className="px-4 py-2 bg-indigo-500/20 rounded-full text-indigo-400 font-bold">
                            Resume Parsed ✓
                        </span>

                        <span className="px-4 py-2 bg-indigo-500/20 rounded-full text-indigo-400 font-bold">
                            Personality Modeled ✓
                        </span>

                        <span className="px-4 py-2 bg-indigo-500/20 rounded-full text-indigo-400 font-bold">
                            Technical Evaluation ✓
                        </span>

                        <span className="px-4 py-2 bg-emerald-500/20 rounded-full text-emerald-400 font-bold">
                            Career Generated ✓
                        </span>

                    </div>

                </div>

                {/* PERFORMANCE SECTION */}
                <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-900/40 border border-white/5 p-8 rounded-[2.5rem]">
                        <p className="text-xs font-black text-slate-500 uppercase mb-4">Quiz Accuracy</p>
                        <div className="flex items-baseline gap-3">
                            <div className="flex items-end gap-4">

                                <span className="text-7xl font-black">
                                    {master.total_score}
                                </span>

                                <span className="text-3xl text-slate-600 mb-2">
                                    / {master.total_questions}
                                </span>

                                <span className="text-indigo-400 font-bold mb-3">

                                    ({
master.total_questions > 0
? Math.round(
(master.total_score / master.total_questions) * 100
)
: 0
}%)

                                </span>

                            </div>
                        </div>
                        <div className="mt-8 w-full h-1.5 bg-slate-800 rounded-full">
                            <div
                                className="h-full bg-indigo-500"
                                style={{
                                    width: `${
master.total_questions > 0
? (master.total_score / master.total_questions) * 100
: 0
}%`
                                }}
                            />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 p-8 rounded-[2.5rem] shadow-xl flex flex-col justify-between">
                        <p className="text-xs font-black uppercase text-white/50 mb-2">Market Standing</p>
                        <h3 className="text-4xl font-black">Career Mapping Ready</h3>
                        <p className="mt-4 text-sm font-bold uppercase text-indigo-100/70">
                            Deterministic Recommendation Engine
                        </p>
                        <button
                            onClick={() => window.location.href = '/resume-optimizer'}
                            className="mt-6 inline-flex items-center justify-center px-4 py-2 rounded-xl text-xs font-black uppercase tracking-[0.2em] bg-black/30 hover:bg-black/40 border border-white/20"
                        >
                            Optimize Resume for a Job
                        </button>
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

                        <div className="flex gap-3">

<button

    onClick={()=>fetchCareers(false)}

    disabled={loadingCareers}

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

{alreadyGenerated && (

<button

onClick={()=>fetchCareers(true)}

className="px-5 py-2 rounded-xl text-xs font-black uppercase tracking-widest

bg-purple-600 hover:bg-purple-500 transition"

>

Regenerate

</button>

)}

</div>

                    </div>

                    {careers.length === 0 && !loadingCareers && (
                        <p className="text-slate-500 text-sm">
                            Click Generate to analyze your profile.
                        </p>
                    )}

                    <div className="space-y-6">
                        {careers.map((career, idx) => (
                            <div key={idx}

                                className="bg-gradient-to-br from-slate-900 to-slate-800 
border border-indigo-500/10 p-8 rounded-3xl 
hover:border-indigo-500/30 transition shadow-xl">
                                <h3 className="text-xl font-black mb-2">
                                    {idx + 1}. {career.title}
                                </h3>

                                <div className="mb-6">

                                    <div className="text-5xl font-black text-indigo-400 mb-2">

{career.final_score}%

<p className="text-xs text-slate-500 mt-2">

Career confidence:

<span className="ml-2 font-bold text-indigo-400">

{career.confidence}

</span>

</p>

</div>

                                    <div className="w-full h-2 bg-slate-800 rounded-full">

                                        <div

                                            className="h-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full"

                                            style={{
                                                width: `${career.final_score}%`
                                            }}

                                        ></div>

                                    </div>

                                </div>

<div className="text-sm text-slate-400 space-y-2">

<p>
Technical Match:
<span className="text-indigo-400 ml-2">
{career.technical_fit}%
</span>
</p>

<p>
Personality Match:
<span className="text-indigo-400 ml-2">
{career.personality_fit}%
</span>
</p>
<p>
Confidence:
<span className="text-indigo-400 ml-2">
{career.confidence}
</span>
</p>

<p>
Skill Coverage:
<span className="text-indigo-400 ml-2">
{career.skill_coverage}%
</span>
</p>
<p>
Claimed Skills Match:
<span className="text-indigo-400 ml-2">
{career.claimed_alignment}%
</span>
</p>

{/* ⭐ JOB FIT ANALYZER */}
{career.reason && (

<div className="mt-3 p-3 bg-indigo-500/10 
border border-indigo-500/20 
rounded-xl">

<p className="text-xs font-bold text-indigo-400 mb-1">
Job Fit Analysis
</p>

<p className="text-xs">
{career.reason}
</p>

</div>




)}
{career.personality_fit && (

<div className="mt-3 p-3 bg-blue-500/10 
border border-blue-500/20 
rounded-xl">

<p className="text-xs font-bold text-blue-400 mb-1">
Personality Compatibility
</p>

<p className="text-xs text-slate-300">

This role matches your behavioral profile with {career.personality_fit}% compatibility.

</p>

</div>

)}

{/* ⭐ CAREER ROADMAP */}
{career.improvement_areas && career.improvement_areas.length > 0 && (

<div className="mt-3 p-3 bg-purple-500/10 
border border-purple-500/20 
rounded-xl">

<p className="text-xs font-bold text-purple-400 mb-1">
Career Roadmap
</p>

<p className="text-xs text-slate-300">

Improve skills:
{career.improvement_areas.join(", ")}

</p>

</div>

)}

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
                    className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-6 py-5 
bg-gradient-to-r from-indigo-600 to-purple-600 
rounded-2xl shadow-2xl hover:scale-105 transition-all
border border-indigo-400/20"
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
