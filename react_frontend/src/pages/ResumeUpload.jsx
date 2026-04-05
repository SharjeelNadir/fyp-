import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { API } from "../config";

const ResumeUpload = () => {

    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);

    const fileInputRef = useRef(null);

    const navigate = useNavigate();

    const handleUpload = async () => {

        if (!file) return;

        setLoading(true);

        const formData = new FormData();

        formData.append('file', file);

        try {

            const response = await fetch(`${API}/api/upload`,
                {
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                }
            );

            const data = await response.json();

            if (data.success) {

                localStorage.setItem(
                    'userSkills',
                    JSON.stringify(data.skills)
                );

                navigate('/personality');

            } else {

                alert("Upload failed. Are you logged in?");

            }

        } catch (error) {

            console.error(error);

        }
        finally {

            setLoading(false);

        }

    };

    const handleDragOver = (e) => {

        e.preventDefault();
        setIsDragging(true);

    };

    const handleDragLeave = () => {

        setIsDragging(false);

    };

    const handleDrop = (e) => {

        e.preventDefault();

        setIsDragging(false);

        if (e.dataTransfer.files[0]) {

            setFile(e.dataTransfer.files[0]);

        }

    };

    return (

        <div className="min-h-screen bg-[#020617] flex items-center justify-center px-6 relative overflow-hidden">

            {/* Background glows */}
            <div className="absolute top-[-15%] right-[-10%] w-[600px] h-[600px] bg-indigo-600/20 blur-[160px] rounded-full" />

            <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-600/10 blur-[150px] rounded-full" />


            <div className="w-full max-w-2xl bg-slate-900/40 backdrop-blur-2xl border border-white/10 p-12 rounded-[3rem] shadow-2xl">


                {/* Step indicator */}
                <div className="flex justify-center mb-10">

                    <div className="flex items-center gap-4 text-xs text-slate-500">

                        <span className="px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full font-bold">
                            Step 1
                        </span>

                        <span>→</span>

                        <span>Personality</span>

                        <span>→</span>

                        <span>Technical Quiz</span>

                    </div>

                </div>


                {/* Header */}
                <div className="text-center mb-12">

                    <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-indigo-500/30">

                        <span className="font-black text-2xl">
                            G
                        </span>

                    </div>

                    <h2 className="text-4xl font-black mb-3">

                        Resume Intelligence

                    </h2>

                    <p className="text-slate-400">

                        Upload your resume and let AI extract your skills.

                    </p>

                </div>


                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={(e) => setFile(e.target.files[0])}
                    className="hidden"
                    accept=".pdf,.docx,.txt"
                />


                {/* Drop zone */}
                <div

                    onClick={() => !loading && fileInputRef.current.click()}

                    onDragOver={handleDragOver}

                    onDragLeave={handleDragLeave}

                    onDrop={handleDrop}

                    className={`relative border-2 border-dashed rounded-[2.5rem] p-14 transition cursor-pointer mb-8 text-center

                    ${isDragging
                            ? 'border-indigo-500 bg-indigo-500/10 scale-[1.02]'
                            : 'border-white/10 bg-slate-800/30 hover:bg-slate-800/50'
                        }

                    ${loading ? 'pointer-events-none' : ''}
                    `}

                >

                    {loading && (

                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent animate-scan" />

                    )}

                    <div className="text-6xl mb-6">

                        {file ? '📄' : '☁️'}

                    </div>

                    <p className="font-bold text-lg">

                        {file ? file.name : "Drop Resume Here"}

                    </p>

                    <p className="text-slate-500 text-sm mt-2">

                        {loading
                            ? "AI analyzing document..."
                            : "PDF • DOCX • TXT"
                        }

                    </p>

                </div>


                {/* Upload button */}
                <button

                    onClick={handleUpload}

                    disabled={loading || !file}

                    className={`w-full py-5 rounded-2xl font-bold text-lg transition

                    ${loading || !file

                            ? 'bg-slate-800 text-slate-600'

                            : 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:scale-[1.02] active:scale-95 shadow-xl shadow-indigo-500/30'

                        }`}

                >

                    {loading
                        ? "Analyzing Resume..."
                        : "Start AI Analysis →"
                    }

                </button>


                {/* Footer */}
                <div className="mt-10 text-center">

                    <button

                        onClick={() => navigate('/dashboard')}

                        className="text-xs text-slate-600 hover:text-slate-400 transition"

                    >

                        ← Back

                    </button>

                </div>

            </div>


            <style dangerouslySetInnerHTML={{
                __html: `

                @keyframes scan{

                    0%{top:0%;opacity:0;}

                    50%{opacity:1;}

                    100%{top:100%;opacity:0;}

                }

                .animate-scan{

                    animation:scan 2s linear infinite;

                }

                `
            }} />

        </div>

    );

};

export default ResumeUpload;