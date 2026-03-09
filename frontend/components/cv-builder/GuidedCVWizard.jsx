/**
 * Guided CV Creation Wizard
 * Main container for the step-by-step CV creation flow
 */
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import WizardProgress from "./wizard-components/WizardProgress";
import Step1BasicInfo from "./wizard-steps/Step1BasicInfo";
import Step2Education from "./wizard-steps/Step2Education";
import Step3Experience from "./wizard-steps/Step3Experience";
import Step4Skills from "./wizard-steps/Step4Skills";
import Step5Summary from "./wizard-steps/Step5Summary";
import Step6Preview from "./wizard-steps/Step6Preview";
import toast from "react-hot-toast";

export default function GuidedCVWizard({ onComplete, onCancel, userId }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [stepsData, setStepsData] = useState({
    step1: {},
    step2: {},
    step3: {},
    step4: {},
    step5: {},
  });

  const updateStepData = (stepNumber, data) => {
    setStepsData((prev) => ({
      ...prev,
      [`step${stepNumber}`]: { ...prev[`step${stepNumber}`], ...data },
    }));
  };

  const handleNext = () => {
    if (currentStep < 6) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = (cvData) => {
    if (onComplete) {
      onComplete(cvData);
    }
  };

  const renderStep = () => {
    const stepProps = {
      data: stepsData[`step${currentStep}`],
      onUpdate: (data) => updateStepData(currentStep, data),
      onNext: handleNext,
      onBack: handleBack,
      previousData: stepsData,
      allStepsData: stepsData,
      userId: userId,
    };

    switch (currentStep) {
      case 1:
        return <Step1BasicInfo {...stepProps} />;
      case 2:
        return <Step2Education {...stepProps} />;
      case 3:
        return <Step3Experience {...stepProps} />;
      case 4:
        return <Step4Skills {...stepProps} />;
      case 5:
        return <Step5Summary {...stepProps} />;
      case 6:
        return <Step6Preview {...stepProps} onComplete={handleComplete} />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Indicator */}
      <WizardProgress currentStep={currentStep} totalSteps={6} />

      {/* Step Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="card"
        >
          {renderStep()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
