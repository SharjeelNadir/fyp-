import { useNavigate } from 'react-router-dom';

const Dashboard = () => {

    const navigate = useNavigate();

    return (

        <div className="min-h-screen bg-[#020617] text-white p-10 font-sans relative overflow-hidden">

            {/* Background glow */}
            <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/20 blur-[160px] rounded-full" />

            <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 blur-[150px] rounded-full" />


            <div className="max-w-6xl mx-auto relative">

                {/* Header */}
                <div className="mb-12">

                    <h1 className="text-5xl font-black mb-3">

                        Dashboard

                    </h1>

                    <p className="text-slate-400">

                        Your AI Career Assistant control center

                    </p>

                </div>


                {/* AI Overview Card */}
                <div className="bg-slate-900/40 backdrop-blur-xl border border-white/10 rounded-3xl p-10 mb-10 shadow-2xl">

                    <h2 className="text-2xl font-bold mb-3">

                        AI Career Analysis

                    </h2>

                    <p className="text-slate-400 mb-6">

                        Complete the assessment to unlock your personalized career recommendations.

                    </p>

                    {/* Progress Steps */}
                    <div className="flex flex-wrap gap-6 text-sm text-slate-400">

                        <span className="px-4 py-2 bg-indigo-500/20 text-indigo-400 rounded-full font-bold">
                            Resume Upload
                        </span>

                        <span className="px-4 py-2 bg-slate-800 rounded-full">
                            Personality Test
                        </span>

                        <span className="px-4 py-2 bg-slate-800 rounded-full">
                            Technical Quiz
                        </span>

                        <span className="px-4 py-2 bg-slate-800 rounded-full">
                            Career Results
                        </span>

                    </div>

                </div>


                {/* Action cards */}
                <div className="grid md:grid-cols-2 gap-8">


                    {/* Start card */}
                    <div className="bg-slate-900/40 backdrop-blur-xl border border-white/10 p-10 rounded-3xl shadow-xl hover:scale-[1.02] transition">

                        <div className="text-5xl mb-6">

                            🚀

                        </div>

                        <h3 className="text-2xl font-bold mb-3">

                            Start Assessment

                        </h3>

                        <p className="text-slate-400 mb-8">

                            Upload your resume and let AI extract your technical profile.

                        </p>

                        <button

                            onClick={() => navigate('/resume-upload')}

                            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 py-4 rounded-2xl font-bold text-lg hover:scale-[1.02] active:scale-95 transition shadow-xl shadow-indigo-500/30"

                        >

                            Upload Resume →

                        </button>

                    </div>


                    {/* Locked results */}
                    <div className="bg-slate-900/20 border border-dashed border-white/10 p-10 rounded-3xl flex flex-col items-center justify-center text-center">

                        <div className="text-4xl mb-4 opacity-40">

                            🔒

                        </div>

                        <h3 className="font-bold text-slate-400 mb-2">

                            Full Career Analysis Locked

                        </h3>

                        <p className="text-slate-500 text-sm">

                            Complete assessment to unlock insights

                        </p>

                    </div>

                </div>

            </div>

        </div>

    );

};

export default Dashboard;