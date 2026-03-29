/*frontend_connected/react_frontend/src/pages/ResumeUpload.jsx*/
import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

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
            // Inside handleUpload in ResumeUpload.jsx
            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
                credentials: 'include', // 🔥 MUST ADD THIS
            });

            const data = await response.json();

            if (data.success) {
                // Still keep this in localStorage for fast UI updates
                localStorage.setItem('userSkills', JSON.stringify(data.skills));
                navigate('/personality');
            } else {
                alert("Upload failed. Are you logged in?");
            }
        } catch (error) {
            console.error("Upload error:", error);
        } finally {
            setLoading(false);
        }
    };

    // Drag and Drop Handlers
    const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
    const handleDragLeave = () => setIsDragging(false);
    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
    };

    return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6 relative overflow-hidden font-sans">
            {/* Ambient Background Decoration */}
            <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/10 blur-[120px] rounded-full -z-10"></div>
            <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-600/10 blur-[120px] rounded-full -z-10"></div>

            <div className="w-full max-w-xl bg-slate-900/40 backdrop-blur-2xl border border-white/10 p-10 rounded-[3rem] shadow-2xl relative">

                <header className="text-center mb-10">
                    <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-indigo-500/20">
                        <span className="text-white font-black italic text-xl">G</span>
                    </div>
                    <h2 className="text-4xl font-black text-white tracking-tighter">Skill <span className="text-indigo-500 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Extraction.</span></h2>
                    <p className="text-slate-400 mt-2 font-medium">Llama 3.1 will decode your technical DNA.</p>
                </header>

                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={(e) => setFile(e.target.files[0])}
                    className="hidden"
                    accept=".pdf,.docx,.txt"
                />

                {/* Dropzone Area */}
                <div
                    onClick={() => !loading && fileInputRef.current.click()}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`relative group border-2 border-dashed rounded-[2.5rem] p-12 transition-all cursor-pointer mb-8 flex flex-col items-center justify-center overflow-hidden
                        ${isDragging ? 'border-indigo-500 bg-indigo-500/10 scale-[1.02]' : 'border-white/10 bg-slate-800/20 hover:border-white/20 hover:bg-slate-800/40'}
                        ${loading ? 'cursor-wait pointer-events-none' : ''}
                    `}
                >
                    {/* The Scanner Animation (Visible only when loading) */}
                    {loading && (
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent animate-scan z-20"></div>
                    )}

                    <div className={`text-6xl mb-6 transition-transform duration-500 ${loading ? 'animate-bounce' : 'group-hover:-translate-y-2'}`}>
                        {file ? '📄' : '☁️'}
                    </div>

                    <p className="text-white font-black text-lg tracking-tight">
                        {file ? file.name : "Select Resume"}
                    </p>
                    <p className="text-slate-500 text-sm mt-2 font-bold uppercase tracking-widest">
                        {loading ? "Neural engine active..." : "PDF, DOCX, or TXT"}
                    </p>

                    {/* Visual pulse for drag state */}
                    {isDragging && (
                        <div className="absolute inset-0 bg-indigo-500/5 animate-pulse"></div>
                    )}
                </div>

                <button
                    onClick={handleUpload}
                    disabled={loading || !file}
                    className={`group relative w-full p-5 rounded-2xl font-black text-lg transition-all overflow-hidden
                        ${loading || !file
                            ? 'bg-slate-800 text-slate-600 cursor-not-allowed border border-white/5'
                            : 'bg-white text-black hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-white/5'}
                    `}
                >
                    <span className="relative z-10">
                        {loading ? "Scanning Document..." : "Initialize Analysis →"}
                    </span>
                    {/* Shimmer effect for button */}
                    {!loading && file && (
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-black/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                    )}
                </button>

                <footer className="mt-8 text-center">
                    <div className="flex items-center justify-center gap-2 px-4 py-2 bg-white/5 rounded-full w-fit mx-auto border border-white/5">
                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-ping"></span>
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">GuideMe Core v2.0</span>
                    </div>
                </footer>
            </div>

            {/* Added custom animation styles for the scanner */}
            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes scan {
                    0% { top: 0%; opacity: 0; }
                    50% { opacity: 1; }
                    100% { top: 100%; opacity: 0; }
                }
                .animate-scan {
                    animation: scan 2s linear infinite;
                }
            `}} />
        </div>
    );
};

export default ResumeUpload;