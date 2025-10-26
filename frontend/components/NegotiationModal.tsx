'use client';

import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { Property } from '@/lib/mockData';

interface NegotiationModalProps {
  property: Property;
  onClose: () => void;
}

export function NegotiationModal({ property, onClose }: NegotiationModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    additionalInfo: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Backend integration will handle submission
    console.log('Negotiation submitted:', {
      propertyId: property.id,
      ...formData,
    });
    onClose();
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-slate-900/95 to-slate-800/95 border border-white/20 rounded-2xl shadow-2xl backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/60 hover:text-white transition-colors z-10"
          aria-label="Close modal"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Header - Property Info */}
        <div className="p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white mb-2">
            Start AI Negotiation
          </h2>
          <p className="text-sm text-white/60 mb-3">
            Our AI agent will negotiate this property on your behalf
          </p>
          <div className="space-y-1">
            <p className="text-lg text-white/90 font-semibold">
              {property.address}
            </p>
            <p className="text-sm text-white/70">
              {property.city}, {property.state}
            </p>
            <div className="flex items-center gap-2 mt-3">
              <span className="text-sm text-white/60">Listed Price:</span>
              <span className="text-xl font-bold text-green-400">
                {formatPrice(property.price)}
              </span>
            </div>
            <div className="text-xs text-white/50 mt-1">
              {property.bedrooms} beds • {property.bathrooms} baths •{' '}
              {property.sqft.toLocaleString()} sqft
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Contact Information Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white/90 border-b border-white/10 pb-2">
              Your Information
            </h3>

            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-white/80 mb-2"
              >
                Full Name <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-white/80 mb-2"
              >
                Email <span className="text-red-400">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all"
                placeholder="john@example.com"
              />
            </div>
          </div>

          {/* Additional Information Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white/90 border-b border-white/10 pb-2">
              Negotiation Preferences
            </h3>

            <div>
              <label
                htmlFor="additionalInfo"
                className="block text-sm font-medium text-white/80 mb-2"
              >
                Additional Information
              </label>
              <textarea
                id="additionalInfo"
                name="additionalInfo"
                rows={5}
                value={formData.additionalInfo}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all resize-none"
                placeholder="Share any preferences or requirements (budget constraints, move-in timeline, financing status, property concerns, etc.). Our AI agent will use this to negotiate on your behalf."
              />
            </div>

            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
              <p className="text-purple-300 text-sm flex items-start gap-2">
                <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <span>Our AI agent will handle the negotiation process with the listing agent on your behalf.</span>
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/20 rounded-lg text-white font-medium transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-semibold shadow-lg shadow-purple-500/20 transition-all"
            >
              Start AI Negotiation
            </button>
          </div>
        </form>

        {/* Footer Note */}
        <div className="px-6 pb-6">
          <p className="text-xs text-white/40 text-center">
            Our AI agent will contact the listing agent and negotiate on your behalf. You'll receive updates via email.
          </p>
        </div>
      </div>
    </div>,
    document.body
  );
}
