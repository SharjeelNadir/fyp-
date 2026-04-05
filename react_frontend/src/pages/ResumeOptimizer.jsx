import { useState } from 'react';
import { API } from "../config";

const ResumeOptimizer = () => {
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [file, setFile] = useState(null);
    const [latex, setLatex] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        const f = e.target.files?.[0];
        setFile(f || null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!file || !jobTitle.trim() || !jobDescription.trim()) {
            setError('Please upload a resume and fill job title + description.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('job_title', jobTitle);
        formData.append('job_description', jobDescription);

        setLoading(true);
        setLatex('');

        try {
            const res = await fetch(`${API}/api/optimize-resume-latex`, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            if (!res.ok) {
                const msg = await res.text();
                throw new Error(msg || 'Failed to optimize resume');
            }

            const data = await res.json();
            setLatex(data.latex || '');
        } catch (err) {
            console.error(err);
            setError('Failed to generate LaTeX resume. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (!latex) return;
        const blob = new Blob([latex], { type: 'text/x-tex' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeTitle = jobTitle || 'optimized_resume';
        a.download = `${safeTitle.replace(/[^a-z0-9]+/gi, '_').toLowerCase()}.tex`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen bg-[#020617] text-white p-6 md:p-12">
            <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-10">
                {/* Left: Form */}
                <div className="space-y-6">
                    <h1 className="text-4xl font-black mb-2">
                        Resume <span className="text-indigo-400">Optimizer</span>
                    </h1>
                    <p className="text-slate-400 text-sm mb-6">
                        Upload your resume and target job, and we&apos;ll generate a LaTeX resume tailored to that role.
                    </p>

                    <form onSubmit={handleSubmit} className="space-y-5 bg-slate-900/40 border border-white/10 p-6 rounded-3xl">
                        <div>
                            <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
                                Resume file (PDF / DOCX / TXT)
                            </label>
                            <input
                                type="file"
                                accept=".pdf,.doc,.docx,.txt"
                                onChange={handleFileChange}
                                className="w-full text-sm text-slate-200"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
                                Job Title
                            </label>
                            <input
                                value={jobTitle}
                                onChange={e => setJobTitle(e.target.value)}
                                placeholder="e.g. Backend Software Engineer"
                                className="w-full bg-slate-800 text-white px-4 py-3 rounded-xl text-sm outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold uppercase text-slate-400 mb-2">
                                Job Description
                            </label>
                            <textarea
                                value={jobDescription}
                                onChange={e => setJobDescription(e.target.value)}
                                placeholder="Paste the full job description here..."
                                rows={8}
                                className="w-full bg-slate-800 text-white px-4 py-3 rounded-xl text-sm outline-none resize-none"
                            />
                        </div>

                        {error && (
                            <p className="text-xs text-red-400">
                                {error}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 rounded-xl text-sm font-black uppercase tracking-[0.2em] 
                                ${loading ? 'bg-slate-700 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-500'}`}
                        >
                            {loading ? 'Optimizing…' : 'Generate LaTeX Resume'}
                        </button>
                    </form>
                </div>

                {/* Right: Preview */}
                <div className="bg-slate-900/40 border border-white/10 p-6 rounded-3xl flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-black uppercase tracking-[0.2em] text-slate-400">
                            LaTeX Preview
                        </h2>
                        <button
                            onClick={handleDownload}
                            disabled={!latex}
                            className={`px-4 py-2 rounded-lg text-xs font-black uppercase tracking-[0.2em]
                                ${latex ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-slate-700 cursor-not-allowed'}`}
                        >
                            Download .tex
                        </button>
                    </div>

                    <div className="flex-1 bg-black/60 rounded-2xl p-4 overflow-auto text-xs font-mono text-slate-200">
                        {latex
                            ? <pre className="whitespace-pre-wrap">{latex}</pre>
                            : <p className="text-slate-500">Generated LaTeX will appear here.</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResumeOptimizer;

