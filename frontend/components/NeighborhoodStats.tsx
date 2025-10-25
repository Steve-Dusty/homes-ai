'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface ScoreDetail {
  factor: string;
  impact: string;
}

interface CompactStatProps {
  title: string;
  value: string | number;
  score?: number;
  icon?: string;
  details?: ScoreDetail[];
  onExpand?: () => void;
}

function CompactStat({ title, value, score, icon, details, onExpand }: CompactStatProps) {
  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const getBarColor = (score?: number) => {
    if (!score) return 'bg-gray-500';
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-blue-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  return (
    <div
      className={`backdrop-blur-md bg-transparent border border-white/10 rounded-lg overflow-hidden ${details ? 'cursor-pointer hover:border-white/20' : ''} transition-colors min-w-[140px]`}
      onClick={() => details && onExpand && onExpand()}
    >
      <div className="p-2.5">
        <div className="flex items-center gap-2">
          {icon && <span className="text-sm">{icon}</span>}
          <div className="flex-1 min-w-0">
            <div className="text-xs text-gray-300/80 uppercase tracking-wide truncate">{title}</div>
            <div className="flex items-baseline gap-1">
              <span className={`text-lg font-bold ${score ? getScoreColor(score) : 'text-white'}`}>
                {value}
              </span>
              {score !== undefined && (
                <span className="text-[10px] text-gray-400">/ 100</span>
              )}
            </div>
          </div>
          {details && (
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </div>
        {score !== undefined && (
          <div className="mt-1.5 w-full bg-white/5 rounded-full h-1 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${getBarColor(score)}`}
              style={{ width: `${score}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

interface ScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  score: number;
  icon: string;
  details: ScoreDetail[];
}

function ScoreModal({ isOpen, onClose, title, score, icon, details }: ScoreModalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!isOpen || !mounted) return null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const getBarColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-blue-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  const modalContent = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative backdrop-blur-2xl bg-white/5 border border-white/20 rounded-2xl shadow-2xl max-w-md w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">{icon}</span>
            <div>
              <h3 className="text-white font-bold text-xl">{title}</h3>
              <p className="text-gray-400 text-sm">Score Breakdown</p>
            </div>
          </div>

          <div className="flex items-baseline gap-2 mb-2">
            <span className={`text-4xl font-bold ${getScoreColor(score)}`}>
              {score}
            </span>
            <span className="text-gray-300">/ 100</span>
          </div>

          <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${getBarColor(score)}`}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>

        {/* Details */}
        <div className="space-y-3">
          <h4 className="text-white font-semibold text-sm uppercase tracking-wide">Factors</h4>
          {details.map((detail, idx) => (
            <div
              key={idx}
              className="flex justify-between items-center backdrop-blur-md bg-white/10 border border-white/20 rounded-lg p-3"
            >
              <span className="text-gray-200 text-sm">{detail.factor}</span>
              <span className="text-white font-semibold text-sm">{detail.impact}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}

interface NeighborhoodStatsProps {
  location?: string;
  propertyCount?: number;
  onNextListing?: () => void;
  currentListingIndex?: number;
  totalListings?: number;
}

export default function NeighborhoodStats({ location = 'San Francisco, CA', propertyCount = 0, onNextListing, currentListingIndex = 0, totalListings = 0 }: NeighborhoodStatsProps) {
  const [modalContent, setModalContent] = useState<{
    title: string;
    score: number;
    icon: string;
    details: ScoreDetail[];
  } | null>(null);

  // Mock data - in real app, this would come from Fetch.ai agents
  const stats = {
    overallScore: 87,
    schoolRating: 92,
    safetyScore: 78,
    avgPricePerSqft: '$950',
    avgSqft: '1,850',
    transitScore: 88,
  };

  const scoreDetails = {
    overall: [
      { factor: 'Location Quality', impact: '+25' },
      { factor: 'School District', impact: '+20' },
      { factor: 'Safety', impact: '+18' },
      { factor: 'Walkability', impact: '+15' },
      { factor: 'Transit Access', impact: '+9' }
    ],
    school: [
      { factor: 'Test Scores', impact: 'Excellent' },
      { factor: 'Student-Teacher Ratio', impact: '15:1' },
      { factor: 'Graduation Rate', impact: '98%' },
      { factor: 'College Readiness', impact: 'High' }
    ],
    safety: [
      { factor: 'Crime Rate', impact: 'Low' },
      { factor: 'Police Response', impact: '< 5 min' },
      { factor: 'Street Lighting', impact: 'Good' },
      { factor: 'Emergency Services', impact: 'Excellent' }
    ]
  };

  const openModal = (title: string, score: number, icon: string, details: ScoreDetail[]) => {
    setModalContent({ title, score, icon, details });
  };

  return (
    <>
      {/* First Row - Scores and Stats with border */}
      <div className="backdrop-blur-md bg-black/10 border-b border-white/10 p-3">
        <div className="flex items-start gap-3 flex-wrap">
          {/* Main Scores */}
          <CompactStat
            title="Overall Score"
            value={stats.overallScore}
            score={stats.overallScore}
            icon="⭐"
            details={scoreDetails.overall}
            onExpand={() => openModal('Overall Score', stats.overallScore, '⭐', scoreDetails.overall)}
          />

          <CompactStat
            title="School Rating"
            value={stats.schoolRating}
            score={stats.schoolRating}
            icon="🎓"
            details={scoreDetails.school}
            onExpand={() => openModal('School Rating', stats.schoolRating, '🎓', scoreDetails.school)}
          />

          <CompactStat
            title="Safety Score"
            value={stats.safetyScore}
            score={stats.safetyScore}
            icon="🛡️"
            details={scoreDetails.safety}
            onExpand={() => openModal('Safety Score', stats.safetyScore, '🛡️', scoreDetails.safety)}
          />

          {/* Neighborhood Stats - Combined */}
          <div className="backdrop-blur-md bg-transparent border border-white/10 rounded-lg overflow-hidden min-w-[140px]">
            <div className="p-2.5">
              <div className="flex items-center gap-2">
                <span className="text-sm">🏘️</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-gray-300/80 uppercase tracking-wide truncate">Avg Listing</div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-lg font-bold text-white">{stats.avgPricePerSqft}/sqft</span>
                  </div>
                  <div className="text-xs text-gray-400">{stats.avgSqft} sqft avg</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Second Row - Action and Location (No blur, transparent) */}
      <div className="p-3 flex items-center gap-3">
        {/* Find Nearby Houses Button */}
        <button
          onClick={onNextListing}
          disabled={!onNextListing || totalListings === 0}
          className="bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 hover:border-blue-500/50 rounded-lg px-4 py-2 text-white font-semibold text-sm transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>🏘️</span>
          {totalListings > 0 ? (
            <>
              Next Listing ({currentListingIndex + 1}/{totalListings})
            </>
          ) : (
            'Find Nearby Houses'
          )}
        </button>

        {/* Location Indicator */}
        <div className="flex items-center gap-2 text-white">
          <span className="text-sm">📍</span>
          <div>
            <div className="text-xs text-gray-300/80 uppercase tracking-wide">Location</div>
            <div className="text-sm font-bold">{location}</div>
          </div>
        </div>
      </div>

      {/* Score Modal */}
      {modalContent && (
        <ScoreModal
          isOpen={!!modalContent}
          onClose={() => setModalContent(null)}
          title={modalContent.title}
          score={modalContent.score}
          icon={modalContent.icon}
          details={modalContent.details}
        />
      )}
    </>
  );
}
