/**
 * Job Application Tracker
 * Track applications, save jobs, and manage application pipeline
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Briefcase, Plus, CheckCircle, Clock, 
  XCircle, Send, FileText, Calendar
} from "lucide-react";
import toast from "react-hot-toast";

const STATUSES = {
  saved: { label: "Saved", color: "bg-gray-100 text-gray-800", icon: Clock },
  applied: { label: "Applied", color: "bg-blue-100 text-blue-800", icon: Send },
  interview: { label: "Interview", color: "bg-yellow-100 text-yellow-800", icon: Calendar },
  offer: { label: "Offer", color: "bg-green-100 text-green-800", icon: CheckCircle },
  rejected: { label: "Rejected", color: "bg-red-100 text-red-800", icon: XCircle },
};

export default function JobApplicationTracker({ userId }) {
  const [applications, setApplications] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newApplication, setNewApplication] = useState({
    job_title: "",
    company: "",
    job_url: "",
    status: "saved",
    notes: "",
    applied_date: "",
  });

  useEffect(() => {
    // Load saved applications from localStorage
    const saved = localStorage.getItem(`job_applications_${userId}`);
    if (saved) {
      setApplications(JSON.parse(saved));
    }
  }, [userId]);

  const saveApplications = (apps) => {
    localStorage.setItem(`job_applications_${userId}`, JSON.stringify(apps));
    setApplications(apps);
  };

  const handleAddApplication = () => {
    if (!newApplication.job_title || !newApplication.company) {
      toast.error("Please fill in job title and company");
      return;
    }

    const application = {
      ...newApplication,
      id: Date.now(),
      created_at: new Date().toISOString(),
    };

    saveApplications([...applications, application]);
    setNewApplication({
      job_title: "",
      company: "",
      job_url: "",
      status: "saved",
      notes: "",
      applied_date: "",
    });
    setShowAddForm(false);
    toast.success("Application added!");
  };

  const handleUpdateStatus = (id, newStatus) => {
    const updated = applications.map(app =>
      app.id === id ? { ...app, status: newStatus } : app
    );
    saveApplications(updated);
    toast.success("Status updated!");
  };

  const handleDelete = (id) => {
    const updated = applications.filter(app => app.id !== id);
    saveApplications(updated);
    toast.success("Application removed!");
  };

  const applicationsByStatus = Object.keys(STATUSES).reduce((acc, status) => {
    acc[status] = applications.filter(app => app.status === status);
    return acc;
  }, {});

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Briefcase className="w-6 h-6" />
          Job Application Tracker
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Application
        </button>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4"
        >
          <h3 className="font-semibold text-gray-900 mb-4">Add New Application</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-blue-900 mb-2">
                Job Title *
              </label>
              <input
                type="text"
                value={newApplication.job_title}
                onChange={(e) =>
                  setNewApplication({ ...newApplication, job_title: e.target.value })
                }
                className="input-field"
                placeholder="Software Engineer"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-blue-900 mb-2">
                Company *
              </label>
              <input
                type="text"
                value={newApplication.company}
                onChange={(e) =>
                  setNewApplication({ ...newApplication, company: e.target.value })
                }
                className="input-field"
                placeholder="Google"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-blue-900 mb-2">
                Job URL
              </label>
              <input
                type="url"
                value={newApplication.job_url}
                onChange={(e) =>
                  setNewApplication({ ...newApplication, job_url: e.target.value })
                }
                className="input-field"
                placeholder="https://..."
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-blue-900 mb-2">
                Status
              </label>
              <select
                value={newApplication.status}
                onChange={(e) =>
                  setNewApplication({ ...newApplication, status: e.target.value })
                }
                className="input-field"
              >
                {Object.entries(STATUSES).map(([key, { label }]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-bold text-blue-900 mb-2">
                Notes
              </label>
              <textarea
                value={newApplication.notes}
                onChange={(e) =>
                  setNewApplication({ ...newApplication, notes: e.target.value })
                }
                className="input-field min-h-[80px]"
                placeholder="Add any notes about this application..."
              />
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <button onClick={handleAddApplication} className="btn-primary">
              Add Application
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* Applications by Status */}
      <div className="space-y-6">
        {Object.entries(STATUSES).map(([status, { label, color, icon: Icon }]) => {
          const statusApps = applicationsByStatus[status] || [];
          if (statusApps.length === 0) return null;

          return (
            <div key={status}>
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Icon className="w-5 h-5" />
                {label} ({statusApps.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {statusApps.map((app) => (
                  <div
                    key={app.id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{app.job_title}</h4>
                        <p className="text-sm text-gray-600">{app.company}</p>
                      </div>
                      <button
                        onClick={() => handleDelete(app.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XCircle className="w-5 h-5" />
                      </button>
                    </div>
                    {app.job_url && (
                      <a
                        href={app.job_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline mb-2 block"
                      >
                        View Job Posting →
                      </a>
                    )}
                    {app.notes && (
                      <p className="text-sm text-gray-700 mb-2">{app.notes}</p>
                    )}
                    <div className="flex gap-2 mt-3">
                      {Object.keys(STATUSES).map((s) => (
                        <button
                          key={s}
                          onClick={() => handleUpdateStatus(app.id, s)}
                          className={
                            "text-xs px-2 py-1 rounded " +
                            (app.status === s
                              ? STATUSES[s].color
                              : "bg-gray-100 text-gray-600 hover:bg-gray-200")
                          }
                        >
                          {STATUSES[s].label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {applications.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Briefcase className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p>No applications tracked yet.</p>
          <p className="text-sm mt-2">Click "Add Application" to start tracking your job applications.</p>
        </div>
      )}
    </div>
  );
}

