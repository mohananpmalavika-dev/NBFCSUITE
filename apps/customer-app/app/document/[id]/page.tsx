"use client";

import React, { useEffect, useState } from 'react';
import { documentApi } from '../../document/documentApi';

interface Props {
  params: { id: string };
}

export default function DocumentDetail({ params }: Props) {
  const { id } = params;
  const [doc, setDoc] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    documentApi.getDocument(id)
      .then((d) => setDoc(d))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!doc) return <div>Document not found</div>;

  return (
    <div>
      <h1>Document: {doc.document_name}</h1>
      <p>Type: {doc.document_type}</p>
      <p>Category: {doc.document_category}</p>
      <p>Subject: {doc.subject_type}:{doc.subject_id}</p>
      <a href={`/api/proxy/document/${id}/download`}>Download</a>
    </div>
  );
}
