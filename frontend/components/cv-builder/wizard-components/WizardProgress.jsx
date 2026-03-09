/**
 * Wizard Progress Indicator
 * Shows current step and progress
 */
import { Check } from "lucide-react";

const STEPS = [
  { id: 1, title: "Basic Info", icon: "👤" },
  { id: 2, title: "Education", icon: "🎓" },
  { id: 3, title: "Experience", icon: "💼" },
  { id: 4, title: "Skills", icon: "⭐" },
  { id: 5, title: "Summary", icon: "📝" },
  { id: 6, title: "Preview", icon: "👁️" },
];

export default function WizardProgress({ currentStep, totalSteps = 6 }) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {STEPS.map((step, idx) => {
          const isActive = currentStep === step.id;
          const isCompleted = currentStep > step.id;
          const isUpcoming = currentStep < step.id;

          return (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all text-lg ${
                    isActive
                      ? "bg-gradient-to-r from-sky-500 to-violet-500 text-white shadow-lg scale-110"
                      : isCompleted
                      ? "bg-green-500 text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <span>{step.icon}</span>
                  )}
                </div>
                <span
                  className={`text-xs mt-2 text-center font-medium ${
                    isActive ? "text-sky-600" : isCompleted ? "text-green-600" : "text-gray-500"
                  }`}
                >
                  {step.title}
                </span>
              </div>
              {idx < STEPS.length - 1 && (
                <div
                  className={`h-1 flex-1 mx-2 transition-all ${
                    isCompleted ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
      <div className="text-center text-sm text-gray-600">
        Step {currentStep} of {totalSteps}
      </div>
    </div>
  );
}
