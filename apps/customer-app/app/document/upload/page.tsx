"use client";

import React, { useState } from 'react';
import { documentApi } from '../../document/documentApi';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const form = new FormData();
    form.append('subject_type', 'customer');
    form.append('subject_id', 'TBD');
    form.append('document_type', 'KYC');
    form.append('document_name', file.name);
    form.append('file', file);

    try {
      setStatus('Uploading...');
      const res = await documentApi.uploadDocument(form);
      setStatus('Uploaded: ' + res.id);
    } catch (err) {
      console.error(err);
      setStatus('Upload failed');
    }
  };

  return (
    <div>
      <h1>Upload Document</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} />
        <button type="submit">Upload</button>
      </form>
      {status && <div>{status}</div>}
    </div>
  );
}
