/**
 * DMS Layout
 * Layout wrapper for DMS module
 */

import React from 'react';

export default function DMSLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

export const metadata = {
  title: 'Document Management System | NBFC Suite',
  description: 'Manage documents, workflows, approvals, and e-signatures',
};
