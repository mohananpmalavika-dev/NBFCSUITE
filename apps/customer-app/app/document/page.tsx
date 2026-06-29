"use client";

import React, { useEffect, useState } from 'react';
import { documentApi } from '../document/documentApi';

export default function DocumentListPage() {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    documentApi.listDocuments()
      .then((res) => setDocs(res.items || []))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading documents...</div>;

  return (
    <div>
      <h1>Documents</h1>
      <a href="/document/upload">Upload Document</a>
      <table>
        <thead>
          <tr>
            <th>Document ID</th>
            <th>Name</th>
            <th>Type</th>
            <th>Category</th>
            <th>Subject</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.id}>
              <td>{d.id}</td>
              <td>{d.document_name}</td>
              <td>{d.document_type}</td>
              <td>{d.document_category}</td>
              <td>{d.subject_type}:{d.subject_id}</td>
              <td>
                <a href={`/document/${d.id}`}>View</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
