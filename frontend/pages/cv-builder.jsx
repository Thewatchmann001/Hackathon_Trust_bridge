import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useRouter } from "next/router";
import { cvAPI } from "../lib/api";
import toast from "react-hot-toast";
import {
  User, FileText, Briefcase, GraduationCap,
  Wand2, Download, Upload, Layout, ChevronRight, ChevronLeft,
  Plus, Trash2, CheckCircle2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Logo from "../components/Logo";

export default function CVBuilder() {
  const { user } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [cvData, setCvData] = useState({
    personal_info: {
      full_name: "",
      email: "",
      phone: "",
      location: "",
      linkedin: "",
      portfolio: "",
      photo_url: ""
    },
    summary: "",
    work_experience: [],
    education: [],
    skills: {
      technical: [],
      soft: [],
      languages: []
    },
    certifications: [],
    template_name: "Modern"
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push("/login");
      return;
    }
    loadExistingCV();
  }, [user]);

  const loadExistingCV = async () => {
    try {
      const response = await cvAPI.getMe();
      if (response.data) {
        setCvData(response.data);
      }
    } catch (err) {
      console.log("No existing CV found or error loading");
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await cvAPI.save(cvData);
      toast.success("CV Saved Successfully!");
    } catch (err) {
      toast.error("Failed to save CV");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await cvAPI.exportPDF(cvData);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'my-cv.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      toast.error("Failed to export PDF");
    }
  };

  const handleAIEnhance = async (section, content) => {
    try {
      const response = await cvAPI.aiEnhance({ section, content });
      return response.data.enhanced_content;
    } catch (err) {
      toast.error("AI Enhancement failed");
      return content;
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      const response = await cvAPI.uploadParse(formData);
      setCvData(prev => ({ ...prev, ...response.data }));
      toast.success("CV Parsed Successfully!");
    } catch (err) {
      toast.error("Failed to parse CV");
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => setStep(s => Math.min(s + 1, 7));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center sticky top-0 z-10">
        <Logo />
        <div className="flex items-center gap-4">
          <button onClick={handleSave} className="btn-secondary flex items-center gap-2">
            <FileText size={18} /> Save Draft
          </button>
          <button onClick={handleExport} className="btn-primary flex items-center gap-2">
            <Download size={18} /> Export PDF
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Navigation */}
        <aside className="w-64 bg-white border-r p-4 hidden md:block">
          <nav className="space-y-1">
            {[
              { id: 1, label: "Personal Info", icon: User },
              { id: 2, label: "Summary", icon: FileText },
              { id: 3, label: "Work Experience", icon: Briefcase },
              { id: 4, label: "Education", icon: GraduationCap },
              { id: 5, label: "Skills", icon: Wand2 },
              { id: 6, label: "Certifications", icon: CheckCircle2 },
              { id: 7, label: "Template", icon: Layout },
            ].map(i => (
              <button
                key={i.id}
                onClick={() => setStep(i.id)}
                className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  step === i.id ? "bg-blue-50 text-blue-600" : "text-gray-600 hover:bg-gray-50"
                }`}
              >
                <i.icon size={18} />
                {i.label}
              </button>
            ))}
          </nav>

          <div className="mt-8 pt-8 border-t">
             <label className="block text-xs font-semibold text-gray-500 uppercase mb-4">Import Existing</label>
             <div className="relative group">
                <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
                <div className="border-2 border-dashed rounded-lg p-4 text-center group-hover:border-blue-400 transition-colors">
                  <Upload className="mx-auto text-gray-400 mb-2" />
                  <span className="text-xs text-gray-600">Upload PDF/DOCX</span>
                </div>
             </div>
          </div>
        </aside>

        {/* Form Area */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-3xl mx-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {step === 1 && (
                  <section className="space-y-4">
                    <h2 className="text-2xl font-bold">Personal Information</h2>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="col-span-2">
                        <label className="label">Full Name</label>
                        <input
                          type="text"
                          className="input"
                          value={cvData.personal_info.full_name}
                          onChange={e => setCvData({...cvData, personal_info: {...cvData.personal_info, full_name: e.target.value}})}
                        />
                      </div>
                      <div>
                        <label className="label">Email</label>
                        <input type="email" className="input" value={cvData.personal_info.email}
                          onChange={e => setCvData({...cvData, personal_info: {...cvData.personal_info, email: e.target.value}})}
                        />
                      </div>
                      <div>
                        <label className="label">Phone</label>
                        <input type="text" className="input" value={cvData.personal_info.phone}
                          onChange={e => setCvData({...cvData, personal_info: {...cvData.personal_info, phone: e.target.value}})}
                        />
                      </div>
                    </div>
                  </section>
                )}

                {step === 2 && (
                  <section className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h2 className="text-2xl font-bold">Professional Summary</h2>
                      <button
                        onClick={async () => {
                          const enhanced = await handleAIEnhance("summary", cvData.summary || "Professional summary based on my experience");
                          setCvData({...cvData, summary: enhanced});
                        }}
                        className="btn-secondary text-xs flex items-center gap-1"
                      >
                        <Wand2 size={14} /> AI Generate
                      </button>
                    </div>
                    <textarea
                      className="input min-h-[150px]"
                      placeholder="Briefly describe your professional background and goals..."
                      value={cvData.summary}
                      onChange={e => setCvData({...cvData, summary: e.target.value})}
                    ></textarea>
                  </section>
                )}

                {step === 3 && (
                  <section className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h2 className="text-2xl font-bold">Work Experience</h2>
                      <button
                        onClick={() => setCvData({...cvData, work_experience: [...cvData.work_experience, {job_title: "", company: "", description: ""}]})}
                        className="btn-primary text-xs flex items-center gap-1"
                      >
                        <Plus size={14} /> Add Role
                      </button>
                    </div>
                    {cvData.work_experience.map((exp, idx) => (
                      <div key={idx} className="p-4 border rounded-xl space-y-4 relative group">
                        <button
                          onClick={() => {
                            const newExp = [...cvData.work_experience];
                            newExp.splice(idx, 1);
                            setCvData({...cvData, work_experience: newExp});
                          }}
                          className="absolute top-2 right-2 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Trash2 size={18} />
                        </button>
                        <div className="grid grid-cols-2 gap-4">
                          <input
                            placeholder="Job Title" className="input"
                            value={exp.job_title}
                            onChange={e => {
                              const newExp = [...cvData.work_experience];
                              newExp[idx].job_title = e.target.value;
                              setCvData({...cvData, work_experience: newExp});
                            }}
                          />
                          <input
                            placeholder="Company" className="input"
                            value={exp.company}
                            onChange={e => {
                              const newExp = [...cvData.work_experience];
                              newExp[idx].company = e.target.value;
                              setCvData({...cvData, work_experience: newExp});
                            }}
                          />
                          <div className="col-span-2 space-y-2">
                            <div className="flex justify-between items-center">
                              <label className="text-xs font-semibold">Description</label>
                              <button
                                onClick={async () => {
                                  const enhanced = await handleAIEnhance("experience", exp.description);
                                  const newExp = [...cvData.work_experience];
                                  newExp[idx].description = enhanced;
                                  setCvData({...cvData, work_experience: newExp});
                                }}
                                className="text-xs text-blue-600 flex items-center gap-1"
                              >
                                <Wand2 size={12} /> Enhance with AI
                              </button>
                            </div>
                            <textarea
                              className="input min-h-[100px]"
                              value={exp.description}
                              onChange={e => {
                                const newExp = [...cvData.work_experience];
                                newExp[idx].description = e.target.value;
                                setCvData({...cvData, work_experience: newExp});
                              }}
                            ></textarea>
                          </div>
                        </div>
                      </div>
                    ))}
                  </section>
                )}

                {step === 4 && (
                  <section className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h2 className="text-2xl font-bold">Education</h2>
                      <button
                        onClick={() => setCvData({...cvData, education: [...cvData.education, {degree: "", institution: "", year: "", grade: ""}]})}
                        className="btn-primary text-xs flex items-center gap-1"
                      >
                        <Plus size={14} /> Add Education
                      </button>
                    </div>
                    {cvData.education.map((edu, idx) => (
                      <div key={idx} className="p-4 border rounded-xl space-y-4 relative group">
                        <button
                          onClick={() => {
                            const newEdu = [...cvData.education];
                            newEdu.splice(idx, 1);
                            setCvData({...cvData, education: newEdu});
                          }}
                          className="absolute top-2 right-2 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Trash2 size={18} />
                        </button>
                        <div className="grid grid-cols-2 gap-4">
                          <input
                            placeholder="Degree" className="input"
                            value={edu.degree}
                            onChange={e => {
                              const newEdu = [...cvData.education];
                              newEdu[idx].degree = e.target.value;
                              setCvData({...cvData, education: newEdu});
                            }}
                          />
                          <input
                            placeholder="Institution" className="input"
                            value={edu.institution}
                            onChange={e => {
                              const newEdu = [...cvData.education];
                              newEdu[idx].institution = e.target.value;
                              setCvData({...cvData, education: newEdu});
                            }}
                          />
                          <input
                            placeholder="Year" className="input"
                            value={edu.year}
                            onChange={e => {
                              const newEdu = [...cvData.education];
                              newEdu[idx].year = e.target.value;
                              setCvData({...cvData, education: newEdu});
                            }}
                          />
                          <input
                            placeholder="Grade / GPA" className="input"
                            value={edu.grade}
                            onChange={e => {
                              const newEdu = [...cvData.education];
                              newEdu[idx].grade = e.target.value;
                              setCvData({...cvData, education: newEdu});
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </section>
                )}

                {step === 5 && (
                  <section className="space-y-6">
                    <h2 className="text-2xl font-bold">Skills</h2>
                    {["technical", "soft", "languages"].map(cat => (
                      <div key={cat} className="space-y-2">
                        <label className="label capitalize">{cat} Skills</label>
                        <div className="flex flex-wrap gap-2 mb-2">
                          {cvData.skills[cat].map((s, i) => (
                            <span key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                              {s}
                              <X size={14} className="cursor-pointer" onClick={() => {
                                const newSkills = {...cvData.skills};
                                newSkills[cat].splice(i, 1);
                                setCvData({...cvData, skills: newSkills});
                              }} />
                            </span>
                          ))}
                        </div>
                        <input
                          placeholder={`Add ${cat} skill...`}
                          className="input"
                          onKeyDown={e => {
                            if (e.key === 'Enter') {
                              const val = e.target.value.trim();
                              if (val) {
                                const newSkills = {...cvData.skills};
                                newSkills[cat].push(val);
                                setCvData({...cvData, skills: newSkills});
                                e.target.value = "";
                              }
                            }
                          }}
                        />
                      </div>
                    ))}
                  </section>
                )}

                {step === 6 && (
                  <section className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h2 className="text-2xl font-bold">Certifications & Awards</h2>
                      <button
                        onClick={() => setCvData({...cvData, certifications: [...cvData.certifications, {name: "", issuer: "", year: ""}]})}
                        className="btn-primary text-xs flex items-center gap-1"
                      >
                        <Plus size={14} /> Add Item
                      </button>
                    </div>
                    {cvData.certifications.map((cert, idx) => (
                      <div key={idx} className="p-4 border rounded-xl space-y-4 relative group">
                        <button
                          onClick={() => {
                            const newCert = [...cvData.certifications];
                            newCert.splice(idx, 1);
                            setCvData({...cvData, certifications: newCert});
                          }}
                          className="absolute top-2 right-2 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <Trash2 size={18} />
                        </button>
                        <div className="grid grid-cols-3 gap-4">
                          <input
                            placeholder="Name" className="input col-span-2"
                            value={cert.name}
                            onChange={e => {
                              const newCert = [...cvData.certifications];
                              newCert[idx].name = e.target.value;
                              setCvData({...cvData, certifications: newCert});
                            }}
                          />
                          <input
                            placeholder="Year" className="input"
                            value={cert.year}
                            onChange={e => {
                              const newCert = [...cvData.certifications];
                              newCert[idx].year = e.target.value;
                              setCvData({...cvData, certifications: newCert});
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </section>
                )}

                {step === 7 && (
                  <section className="space-y-6">
                    <h2 className="text-2xl font-bold">Select Template</h2>
                    <div className="grid grid-cols-3 gap-6">
                      {["Modern", "Classic", "ATS-Friendly"].map(t => (
                        <div
                          key={t}
                          onClick={() => setCvData({...cvData, template_name: t})}
                          className={`cursor-pointer border-2 rounded-xl p-4 text-center transition-all ${
                            cvData.template_name === t ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:border-gray-300"
                          }`}
                        >
                          <div className="bg-gray-200 aspect-[1/1.414] rounded mb-3"></div>
                          <span className="font-semibold">{t}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                <div className="pt-8 flex justify-between border-t mt-12">
                  <button onClick={prevStep} disabled={step === 1} className="btn-secondary flex items-center gap-2">
                    <ChevronLeft size={18} /> Previous
                  </button>
                  <button onClick={nextStep} className="btn-primary flex items-center gap-2">
                    {step === 7 ? "Finish" : "Next Step"} <ChevronRight size={18} />
                  </button>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        {/* Live Preview */}
        <aside className="w-[400px] bg-gray-200 p-6 hidden lg:block overflow-y-auto">
          <div className="sticky top-0 bg-white shadow-2xl rounded-sm aspect-[1/1.414] p-8 origin-top scale-90">
             {/* Mock Live Preview Render */}
             <div className="text-center border-b pb-4 mb-4">
                <h1 className="text-xl font-bold uppercase tracking-widest">{cvData.personal_info.full_name || "Your Name"}</h1>
                <p className="text-[10px] text-gray-500">{cvData.personal_info.email} | {cvData.personal_info.phone}</p>
             </div>
             <div className="space-y-4">
                <section>
                   <h2 className="text-xs font-bold border-b mb-1">SUMMARY</h2>
                   <p className="text-[9px] text-gray-700 leading-relaxed">{cvData.summary}</p>
                </section>
                <section>
                   <h2 className="text-xs font-bold border-b mb-1">EXPERIENCE</h2>
                   {cvData.work_experience.map((e, i) => (
                     <div key={i} className="mb-2">
                        <div className="flex justify-between font-bold text-[9px]">
                           <span>{e.job_title}</span>
                           <span>{e.company}</span>
                        </div>
                        <p className="text-[8px] text-gray-600 mt-0.5">{e.description}</p>
                     </div>
                   ))}
                </section>
             </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
