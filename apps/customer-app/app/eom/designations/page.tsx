"use client";
import React, { useEffect, useState } from 'react';
import { listDesignations } from './designationApi';

export default function DesignationDirectory() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    listDesignations()
      .then((d) => setItems(d.items || []))
      .catch(() => setItems([]));
  }, []);

  return (
    <div>
      <h1>Designation Directory</h1>
      <p>Total: {items.length}</p>
      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Designation</th>
            <th>Grade</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((it) => (
            <tr key={it.id}>
              <td>{it.code}</td>
              <td>{it.name}</td>
              <td>{it.grade_id}</td>
              <td>{it.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
