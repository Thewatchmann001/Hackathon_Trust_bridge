/**
 * Step 3: Experience
 * Collects work experience with AI enhancement
 */
import { useState } from "react";
import WizardNavigation from "../wizard-components/WizardNavigation";
import { Plus, Trash2, Sparkles, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

export default function Step3Experience({ data, onUpdate, onNext, onBack, previousData }) {
  const [experience, setExperience] = useState(
    data?.experience || [
      {
        job_title: "",
        company: "",
        start_date: "",
        end_date: "",
        description: "",
        enhanced_bullets: [],
      },
    ]
  );
  const [enhancing, setEnhancing] = useState({});

  const addExperience = () => {
    setExperience([
      ...experience,
      {
        job_title: "",
        company: "",
        start_date: "",
        end_date: "",
        description: "",
        enhanced_bullets: [],
      },
    ]);
  };

  const removeExperience = (index) => {
    const updated = experience.filter((_, i) => i !== index);
    setExperience(updated);
    onUpdate({ experience: updated });
  };

  const updateExperience = (index, field, value) => {
    const updated = [...experience];
    updated[index] = { ...updated[index], [field]: value };
    setExperience(updated);
    onUpdate({ experience: updated });
  };

  const enhanceDescription = async (index) => {
    const exp = experience[index];
    if (!exp.job_title || !exp.company || !exp.description) {
      toast.error("Please fill in job title, company, and description first");
      return;
    }

    setEnhancing({ ...enhancing, [index]: true });
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://192.168.100.93:8000";
      const industry = previousData?.step2?.detected_industry;
      const response = await fetch(`${apiUrl}/api/cv/wizard/experience/enhance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: exp.job_title,
          company: exp.company,
          description: exp.description,
          industry: industry,
        }),
      });

      const result = await response.json();
      if (result.success && result.enhanced_bullets) {
        updateExperience(index, "enhanced_bullets", result.enhanced_bullets);
        toast.success("Experience enhanced!");
      } else {
        toast.error("Failed to enhance experience");
      }
    } catch (error) {
      console.error("Error enhancing experience:", error);
      toast.error("Error enhancing experience");
    } finally {
      setEnhancing({ ...enhancing, [index]: false });
    }
  };

  const useEnhanced = (index) => {
    const exp = experience[index];
    if (exp.enhanced_bullets && exp.enhanced_bullets.length > 0) {
      updateExperience(index, "description", exp.enhanced_bullets.join("\n"));
      updateExperience(index, "enhanced_bullets", []);
      toast.success("Using enhanced description");
    }
  };

  const canProceed = experience.some(
    (exp) => exp.job_title && exp.company && exp.description
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Work Experience</h2>
        <p className="text-gray-600 mb-6">
          Add your work experience. Our AI will help enhance your descriptions.
        </p>
      </div>

      <div className="space-y-6">
        {experience.map((exp, index) => (
          <div key={index} className="card p-6 border-2 border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Experience #{index + 1}
              </h3>
              {experience.length > 1 && (
                <button
                  onClick={() => removeExperience(index)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              )}
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Job Title <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={exp.job_title}
                    onChange={(e) =>
                      updateExperience(index, "job_title", e.target.value)
                    }
                    className="input-field w-full"
                    placeholder="e.g., Software Developer"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Company <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={exp.company}
                    onChange={(e) =>
                      updateExperience(index, "company", e.target.value)
                    }
                    className="input-field w-full"
                    placeholder="Company Name"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="month"
                    value={exp.start_date}
                    onChange={(e) =>
                      updateExperience(index, "start_date", e.target.value)
                    }
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="month"
                    value={exp.end_date}
                    onChange={(e) =>
                      updateExperience(index, "end_date", e.target.value)
                    }
                    className="input-field w-full"
                    placeholder="Leave empty if current"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={exp.description}
                  onChange={(e) =>
                    updateExperience(index, "description", e.target.value)
                  }
                  className="input-field w-full min-h-[100px]"
                  placeholder="Describe your responsibilities and achievements..."
                />
                {exp.description && (
                  <button
                    onClick={() => enhanceDescription(index)}
                    disabled={enhancing[index]}
                    className="mt-2 btn-secondary flex items-center gap-2 text-sm"
                  >
                    {enhancing[index] ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Enhancing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Enhance with AI
                      </>
                    )}
                  </button>
                )}
              </div>

              {exp.enhanced_bullets && exp.enhanced_bullets.length > 0 && (
                <div className="bg-gradient-to-r from-sky-50 to-violet-50 rounded-lg p-4 border border-sky-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-sky-900">
                      AI-Enhanced Description
                    </h4>
                    <button
                      onClick={() => useEnhanced(index)}
                      className="text-sm text-sky-600 hover:text-sky-700 font-medium"
                    >
                      Use This
                    </button>
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                    {exp.enhanced_bullets.map((bullet, idx) => (
                      <li key={idx}>{bullet}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        <button
          onClick={addExperience}
          className="btn-secondary flex items-center gap-2 w-full"
        >
          <Plus className="w-5 h-5" />
          Add Another Experience
        </button>
      </div>

      <WizardNavigation
        currentStep={3}
        totalSteps={6}
        onBack={onBack}
        onNext={onNext}
        canProceed={canProceed}
        nextLabel="Continue to Skills"
      />
    </div>
  );
}
