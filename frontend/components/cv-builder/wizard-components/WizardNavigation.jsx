/**
 * Wizard Navigation Buttons
 * Next/Back buttons with validation
 */
import { ChevronLeft, ChevronRight, Check } from "lucide-react";

export default function WizardNavigation({
  currentStep,
  totalSteps,
  onBack,
  onNext,
  onComplete,
  canProceed = true,
  loading = false,
  backLabel = "Back",
  nextLabel = "Next",
  completeLabel = "Complete",
}) {
  const isFirstStep = currentStep === 1;
  const isLastStep = currentStep === totalSteps;

  return (
    <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
      <button
        onClick={onBack}
        disabled={isFirstStep || loading}
        className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <ChevronLeft className="w-4 h-4" />
        {backLabel}
      </button>
      {isLastStep ? (
        <button
          onClick={onComplete}
          disabled={!canProceed || loading}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Processing..." : completeLabel}
          {!loading && <Check className="w-4 h-4" />}
        </button>
      ) : (
        <button
          onClick={onNext}
          disabled={!canProceed || loading}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Loading..." : nextLabel}
          {!loading && <ChevronRight className="w-4 h-4" />}
        </button>
      )}
    </div>
  );
}
