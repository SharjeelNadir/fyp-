/*frontend_connected/react_frontend/src/pages/Dashboard.jsx*/
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const navigate = useNavigate();

    return (
        <div className="p-10 bg-slate-50 min-h-screen font-sans">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-black text-slate-900 mb-2">User Dashboard</h1>
                <p className="text-slate-500 mb-10">Welcome to your AI Career Assistant.</p>

                <div className="grid md:grid-cols-2 gap-8">
                    <div className="bg-white p-8 rounded-3xl border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                        <div className="text-4xl mb-4">🚀</div>
                        <h3 className="text-2xl font-bold text-blue-600 mb-2">Guided Path</h3>
                        <p className="text-slate-500 mb-6">
                            Start your journey here. Upload your resume and let AI analyze your technical profile.
                        </p>

                        <button
                            onClick={() => navigate('/resume-upload')}
                            className="w-full bg-blue-600 text-white px-6 py-4 rounded-xl font-bold hover:bg-blue-700 active:scale-95 transition-all"
                        >
                            Upload Resume →
                        </button>
                    </div>

                    <div className="bg-slate-100 p-8 rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center opacity-60">
                        <p className="font-bold text-slate-400 text-center">
                            Full Analysis <br /> (Locked until Assessment)
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;