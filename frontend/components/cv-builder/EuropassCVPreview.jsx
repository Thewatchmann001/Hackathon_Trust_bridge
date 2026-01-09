/**
 * Europass-Style CV Preview Component
 * Displays CV in Europass format with inline editing
 */
import { useState } from "react";
import { Edit2, Save, X, Check } from "lucide-react";
import toast from "react-hot-toast";

export default function EuropassCVPreview({ cvData, onUpdate, onSave }) {
  const [editingField, setEditingField] = useState(null);
  const [editValue, setEditValue] = useState("");

  const startEditing = (field, currentValue) => {
    setEditingField(field);
    setEditValue(currentValue || "");
  };

  const saveEdit = () => {
    if (!editingField) return;
    
    // Update CV data based on field path
    const fieldParts = editingField.split(".");
    const updatedData = { ...cvData };
    
    let target = updatedData;
    for (let i = 0; i < fieldParts.length - 1; i++) {
      if (!target[fieldParts[i]]) {
        target[fieldParts[i]] = {};
      }
      target = target[fieldParts[i]];
    }
    
    target[fieldParts[fieldParts.length - 1]] = editValue;
    
    onUpdate(updatedData);
    setEditingField(null);
    toast.success("Updated!");
  };

  const cancelEdit = () => {
    setEditingField(null);
    setEditValue("");
  };

  const EditableField = ({ field, value, type = "text", className = "" }) => {
    const isEditing = editingField === field;
    
    if (isEditing) {
      return (
        <div className="flex items-center gap-2">
          {type === "textarea" ? (
            <textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className={"flex-1 input-field " + (className || "")}
              rows={3}
              autoFocus
            />
          ) : (
            <input
              type={type}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className={"flex-1 input-field " + (className || "")}
              autoFocus
            />
          )}
          <button
            onClick={saveEdit}
            className="p-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            <Check className="w-4 h-4" />
          </button>
          <button
            onClick={cancelEdit}
            className="p-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      );
    }
    
    return (
      <div className="group flex items-center gap-2">
        <span className={className}>{value || <span className="text-gray-400 italic">Not provided</span>}</span>
        <button
          onClick={() => startEditing(field, value)}
          className="opacity-0 group-hover:opacity-100 p-1 text-blue-600 hover:text-blue-800 transition-opacity"
        >
          <Edit2 className="w-4 h-4" />
        </button>
      </div>
    );
  };

  if (!cvData) {
    return (
      <div className="card p-6 text-center">
        <p className="text-gray-600">No CV data to preview. Please create a CV first.</p>
      </div>
    );
  }

  const personalInfo = cvData.personal_info || {};
  const experience = cvData.experience || [];
  const education = cvData.education || [];
  const skills = cvData.skills || { technical: [], soft: [], languages: [] };

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Europass Header */}
      <div className="bg-blue-600 text-white p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              <EditableField
                field="personal_info.first_name"
                value={personalInfo.first_name}
                className="text-white bg-transparent border-none"
              />
              {" "}
              <EditableField
                field="personal_info.surname"
                value={personalInfo.surname}
                className="text-white bg-transparent border-none"
              />
            </h1>
            <div className="text-blue-100 space-y-1">
              <EditableField
                field="personal_info.email"
                value={personalInfo.email}
                type="email"
                className="text-blue-100"
              />
              <EditableField
                field="personal_info.phone"
                value={personalInfo.phone}
                className="text-blue-100"
              />
              <EditableField
                field="personal_info.address"
                value={personalInfo.address}
                className="text-blue-100"
              />
            </div>
          </div>
          {cvData.photo_url && (
            <img
              src={cvData.photo_url}
              alt="Profile"
              className="w-32 h-32 rounded-full border-4 border-white object-cover"
            />
          )}
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Professional Summary */}
        <section>
          <h2 className="text-xl font-bold text-blue-900 mb-3 border-b-2 border-blue-200 pb-2">
            Professional Summary
          </h2>
          <EditableField
            field="summary"
            value={cvData.summary}
            type="textarea"
            className="text-gray-700 leading-relaxed"
          />
        </section>

        {/* Work Experience */}
        <section>
          <h2 className="text-xl font-bold text-blue-900 mb-3 border-b-2 border-blue-200 pb-2">
            Work Experience
          </h2>
          {experience.length === 0 ? (
            <p className="text-gray-400 italic">No work experience added yet.</p>
          ) : (
            <div className="space-y-4">
              {experience.map((exp, idx) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-bold text-gray-900">
                        <EditableField
                          field={`experience.${idx}.job_title`}
                          value={exp.job_title}
                          className="font-bold"
                        />
                      </h3>
                      <p className="text-blue-700 font-medium">
                        <EditableField
                          field={`experience.${idx}.company`}
                          value={exp.company}
                          className="text-blue-700"
                        />
                      </p>
                    </div>
                    <div className="text-gray-600 text-sm">
                      <EditableField
                        field={`experience.${idx}.start_date`}
                        value={exp.start_date}
                        type="month"
                        className="text-sm"
                      />
                      {" - "}
                      <EditableField
                        field={`experience.${idx}.end_date`}
                        value={exp.end_date || "Present"}
                        type="month"
                        className="text-sm"
                      />
                    </div>
                  </div>
                  <EditableField
                    field={`experience.${idx}.description`}
                    value={exp.description}
                    type="textarea"
                    className="text-gray-700 text-sm"
                  />
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Education */}
        <section>
          <h2 className="text-xl font-bold text-blue-900 mb-3 border-b-2 border-blue-200 pb-2">
            Education & Training
          </h2>
          {education.length === 0 ? (
            <p className="text-gray-400 italic">No education added yet.</p>
          ) : (
            <div className="space-y-4">
              {education.map((edu, idx) => (
                <div key={idx} className="border-l-4 border-green-500 pl-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-gray-900">
                        <EditableField
                          field={`education.${idx}.degree`}
                          value={edu.degree}
                          className="font-bold"
                        />
                      </h3>
                      <p className="text-gray-700">
                        <EditableField
                          field={`education.${idx}.institution`}
                          value={edu.institution}
                        />
                      </p>
                      {edu.field_of_study && (
                        <p className="text-sm text-gray-600">
                          <EditableField
                            field={`education.${idx}.field_of_study`}
                            value={edu.field_of_study}
                            className="text-sm"
                          />
                        </p>
                      )}
                    </div>
                    <div className="text-gray-600 text-sm">
                      <EditableField
                        field={`education.${idx}.start_date`}
                        value={edu.start_date}
                        type="month"
                        className="text-sm"
                      />
                      {" - "}
                      <EditableField
                        field={`education.${idx}.end_date`}
                        value={edu.end_date}
                        type="month"
                        className="text-sm"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Skills */}
        <section>
          <h2 className="text-xl font-bold text-blue-900 mb-3 border-b-2 border-blue-200 pb-2">
            Skills & Competences
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Technical Skills</h3>
              <div className="flex flex-wrap gap-2">
                {skills.technical && skills.technical.length > 0 ? (
                  skills.technical.map((skill, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-gray-400 italic text-sm">No technical skills added</p>
                )}
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Soft Skills</h3>
              <div className="flex flex-wrap gap-2">
                {skills.soft && skills.soft.length > 0 ? (
                  skills.soft.map((skill, idx) => (
                    <span
                      key={idx}
                      className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-gray-400 italic text-sm">No soft skills added</p>
                )}
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Languages</h3>
              <div className="flex flex-wrap gap-2">
                {skills.languages && skills.languages.length > 0 ? (
                  skills.languages.map((skill, idx) => (
                    <span
                      key={idx}
                      className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-gray-400 italic text-sm">No languages added</p>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Save Button */}
      <div className="bg-gray-50 p-4 border-t border-gray-200 flex justify-end">
        <button
          onClick={onSave}
          className="btn-primary flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save CV
        </button>
      </div>
    </div>
  );
}

