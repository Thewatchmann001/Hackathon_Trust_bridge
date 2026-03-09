/**
 * Step 1: Basic Info
 * Collects name, email, phone, location, LinkedIn, portfolio
 */
import { useState } from "react";
import WizardNavigation from "../wizard-components/WizardNavigation";

export default function Step1BasicInfo({ data, onUpdate, onNext, onBack }) {
  const [formData, setFormData] = useState({
    full_name: data?.full_name || "",
    email: data?.email || "",
    phone: data?.phone || "",
    location: data?.location || "",
    linkedin: data?.linkedin || "",
    portfolio: data?.portfolio || "",
  });

  const handleChange = (field, value) => {
    const updated = { ...formData, [field]: value };
    setFormData(updated);
    onUpdate(updated);
  };

  const canProceed = formData.full_name && formData.email;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Basic Information</h2>
        <p className="text-gray-600 mb-6">
          Let's start with your basic contact information
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Full Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => handleChange("full_name", e.target.value)}
            className="input-field w-full"
            placeholder="John Doe"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            className="input-field w-full"
            placeholder="john.doe@email.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Phone
          </label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => handleChange("phone", e.target.value)}
            className="input-field w-full"
            placeholder="+1 (555) 123-4567"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => handleChange("location", e.target.value)}
            className="input-field w-full"
            placeholder="City, Country or Remote"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            LinkedIn URL (Optional)
          </label>
          <input
            type="url"
            value={formData.linkedin}
            onChange={(e) => handleChange("linkedin", e.target.value)}
            className="input-field w-full"
            placeholder="https://linkedin.com/in/yourprofile"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Portfolio URL (Optional)
          </label>
          <input
            type="url"
            value={formData.portfolio}
            onChange={(e) => handleChange("portfolio", e.target.value)}
            className="input-field w-full"
            placeholder="https://yourportfolio.com"
          />
        </div>
      </div>

      <WizardNavigation
        currentStep={1}
        totalSteps={6}
        onBack={onBack}
        onNext={onNext}
        canProceed={canProceed}
        nextLabel="Continue to Education"
      />
    </div>
  );
}
