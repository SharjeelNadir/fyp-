import { useNavigate } from 'react-router-dom';
import { API } from "../config";

const successStories = [

{
career:"Software Engineering",
title:"From Average Student → Software Engineer",
problem:"Weak coding fundamentals and no direction",
actions:"Learned Data Structures, solved LeetCode daily, built 3 projects",
outcome:"Software Engineer",
company:"Google",
quote:"Consistency beats talent when talent doesn't work hard."
},

{
career:"Data Science",
title:"Confused Student → Data Analyst",
problem:"No specialization path",
actions:"Python, Pandas, SQL, Kaggle projects, Power BI dashboards",
outcome:"Data Analyst",
company:"Deloitte",
quote:"Small projects can open big doors."
},

{
career:"AI / Machine Learning",
title:"Self-Taught AI Engineer",
problem:"No AI courses at university",
actions:"YouTube ML courses, built classifiers, hackathons",
outcome:"ML Engineer",
company:"IBM",
quote:"You don’t need resources, you need resourcefulness."
},

{
career:"Web Development",
title:"Freelancer → Full Stack Developer",
problem:"Needed experience and income",
actions:"React, Node, freelancing, client projects",
outcome:"Full Stack Developer",
company:"Shopify",
quote:"Start small, but start now."
},

{
career:"Cybersecurity",
title:"Networking Student → Security Analyst",
problem:"No structured roadmap",
actions:"Networking fundamentals, TryHackMe labs, Security+",
outcome:"Security Analyst",
company:"Cisco",
quote:"Curiosity can become your career."
},

{
career:"Cloud / DevOps",
title:"Backend Developer → DevOps Engineer",
problem:"Deployment knowledge missing",
actions:"Docker, AWS, CI/CD pipelines, Kubernetes basics",
outcome:"DevOps Engineer",
company:"Amazon",
quote:"Learn how software runs, not just how it's written."
}

];

const Landing = () => {

const navigate = useNavigate();

return (

<div className="min-h-screen bg-[#020617] text-white font-sans selection:bg-indigo-500/30 overflow-x-hidden">

{/* Ambient background */}
<div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10">

<div className="absolute top-[-10%] left-[-10%] w-[700px] h-[700px] bg-indigo-600/20 blur-[160px] rounded-full"/>

<div className="absolute bottom-[5%] right-[-5%] w-[600px] h-[600px] bg-cyan-500/10 blur-[150px] rounded-full"/>

</div>

{/* Navbar */}

<nav className="max-w-7xl mx-auto px-8 py-8 flex justify-between items-center">

<div className="flex items-center gap-3 cursor-pointer">

<div className="w-11 h-11 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-xl">

<span className="text-xl font-black">G</span>

</div>

<span className="text-2xl font-black">

Guide<span className="text-indigo-500">Me</span>

</span>

</div>

<div className="flex items-center gap-10">

<button
onClick={()=>navigate('/login')}
className="text-sm text-slate-400 hover:text-white"
>
Login
</button>

<button
onClick={()=>navigate('/signup')}
className="px-7 py-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 text-sm font-bold hover:scale-105 transition"
>
Get Started
</button>

</div>

</nav>

{/* Hero */}

<main className="max-w-6xl mx-auto px-8 pt-24 pb-24 text-center">

<div className="inline-flex px-5 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold mb-10">
AI Career Intelligence Engine
</div>

<h1 className="text-6xl md:text-8xl font-black mb-10">

Your Career

<span className="block bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-cyan-400 to-purple-500">
Reimagined with AI
</span>

</h1>

<p className="text-xl text-slate-400 max-w-3xl mx-auto mb-14">

GuideMe analyzes your resume, verifies your skills,
evaluates personality, and maps you to the best tech careers.

</p>

<div className="flex justify-center gap-6">

<button
onClick={()=>navigate('/signup')}
className="px-14 py-5 bg-indigo-600 rounded-2xl font-bold text-xl hover:scale-105"
>

Start Assessment →

</button>

<button className="px-14 py-5 border border-slate-800 rounded-2xl">

How it Works

</button>

</div>

{/* Features */}

<div className="grid md:grid-cols-3 gap-8 mt-28">

<div className="p-8 rounded-2xl bg-white/5 border border-white/10">

<h3 className="font-bold mb-3">
Resume Intelligence
</h3>

<p className="text-slate-400 text-sm">
NLP skill extraction from resume.
</p>

</div>

<div className="p-8 rounded-2xl bg-white/5 border border-white/10">

<h3 className="font-bold mb-3">
Skill Verification
</h3>

<p className="text-slate-400 text-sm">
AI quizzes validate real knowledge.
</p>

</div>

<div className="p-8 rounded-2xl bg-white/5 border border-white/10">

<h3 className="font-bold mb-3">
Career Matching
</h3>

<p className="text-slate-400 text-sm">
Hybrid AI career recommendations.
</p>

</div>

</div>

{/* SUCCESS STORIES */}

{/* SUCCESS STORIES */}

<div className="mt-36">

<h2 className="text-4xl font-black mb-6 text-center">

Career Success Stories

</h2>

<p className="text-slate-400 mb-14 text-center">

Real journeys students can follow with GuideMe.

</p>

<div className="overflow-hidden relative">

<div className="flex gap-8 scroll-track w-[200%]">

{[...successStories,...successStories].map((story,index)=>(

<div
key={index}
className="min-w-[320px] p-8 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition"
>

<div className="text-xs text-indigo-400 font-bold uppercase mb-2">

{story.career}

</div>

<h3 className="text-xl font-bold mb-4">

{story.title}

</h3>

<div className="text-sm text-slate-400 space-y-2">

<p>

<span className="text-white font-semibold">
Problem:
</span>

{story.problem}

</p>

<p>

<span className="text-white font-semibold">
Actions:
</span>

{story.actions}

</p>

<p>

<span className="text-white font-semibold">
Outcome:
</span>

{story.outcome}

</p>

</div>

<div className="mt-5 text-green-400 font-bold">

{story.company}

</div>

<div className="mt-4 text-indigo-400 text-sm italic">

"{story.quote}"

</div>

</div>

))}

</div>

</div>

</div>
{/* Trust */}

<div className="mt-28 pt-12 border-t border-white/5">

<p className="text-xs text-slate-500 mb-8">

Built for students from

</p>

<div className="flex justify-center gap-14 opacity-40">

<span className="text-2xl font-black">FAST</span>
<span className="text-2xl font-black">NUST</span>
<span className="text-2xl font-black">COMSATS</span>
<span className="text-2xl font-black">GIKI</span>

</div>

</div>

</main>

</div>

);

};

export default Landing;