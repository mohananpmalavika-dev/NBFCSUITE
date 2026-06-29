"use client";
import React, { useState } from 'react';
import { createDesignation } from '../designationApi';

export default function NewDesignation() {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [status, setStatus] = useState('draft');
  const [message, setMessage] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createDesignation({ code, name, status });
      setMessage('Created');
    } catch (err) {
      setMessage('Failed');
    }
  }

  return (
    <div>
      <h1>New Designation</h1>
      <form onSubmit={submit}>
        <div>
          <label>Code</label>
          <input value={code} onChange={(e) => setCode(e.target.value)} />
        </div>
        <div>
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label>Status</label>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="draft">draft</option>
            <option value="active">active</option>
            <option value="inactive">inactive</option>
          </select>
        </div>
        <button type="submit">Create</button>
      </form>
      <div>{message}</div>
    </div>
  );
}
