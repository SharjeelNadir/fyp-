/*frontend_connected/react_frontend/src/pages/Personality.jsx*/
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Personality = () => {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchQuestions = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/personality-questions');
                if (!res.ok) throw new Error(`Server status: ${res.status}`);

                const data = await res.json();

                if (Array.isArray(data)) {
                    setQuestions(data);
                    // Initialize answers using the index as a key since the data lacks an ID
                    const initialAnswers = {};
                    data.forEach((_, index) => {
                        initialAnswers[index] = 3;
                    });
                    setAnswers(initialAnswers);
                }
            } catch (err) {
                console.error("Fetch error:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchQuestions();
    }, []);

    const handleNext = () => {
        const traitScores = {
            openness: 0,
            conscientiousness: 0,
            extraversion: 0,
            agreeableness: 0,
            neuroticism: 0
        };

        const traitCounts = { ...traitScores };

        questions.forEach((q, index) => {
            if (!q?.trait) return;

            const score = parseInt(answers[index] ?? 3);
            const traitKey = q.trait.toLowerCase();

            if (traitScores.hasOwnProperty(traitKey)) {
                traitScores[traitKey] += score;
                traitCounts[traitKey] += 1;
            }
        });

        const finalPersonality = {};

        Object.keys(traitScores).forEach(trait => {
            finalPersonality[trait] =
                traitCounts[trait] > 0
                    ? Math.round(traitScores[trait] / traitCounts[trait])
                    : 3;
        });

        localStorage.setItem('userPersonality', JSON.stringify(finalPersonality));
        navigate('/quiz');
    };

    if (loading) return (
        <div className="h-screen flex items-center justify-center bg-slate-900 text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            <p className="ml-4 font-bold">Llama is preparing your profile questions...</p>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-900 py-12 px-4 font-sans">
            <div className="max-w-3xl mx-auto bg-white p-8 md:p-12 rounded-[2rem] shadow-2xl">
                <header className="text-center mb-12">
                    <span className="bg-blue-100 text-blue-600 px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">Part 2: Soft Skills</span>
                    <h2 className="text-4xl font-black mt-4 text-slate-800">Personality Profile</h2>
                    <p className="text-slate-500 mt-2">Help our AI understand your work style and preferences.</p>
                </header>

                <div className="space-y-10">
                    {questions.map((q, index) => (
                        <div key={`q-${index}`} className="group">
                            <div className="flex justify-between items-start mb-4">
                                {/* FIXED: Using q.question instead of q.text */}
                                <p className="text-lg font-bold text-slate-700 leading-tight pr-4">
                                    {q.question}
                                </p>
                                <span className="text-blue-600 font-black text-xl bg-blue-50 w-10 h-10 flex items-center justify-center rounded-xl">
                                    {answers[index] || 3}
                                </span>
                            </div>

                            <div className="relative flex items-center">
                                <span className="text-xs font-bold text-slate-400 uppercase">Disagree</span>
                                <input
                                    type="range" min="1" max="5" step="1"
                                    value={answers[index] || 3}
                                    onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
                                    className="mx-4 w-full h-3 bg-slate-100 rounded-full appearance-none cursor-pointer accent-blue-600 hover:accent-blue-700 transition-all"
                                />
                                <span className="text-xs font-bold text-slate-400 uppercase">Agree</span>
                            </div>
                        </div>
                    ))}
                </div>

                <button
                    onClick={handleNext}
                    className="w-full mt-16 bg-slate-900 text-white py-5 rounded-2xl font-black text-xl shadow-xl hover:bg-blue-600 hover:-translate-y-1 transition-all active:scale-95"
                >
                    Proceed to Technical Quiz →
                </button>
            </div>
        </div>
    );
};

export default Personality;