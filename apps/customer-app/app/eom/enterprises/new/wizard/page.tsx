"use client";

import React, { useState } from 'react';
import { AppShell } from '../../../../components/AppShell';
import { useRouter } from 'next/navigation';
import { eomApiUrl } from '../../../eomApi';

export default function Wizard() {
  const [step, setStep] = useState(1);
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [currency, setCurrency] = useState('');
  const router = useRouter();

  async function submit() {
    const res = await fetch(eomApiUrl('/eom/enterprises'), {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, name, currency_code: currency })
    });
    if (res.ok) router.push('/eom/enterprises');
    else alert('Failed to create');
  }

  return (
    <AppShell>
      <div className="max-w-2xl">
        <h2 className="text-lg font-semibold mb-4">New Enterprise Wizard</h2>
        <div className="mb-4">Step {step} of 2</div>
        {step === 1 && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm">Code</label>
              <input className="input mt-1" value={code} onChange={(e)=>setCode(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm">Name</label>
              <input className="input mt-1" value={name} onChange={(e)=>setName(e.target.value)} />
            </div>
            <div className="flex space-x-2 mt-3">
              <button className="btn" onClick={() => setStep(2)}>Next</button>
            </div>
          </div>
        )}
        {step === 2 && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm">Currency</label>
              <input className="input mt-1" value={currency} onChange={(e)=>setCurrency(e.target.value)} />
            </div>
            <div className="flex space-x-2 mt-3">
              <button className="btn" onClick={() => setStep(1)}>Back</button>
              <button className="btn btn-primary" onClick={submit}>Create enterprise</button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
