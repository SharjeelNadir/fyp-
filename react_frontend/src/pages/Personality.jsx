import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API } from "../config";

const Personality = () => {

    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(true);

    const navigate = useNavigate();

useEffect(() => {
    const fetchQuestions = async () => {

        try {

            const res = await fetch(
                `${API}/api/personality-questions`
            );

            const data = await res.json();

            if (Array.isArray(data)) {

                setQuestions(data);

                const initial = {};

                data.forEach((_, index) => {

                    initial[index] = 3;

                });

                setAnswers(initial);

                setLoading(false);

            }

        }
        catch (err) {

            console.error(err);

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

            const key = q.trait.toLowerCase();

            if (Object.prototype.hasOwnProperty.call(traitScores, key)) {

                traitScores[key] += score;

                traitCounts[key] += 1;

            }

        });


        const finalPersonality = {};

        Object.keys(traitScores).forEach(trait => {

            finalPersonality[trait] =

                traitCounts[trait] > 0

                    ? Math.round(
                        traitScores[trait] /
                        traitCounts[trait]
                    )

                    : 3;

        });

        localStorage.setItem(
            'userPersonality',
            JSON.stringify(finalPersonality)
        );

        navigate('/quiz');

    };



    if (loading)

        return (

            <div className="h-screen flex flex-col items-center justify-center bg-[#020617] text-white">

                <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-6" />

                <p className="text-slate-400 font-bold">

                    AI preparing personality assessment...

                </p>

            </div>

        );



    return (

        <div className="min-h-screen bg-[#020617] py-16 px-6 text-white">

            <div className="max-w-4xl mx-auto">


                {/* Steps */}
                <div className="flex justify-center mb-12 text-xs text-slate-500 gap-4">

                    <span className="px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full font-bold">
                        Resume
                    </span>

                    <span>→</span>

                    <span className="px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full font-bold">
                        Personality
                    </span>

                    <span>→</span>

                    <span>
                        Technical
                    </span>

                    <span>→</span>

                    <span>
                        Results
                    </span>

                </div>


                {/* Card */}
                <div className="bg-slate-900/40 backdrop-blur-xl border border-white/10 p-12 rounded-[2.5rem] shadow-2xl">


                    <header className="text-center mb-14">

                        <h2 className="text-4xl font-black mb-3">

                            Personality Analysis

                        </h2>

                        <p className="text-slate-400">

                            Help AI understand your behavioral traits.

                        </p>

                    </header>



                    <div className="space-y-8">

                        {questions.map((q, index) => (

                            <div
                                key={index}

                                className="bg-slate-800/40 p-8 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition"
                            >

                                <div className="flex justify-between mb-6">

                                    <p className="font-bold text-lg text-slate-200">

                                        {q.question}

                                    </p>

                                    <div className="w-12 h-12 bg-indigo-500/20 text-indigo-400 rounded-xl flex items-center justify-center font-black">

                                        {answers[index] || 3}

                                    </div>

                                </div>



                                <div className="flex items-center">

                                    <span className="text-xs text-slate-500 font-bold">

                                        DISAGREE

                                    </span>

                                    <input

                                        type="range"

                                        min="1"

                                        max="5"

                                        value={answers[index] || 3}

                                        onChange={(e) =>

                                            setAnswers({

                                                ...answers,

                                                [index]: e.target.value

                                            })

                                        }

                                        className="mx-5 w-full accent-indigo-500"

                                    />

                                    <span className="text-xs text-slate-500 font-bold">

                                        AGREE

                                    </span>

                                </div>

                            </div>

                        ))}

                    </div>



                    <button

                        onClick={handleNext}

                        className="w-full mt-16 bg-gradient-to-r from-indigo-500 to-purple-600 py-5 rounded-2xl font-bold text-lg hover:scale-[1.02] active:scale-95 transition shadow-xl shadow-indigo-500/30"

                    >

                        Continue Assessment →

                    </button>

                </div>

            </div>

        </div>

    );

};

export default Personality;