import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const Quiz = () => {

    const navigate = useNavigate();

    // STATE
    const [questions, setQuestions] = useState([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [answerLocked, setAnswerLocked] = useState(false);
    const [loading, setLoading] = useState(true);

    // SAFE REFS
    const scoreRef = useRef(0);
    const breakdownRef = useRef([]);

    // ===============================
    // LOAD QUIZ FROM DATABASE
    // ===============================
    useEffect(() => {

        const loadQuiz = async () => {

            try {

                const res = await fetch(

                    "http://localhost:8000/api/quiz",

                    { credentials: "include" }

                );

                if (!res.ok) {

                    console.error("Quiz not found");
                    return;

                }

                const data = await res.json();

                setQuestions(data);

                setLoading(false);

            } catch (err) {

                console.error("Quiz load failed:", err);

            }

        };

        loadQuiz();

    }, []);

    // ===============================
    // HANDLE ANSWER
    // ===============================
    const handleAnswer = (choice) => {

        if (answerLocked) return;

        setAnswerLocked(true);

        const q = questions[currentIdx] || {};

        const isCorrect = choice === q.answer;

        breakdownRef.current.push([
            q.skill,
            isCorrect ? 1 : 0
        ]);

        if (isCorrect) {

            scoreRef.current++;

        }

        setTimeout(() => {

            const next = currentIdx + 1;

            if (next < questions.length) {

                setCurrentIdx(next);
                setAnswerLocked(false);
                return;

            }

            submitResults();

        }, 150);

    };

    // ===============================
    // SAVE RESULTS
    // ===============================
    const submitResults = async () => {

        const payload = {

            total_score: scoreRef.current,

            total_questions: breakdownRef.current.length,

            personality: JSON.parse(
                localStorage.getItem("userPersonality")
            ),

            breakdown: breakdownRef.current

        };

        try {

            const res = await fetch(

                "http://localhost:8000/api/save-results",

                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify(payload)

                }

            );

            if (res.ok) {

                navigate("/profile");

            }

        } catch (err) {

            console.error("Save failed:", err);

        }

    };

    // ===============================
    // LOADING SCREEN
    // ===============================
    if (loading) {

        return (

            <div className="h-screen flex items-center justify-center bg-[#020617] text-white">

                <div className="text-xl font-bold">

                    Loading Quiz...

                </div>

            </div>

        );

    }

    if (questions.length === 0) {

        return (

            <div className="h-screen flex items-center justify-center bg-[#020617] text-white">

                No questions found. Upload resume again.

            </div>

        );

    }

    const q = questions[currentIdx];

    // ===============================
    // UI
    // ===============================
    return (

        <div className="min-h-screen bg-[#020617] text-white p-6 flex items-center justify-center">

            <div className="w-full max-w-3xl bg-slate-900/40 border border-white/10 rounded-[2.5rem] p-10">

                {/* HEADER */}

                <div className="flex justify-between mb-8">

                    <span className="px-4 py-1.5 rounded-xl bg-indigo-500/20">

                        {q.skill}

                    </span>

                    <span>

                        {currentIdx + 1} / {questions.length}

                    </span>

                </div>

                {/* QUESTION */}

                <div className="mb-10 text-2xl font-bold">

                    {q.question}

                </div>

                {/* OPTIONS */}

                <div className="grid gap-4">

                    {["A", "B", "C", "D"].map(k => (

                        <button

                            key={k}

                            disabled={answerLocked}

                            onClick={() => handleAnswer(k)}

                            className={`p-6 rounded-2xl text-left border transition
                            ${answerLocked
                                    ? 'opacity-50 cursor-not-allowed'
                                    : 'bg-slate-800/30 hover:border-indigo-500'
                                }`}

                        >

                            <strong className="mr-4">

                                {k}

                            </strong>

                            {q.options?.[k]}

                        </button>

                    ))}

                </div>

            </div>

        </div>

    );

};

export default Quiz;