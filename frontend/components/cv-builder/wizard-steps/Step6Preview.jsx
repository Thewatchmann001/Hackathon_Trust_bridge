/**
 * Step 6: Preview & Download
 * Final CV preview with export options
 */
import { useState } from "react";
import WizardNavigation from "../wizard-components/WizardNavigation";
import { Download, FileText, File, Loader2, Edit2 } from "lucide-react";
import toast from "react-hot-toast";

export default function Step6Preview({
  data,
  onUpdate,
  onBack,
  onComplete,
  allStepsData,
  userId,
}) {
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState({ pdf: false, docx: false });

  const handleSave = async () => {
    setSaving(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://192.168.100.93:8000";
      const response = await fetch(`${apiUrl}/api/cv/wizard/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          steps: allStepsData,
        }),
      });

      const result = await response.json();
      if (result.success) {
        toast.success("CV saved successfully!");
        onComplete && onComplete(result.cv_data);
      } else {
        toast.error("Failed to save CV");
      }
    } catch (error) {
      console.error("Error saving CV:", error);
      toast.error("Error saving CV");
    } finally {
      setSaving(false);
    }
  };

  // Transform wizard data into format expected by export functions
  const transformWizardDataToCVFormat = () => {
    const step1 = allStepsData?.step1 || {};
    const step2 = allStepsData?.step2 || {};
    const step3 = allStepsData?.step3 || {};
    const step4 = allStepsData?.step4 || {};
    const step5 = allStepsData?.step5 || {};

    // Format experience
    const experience = (step3.experience || []).map((exp) => ({
      job_title: exp.job_title || "",
      company: exp.company || "",
      start_date: exp.start_date || "",
      end_date: exp.end_date || "Present",
      description: exp.description || "",
    }));

    // Format education
    const education = step2.degree
      ? [
          {
            degree: step2.degree || "",
            field_of_study: step2.field_of_study || "",
            institution: step2.institution || "",
            start_date: step2.start_date || "",
            end_date: step2.end_date || "Present",
            gpa: step2.gpa || "",
            honors: step2.honors || "",
          },
        ]
      : [];

    // Format skills - use the already-categorized skills from step4.skills
    // Step4Skills categorizes skills into technical, tools, soft, and other
    let skills = step4.skills || {};
    
    // If skills object is empty, try to get from recommendations or fallback to selected_skills
    if ((!skills.technical && !skills.tools && !skills.soft && !skills.other) && step4.selected_skills && step4.selected_skills.length > 0) {
      // Try to get recommendations to categorize properly
      const recommendedSkills = step4.recommendations?.recommended_skills?.recommended || {
        technical: [],
        soft: [],
        tools: [],
      };
      
      // Categorize based on recommendations
      skills = {
        technical: step4.selected_skills.filter((s) => recommendedSkills.technical.includes(s)),
        tools: step4.selected_skills.filter((s) => recommendedSkills.tools.includes(s)),
        soft: step4.selected_skills.filter((s) => recommendedSkills.soft.includes(s)),
        other: step4.selected_skills.filter(
          (s) =>
            !recommendedSkills.technical.includes(s) &&
            !recommendedSkills.soft.includes(s) &&
            !recommendedSkills.tools.includes(s)
        ),
      };
    }
    
    // Now use the properly categorized skills
    const technicalSkills = skills.technical || [];
    const toolSkills = skills.tools || [];
    const softSkills = skills.soft || [];
    const otherSkills = skills.other || [];
    
    // Map to export format - each skill appears in only ONE category
    const exportSkills = {
      // Technical skills (job-related, domain-specific) - technical + other custom skills
      job_related_skills: [...technicalSkills, ...otherSkills],
      technical_skills: [...technicalSkills, ...otherSkills],
      technical: [...technicalSkills, ...otherSkills],
      // Tools/programming (separate from technical to avoid duplication)
      computer_skills: toolSkills,
      programming_skills: toolSkills,
      // Soft skills (separate)
      soft: softSkills,
      social_skills: softSkills,
      languages: [],
    };

    // Build CV data in expected format
    return {
      personal_info: {
        full_name: step1.full_name || "",
        email: step1.email || "",
        phone: step1.phone || "",
        location: step1.location || "",
        linkedin: step1.linkedin || "",
        portfolio: step1.portfolio || "",
      },
      summary: step5.summary || "",
      experience: experience,
      education: education,
      skills: exportSkills,
      personal_skills: exportSkills,
      json_content: {
        personal_info: {
          full_name: step1.full_name || "",
          email: step1.email || "",
          phone: step1.phone || "",
          location: step1.location || "",
          linkedin: step1.linkedin || "",
          portfolio: step1.portfolio || "",
        },
        summary: step5.summary || "",
        experience: experience,
        education: education,
        skills: exportSkills,
        personal_skills: exportSkills, // Also include as personal_skills for compatibility
      },
    };
  };

  const handleExport = async (format) => {
    setExporting({ ...exporting, [format]: true });
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://192.168.100.93:8000";
      const endpoint =
        format === "pdf"
          ? `${apiUrl}/api/cv/export-pdf`
          : `${apiUrl}/api/cv/export-docx`;

      // Transform wizard data to CV format
      const cvData = transformWizardDataToCVFormat();

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          cv_data: cvData,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `CV.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success(`CV exported as ${format.toUpperCase()}!`);
      } else {
        toast.error(`Failed to export as ${format.toUpperCase()}`);
      }
    } catch (error) {
      console.error(`Error exporting ${format}:`, error);
      toast.error(`Error exporting ${format.toUpperCase()}`);
    } finally {
      setExporting({ ...exporting, [format]: false });
    }
  };

  const step1 = allStepsData?.step1 || {};
  const step2 = allStepsData?.step2 || {};
  const step3 = allStepsData?.step3 || {};
  const step4 = allStepsData?.step4 || {};
  const step5 = allStepsData?.step5 || {};

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Preview Your CV</h2>
        <p className="text-gray-600 mb-6">
          Review your CV and download it when ready.
        </p>
      </div>

      {/* CV Preview */}
      <div className="card p-8 bg-white">
        <div className="space-y-6">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4">
            <h1 className="text-3xl font-bold text-gray-900">
              {step1.full_name || "Your Name"}
            </h1>
            <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
              {step1.email && <span>{step1.email}</span>}
              {step1.phone && <span>{step1.phone}</span>}
              {step1.location && <span>{step1.location}</span>}
              {step1.linkedin && (
                <a href={step1.linkedin} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline">
                  LinkedIn
                </a>
              )}
              {step1.portfolio && (
                <a href={step1.portfolio} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline">
                  Portfolio
                </a>
              )}
            </div>
          </div>

          {/* Summary */}
          {step5.summary && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">Professional Summary</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{step5.summary}</p>
            </div>
          )}

          {/* Experience */}
          {step3.experience && step3.experience.length > 0 && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-3">Experience</h2>
              <div className="space-y-4">
                {step3.experience.map((exp, idx) => (
                  <div key={idx} className="border-l-4 border-sky-500 pl-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {exp.job_title} at {exp.company}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">
                      {exp.start_date} - {exp.end_date || "Present"}
                    </p>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {exp.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {step2.degree && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-3">Education</h2>
              <div className="border-l-4 border-violet-500 pl-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {step2.degree} in {step2.field_of_study}
                </h3>
                <p className="text-gray-700">{step2.institution}</p>
                <p className="text-sm text-gray-600">
                  {step2.start_date} - {step2.end_date || "Present"}
                </p>
                {step2.gpa && <p className="text-sm text-gray-600">GPA: {step2.gpa}</p>}
              </div>
            </div>
          )}

          {/* Skills */}
          {step4.selected_skills && step4.selected_skills.length > 0 && (
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-3">Skills</h2>
              <div className="flex flex-wrap gap-2">
                {step4.selected_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-4">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center gap-2"
        >
          {saving ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              Save CV
            </>
          )}
        </button>
        <button
          onClick={() => handleExport("pdf")}
          disabled={exporting.pdf}
          className="btn-secondary flex items-center gap-2"
        >
          {exporting.pdf ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              Download PDF
            </>
          )}
        </button>
        <button
          onClick={() => handleExport("docx")}
          disabled={exporting.docx}
          className="btn-secondary flex items-center gap-2"
        >
          {exporting.docx ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <File className="w-5 h-5" />
              Download Word
            </>
          )}
        </button>
      </div>

      <WizardNavigation
        currentStep={6}
        totalSteps={6}
        onBack={onBack}
        onComplete={handleSave}
        canProceed={true}
        loading={saving}
        completeLabel="Save & Complete"
      />
    </div>
  );
}
