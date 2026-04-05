import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { API } from "../config";

const Quiz = () => {

    const navigate = useNavigate();

    const [questions, setQuestions] = useState([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [answerLocked, setAnswerLocked] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(true);
    const [expectedTotal, setExpectedTotal] = useState(null);
    const [generatedTotal, setGeneratedTotal] = useState(0);
    const [elapsedSeconds, setElapsedSeconds] = useState(null);
    const [waitingForMore,setWaitingForMore] = useState(false);

    const scoreRef = useRef(0);
    const breakdownRef = useRef([]);
    const pollRef = useRef(null);
    const MIN_START_QUESTIONS = 8; // fallback if server doesn't send expected_total


    useEffect(() => {

        const fetchQuiz = async () => {
            try {
                const res = await fetch(`${API}/api/quiz`,
                    { credentials: "include" }
                );

                const data = await res.json();

                const fetchedQuestions = data.questions || [];
                const generating = !!data.generating;
                const expected = Number.isFinite(Number(data.expected_total))
                    ? Number(data.expected_total)
                    : null;
                const generated = Number.isFinite(Number(data.generated_total))
                    ? Number(data.generated_total)
                    : fetchedQuestions.length;
                const elapsed = (data.elapsed_seconds === null || data.elapsed_seconds === undefined)
                    ? null
                    : Number(data.elapsed_seconds);

                setQuestions(prev => {

    if(fetchedQuestions.length > prev.length)
        return fetchedQuestions;

    return prev;

});

                setIsGenerating(generating);
                setExpectedTotal(expected);
                setGeneratedTotal(generated);
                setElapsedSeconds(Number.isFinite(elapsed) ? elapsed : null);

                // Only start quiz after generation finished AND expected total reached (if known)
                if(generated > 0){
    setLoading(false);
}else{
    setLoading(true);
}

                // Poll while generating OR until expected count reached
                const shouldPoll = generating || (expected ? generated < expected : true);
                if (shouldPoll && !pollRef.current) {

                    pollRef.current = setInterval(() => {
                
                        fetchQuiz();
                
                    },1200);
                }

                if (!shouldPoll && pollRef.current) {
                    clearInterval(pollRef.current);
                    pollRef.current = null;
                }
            }
            catch (err) {
                console.error(err);
                setLoading(false);
            }
        };

        fetchQuiz();

        return () => {
            if (pollRef.current) {
                clearInterval(pollRef.current);
                pollRef.current = null;
            }
        };

    }, []);
    useEffect(()=>{

    if(waitingForMore && questions.length > currentIdx){

        setWaitingForMore(false);

        setAnswerLocked(false);

    }

},[questions.length, waitingForMore, currentIdx]);



    const handleAnswer = (choice) => {

        if (answerLocked) return;

        setAnswerLocked(true);

        const q = questions[currentIdx] || {};

        const correct = choice === q?.answer;

        breakdownRef.current.push([

            q.skill,

            correct ? 1 : 0

        ]);

        if (correct) {

            scoreRef.current++;

        }

        setTimeout(() => {

            const next = currentIdx + 1;

            if (next < questions.length) {

                setCurrentIdx(next);

                setAnswerLocked(false);

                return;

            }

            
            if (currentIdx >= questions.length-1 && isGenerating){

    setWaitingForMore(true);

    setAnswerLocked(false);

    return;

}

            submitResults();

        }, 200);

    };



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

                `${API}/api/save-results`,

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

        }
        catch (err) {

            console.error(err);

        }

    };



    if (loading)
        return (
    
            <div className="h-screen flex flex-col items-center justify-center bg-[#020617] text-white">
    
                <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-6" />
    
                <p className="text-slate-400 font-bold">
                    AI generating technical assessment...
                </p>
    
                <p className="text-slate-500 text-xs mt-2">
                    {expectedTotal
                        ? `Generated ${generatedTotal}/${expectedTotal} questions`
                        : `Generated ${generatedTotal} questions`}
                    {elapsedSeconds !== null ? ` • ${elapsedSeconds}s elapsed` : ""}
                </p>
    
                {/* ADD THIS PART */}
                {waitingForMore && (
                    <p className="text-xs text-indigo-400 mt-3">
                        Generating remaining questions...
                    </p>
                )}
    
            </div>
    
        );



    if (questions.length === 0)

        return (

            <div className="h-screen flex items-center justify-center bg-[#020617] text-white">

                No quiz generated. Upload resume again.

            </div>

        );



const q = questions[currentIdx];

const splitQuestion = (text) => {

    if(!text) return {text:"",code:null};

    const match = text.match(/```([\s\S]*?)```|`([\s\S]*?)`/);

    if(!match){
        return {text,code:null};
    }

    const code = (match[1] || match[2])
    .replace(/{/g,"{\n")
    .replace(/;/g,";\n")
    .replace(/}/g,"\n}");

    return {
        text: text.replace(match[0], "").trim(),
        code: code
    };

};

const parsed = splitQuestion(q.question);

const total = expectedTotal || questions.length;

const progress = ((currentIdx + 1) / total) * 100;

    return (

        <div className="min-h-screen bg-[#020617] text-white flex items-center justify-center p-8">

            <div className="w-full max-w-3xl bg-slate-900/40 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-12 shadow-2xl">

                {isGenerating && (
                    <div className="mb-6 flex items-center justify-between gap-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl px-5 py-3">
                        <p className="text-xs font-bold text-indigo-300">
                            More questions are still generating in the background.
                        </p>
                        <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                    </div>
                )}

                {/* HEADER */}
                <div className="mb-10">

                    <div className="flex justify-between mb-4">

                        <span className="px-4 py-1.5 rounded-xl bg-indigo-500/20 text-indigo-400 font-bold">

                            {q.skill}

                        </span>

                        <span className="text-slate-400">

                            {currentIdx + 1} / {expectedTotal || questions.length}

                        </span>

                    </div>


                    {/* Progress bar */}
                    <div className="w-full h-2 bg-slate-800 rounded-full">

                        <div

                            style={{ width: `${progress}%` }}

                            className="h-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all"

                        />

                    </div>

                </div>
{isGenerating && (
<div className="text-xs text-indigo-400">
Generated {generatedTotal}/{expectedTotal}
</div>
)}


                {/* QUESTION */}

<div className="mb-12">

<div className="text-xl font-semibold leading-relaxed whitespace-pre-line">
    {parsed.text}
</div>

{parsed.code && (
<SyntaxHighlighter
    language="javascript"
    style={vscDarkPlus}
    customStyle={{
        borderRadius:"16px",
        marginTop:"24px",
        fontSize:"14px"
    }}
>
{parsed.code}
</SyntaxHighlighter>
)}

</div>



                {/* OPTIONS */}

                <div className="grid gap-5">

                    {["A", "B", "C", "D"].map(k => (

                        <button

                            key={k}

                            disabled={answerLocked}

                            onClick={() => handleAnswer(k)}

                            className={`p-6 rounded-2xl border text-left transition

                            ${answerLocked

                                    ? 'opacity-40'

                                    : 'bg-slate-800/40 hover:border-indigo-500 hover:bg-slate-800/70 hover:scale-[1.01]'

                                }`}

                        >

                            <span className="font-black text-indigo-400 mr-4">

                                {k}

                            </span>

                            {q.options?.[k]}

                        </button>

                    ))}

                </div>



                {/* Footer */}
                <div className="mt-10 text-xs text-slate-500 text-center">

                    AI evaluates skills dynamically based on responses

                </div>


            </div>

        </div>

    );

};

export default Quiz;