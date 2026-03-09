/**
 * Step 5: Professional Summary
 * AI-generated professional summary
 */
import { useState, useEffect } from "react";
import WizardNavigation from "../wizard-components/WizardNavigation";
import AISuggestionBox from "../wizard-components/AISuggestionBox";
import { Sparkles, Loader2, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";

export default function Step5Summary({ data, onUpdate, onNext, onBack, previousData }) {
  const [summary, setSummary] = useState(data?.summary || "");
  const [variations, setVariations] = useState(data?.summary_variations || []);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!summary && previousData) {
      generateSummary();
    }
  }, []);

  const generateSummary = async () => {
    setGenerating(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://192.168.100.93:8000";
      const basic_info = previousData?.step1 || {};
      const education = previousData?.step2
        ? [previousData.step2]
        : [];
      const experience = previousData?.step3?.experience || [];
      const skills = previousData?.step4?.skills || {};
      const industry = previousData?.step2?.detected_industry;

      const response = await fetch(`${apiUrl}/api/cv/wizard/summary/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          basic_info: basic_info,
          education: education,
          experience: experience,
          skills: skills,
          industry: industry,
        }),
      });

      const result = await response.json();
      if (result.success) {
        setSummary(result.summary);
        setVariations(result.variations || []);
        onUpdate({ summary: result.summary, summary_variations: result.variations });
        toast.success("Summary generated!");
      } else {
        toast.error("Failed to generate summary");
      }
    } catch (error) {
      console.error("Error generating summary:", error);
      toast.error("Error generating summary");
    } finally {
      setGenerating(false);
    }
  };

  const selectVariation = (variation) => {
    setSummary(variation);
    onUpdate({ summary: variation });
    toast.success("Summary updated");
  };

  const handleChange = (value) => {
    setSummary(value);
    onUpdate({ summary: value });
  };

  const canProceed = summary && summary.trim().length >= 50;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Professional Summary</h2>
        <p className="text-gray-600 mb-6">
          Your professional summary. We've generated one for you, but you can edit it or choose a variation.
        </p>
      </div>

      {generating ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-sky-600" />
          <span className="ml-2 text-gray-600">Generating summary...</span>
        </div>
      ) : (
        <div className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-semibold text-gray-700">
                Summary <span className="text-red-500">*</span>
              </label>
              <button
                onClick={generateSummary}
                className="btn-secondary flex items-center gap-2 text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                Regenerate
              </button>
            </div>
            <textarea
              value={summary}
              onChange={(e) => handleChange(e.target.value)}
              className="input-field w-full min-h-[150px]"
              placeholder="Your professional summary will appear here..."
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {summary.length} characters (minimum 50)
            </p>
          </div>

          {variations && variations.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Alternative Versions
              </h3>
              <AISuggestionBox
                suggestions={variations}
                title="Choose a different version"
                onSelect={selectVariation}
                emptyMessage="No variations available"
              />
            </div>
          )}
        </div>
      )}

      <WizardNavigation
        currentStep={5}
        totalSteps={6}
        onBack={onBack}
        onNext={onNext}
        canProceed={canProceed}
        nextLabel="Continue to Preview"
      />
    </div>
  );
}
