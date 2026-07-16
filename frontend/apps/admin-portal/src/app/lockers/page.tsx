"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LockersPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/lockers/dashboard");
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <p>Redirecting to dashboard...</p>
    </div>
  );
}
