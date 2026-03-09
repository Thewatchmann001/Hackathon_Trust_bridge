/**
 * Step 4: Skills
 * AI-suggested skills based on field of study
 */
import { useState, useEffect } from "react";
import WizardNavigation from "../wizard-components/WizardNavigation";
import AISuggestionBox from "../wizard-components/AISuggestionBox";
import { Sparkles, Loader2, X } from "lucide-react";
import toast from "react-hot-toast";

export default function Step4Skills({ data, onUpdate, onNext, onBack, previousData }) {
  const [selectedSkills, setSelectedSkills] = useState(data?.selected_skills || []);
  const [recommendedSkills, setRecommendedSkills] = useState({
    technical: [],
    soft: [],
    tools: [],
  });
  const [loading, setLoading] = useState(false);
  const [customSkill, setCustomSkill] = useState("");

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://192.168.100.93:8000";
      const field_of_study = previousData?.step2?.field_of_study || "";
      const experience = previousData?.step3?.experience || [];
      const industry = previousData?.step2?.detected_industry || "";

      const response = await fetch(`${apiUrl}/api/cv/wizard/skills/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          field_of_study: field_of_study,
          experience: experience,
          industry: industry,
          selected_skills: selectedSkills,
        }),
      });

      const result = await response.json();
      if (result.success && result.recommended_skills) {
        setRecommendedSkills(result.recommended_skills.recommended || {
          technical: [],
          soft: [],
          tools: [],
        });
      }
    } catch (error) {
      console.error("Error loading recommendations:", error);
      toast.error("Failed to load skill recommendations");
    } finally {
      setLoading(false);
    }
  };

  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter((s) => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const addCustomSkill = () => {
    if (customSkill.trim() && !selectedSkills.includes(customSkill.trim())) {
      setSelectedSkills([...selectedSkills, customSkill.trim()]);
      setCustomSkill("");
      toast.success("Skill added");
    }
  };

  const removeSkill = (skill) => {
    setSelectedSkills(selectedSkills.filter((s) => s !== skill));
  };

  useEffect(() => {
    // Update parent with selected skills - properly categorize into technical, tools, soft, and other
    const skillsObj = {
      technical: selectedSkills.filter((s) => recommendedSkills.technical.includes(s)),
      tools: selectedSkills.filter((s) => recommendedSkills.tools.includes(s)),
      soft: selectedSkills.filter((s) => recommendedSkills.soft.includes(s)),
      other: selectedSkills.filter(
        (s) =>
          !recommendedSkills.technical.includes(s) &&
          !recommendedSkills.soft.includes(s) &&
          !recommendedSkills.tools.includes(s)
      ),
    };
    onUpdate({ selected_skills: selectedSkills, skills: skillsObj });
  }, [selectedSkills]);

  const canProceed = selectedSkills.length >= 3;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Skills</h2>
        <p className="text-gray-600 mb-6">
          Select your skills. We've suggested some based on your education and experience.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-sky-600" />
          <span className="ml-2 text-gray-600">Loading recommendations...</span>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Technical Skills */}
          {recommendedSkills.technical.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Technical Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {recommendedSkills.technical.map((skill) => (
                  <button
                    key={skill}
                    onClick={() => toggleSkill(skill)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      selectedSkills.includes(skill)
                        ? "bg-sky-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {skill}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Soft Skills */}
          {recommendedSkills.soft.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Soft Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {recommendedSkills.soft.map((skill) => (
                  <button
                    key={skill}
                    onClick={() => toggleSkill(skill)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      selectedSkills.includes(skill)
                        ? "bg-violet-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {skill}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Tools */}
          {recommendedSkills.tools.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Tools</h3>
              <div className="flex flex-wrap gap-2">
                {recommendedSkills.tools.map((skill) => (
                  <button
                    key={skill}
                    onClick={() => toggleSkill(skill)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      selectedSkills.includes(skill)
                        ? "bg-green-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {skill}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Custom Skill Input */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Add Custom Skill
            </h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={customSkill}
                onChange={(e) => setCustomSkill(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addCustomSkill()}
                className="input-field flex-1"
                placeholder="Type a skill and press Enter"
              />
              <button onClick={addCustomSkill} className="btn-primary">
                Add
              </button>
            </div>
          </div>

          {/* Selected Skills */}
          {selectedSkills.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Selected Skills ({selectedSkills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedSkills.map((skill) => (
                  <span
                    key={skill}
                    className="px-4 py-2 bg-sky-100 text-sky-800 rounded-full text-sm font-medium flex items-center gap-2"
                  >
                    {skill}
                    <button
                      onClick={() => removeSkill(skill)}
                      className="text-sky-600 hover:text-sky-800"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <WizardNavigation
        currentStep={4}
        totalSteps={6}
        onBack={onBack}
        onNext={onNext}
        canProceed={canProceed}
        nextLabel="Continue to Summary"
      />
    </div>
  );
}
