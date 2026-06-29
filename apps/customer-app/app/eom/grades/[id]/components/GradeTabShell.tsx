
"use client";

import React from 'react';

export function SectionHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-4">
      <div className="text-sm text-gray-600">{subtitle ?? ' '}</div>
      <div className="text-lg font-semibold">{title}</div>
    </div>
  );
}

export function InlineRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 py-1">
      <div className="text-sm text-gray-600">{label}</div>
      <div className="text-sm text-gray-800 text-right break-words">{value}</div>
    </div>
  );
}

