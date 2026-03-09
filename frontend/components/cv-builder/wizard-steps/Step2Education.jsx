/**
 * Step 2: Education
 * Collects degree, field of study, institution, dates
 * Triggers industry detection
 */
import { useState, useEffect } from "react";
import WizardNavigation from "../wizard-components/WizardNavigation";
import AISuggestionBox from "../wizard-components/AISuggestionBox";
import { GraduationCap, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

export default function Step2Education({ data, onUpdate, onNext, onBack, previousData }) {
  const [formData, setFormData] = useState({
    degree: data?.degree || "",
    field_of_study: data?.field_of_study || "",
    institution: data?.institution || "",
    start_date: data?.start_date || "",
    end_date: data?.end_date || "",
    gpa: data?.gpa || "",
    honors: data?.honors || "",
  });

  const [industry, setIndustry] = useState(data?.detected_industry || null);
  const [industryInsights, setIndustryInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Auto-detect industry when field of study changes
    if (formData.field_of_study && formData.field_of_study.length > 3) {
      detectIndustry();
    }
  }, [formData.field_of_study]);

  const detectIndustry = async () => {
    if (!formData.field_of_study) return;

    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://192.168.100.93:8000";
      const response = await fetch(`${apiUrl}/api/cv/wizard/step/2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: formData,
          previous_data: previousData || {},
        }),
      });

      const result = await response.json();
      if (result.success) {
        setIndustry(result.industry);
        setIndustryInsights(result.industry_insights);
        const updated = { ...formData, detected_industry: result.industry };
        setFormData(updated);
        onUpdate(updated);
      }
    } catch (error) {
      console.error("Error detecting industry:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    const updated = { ...formData, [field]: value };
    setFormData(updated);
    onUpdate(updated);
  };

  const canProceed =
    formData.degree && formData.field_of_study && formData.institution;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Education</h2>
        <p className="text-gray-600 mb-6">
          Tell us about your educational background
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Degree Type <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.degree}
            onChange={(e) => handleChange("degree", e.target.value)}
            className="input-field w-full"
            required
          >
            <option value="">Select degree</option>
            <option value="High School">High School</option>
            <option value="Associate's">Associate's</option>
            <option value="Bachelor's">Bachelor's</option>
            <option value="Master's">Master's</option>
            <option value="PhD">PhD</option>
            <option value="Certificate">Certificate</option>
            <option value="Diploma">Diploma</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Field of Study <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.field_of_study}
            onChange={(e) => handleChange("field_of_study", e.target.value)}
            className="input-field w-full"
            placeholder="e.g., Computer Science, Business Administration"
            required
          />
          {loading && (
            <div className="mt-2 flex items-center gap-2 text-sm text-sky-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Detecting industry...</span>
            </div>
          )}
          {industry && !loading && (
            <div className="mt-2 flex items-center gap-2 text-sm text-sky-600">
              <GraduationCap className="w-4 h-4" />
              <span>Detected industry: <strong>{industry}</strong></span>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Institution <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.institution}
            onChange={(e) => handleChange("institution", e.target.value)}
            className="input-field w-full"
            placeholder="University Name"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="month"
              value={formData.start_date}
              onChange={(e) => handleChange("start_date", e.target.value)}
              className="input-field w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="month"
              value={formData.end_date}
              onChange={(e) => handleChange("end_date", e.target.value)}
              className="input-field w-full"
              placeholder="Leave empty if current"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            GPA (Optional)
          </label>
          <input
            type="text"
            value={formData.gpa}
            onChange={(e) => handleChange("gpa", e.target.value)}
            className="input-field w-full"
            placeholder="e.g., 3.8/4.0"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Honors/Awards (Optional)
          </label>
          <input
            type="text"
            value={formData.honors}
            onChange={(e) => handleChange("honors", e.target.value)}
            className="input-field w-full"
            placeholder="e.g., Summa Cum Laude, Dean's List"
          />
        </div>
      </div>

      {industryInsights && industryInsights.recommendations && (
        <AISuggestionBox
          suggestions={industryInsights.recommendations}
          title={`Industry Insights for ${industry}`}
          emptyMessage="No recommendations available"
        />
      )}

      <WizardNavigation
        currentStep={2}
        totalSteps={6}
        onBack={onBack}
        onNext={onNext}
        canProceed={canProceed}
        nextLabel="Continue to Experience"
      />
    </div>
  );
}
