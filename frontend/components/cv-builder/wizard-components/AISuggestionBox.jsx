/**
 * AI Suggestion Box
 * Reusable component for displaying AI suggestions
 */
import { Sparkles, Loader2 } from "lucide-react";
import { useState } from "react";

export default function AISuggestionBox({
  suggestions = [],
  loading = false,
  onSelect,
  title = "AI Suggestions",
  emptyMessage = "No suggestions available",
}) {
  if (loading) {
    return (
      <div className="bg-gradient-to-r from-sky-50 to-violet-50 rounded-lg p-4 border border-sky-200">
        <div className="flex items-center gap-2 text-sky-700">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm font-medium">Generating suggestions...</span>
        </div>
      </div>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <p className="text-sm text-gray-600">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-sky-50 to-violet-50 rounded-lg p-4 border border-sky-200">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-4 h-4 text-sky-600" />
        <h4 className="text-sm font-semibold text-sky-900">{title}</h4>
      </div>
      <div className="space-y-2">
        {suggestions.map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => onSelect && onSelect(suggestion)}
            className="w-full text-left p-3 bg-white rounded-lg border border-sky-200 hover:border-sky-400 hover:bg-sky-50 transition-all text-sm text-gray-700"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
