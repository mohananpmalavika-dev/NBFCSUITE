'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Award, Plus, AlertCircle } from 'lucide-react';

export default function CertificationsPage() {
  const [certifications, setCertifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCertifications();
  }, []);

  const loadCertifications = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/gold/audit-compliance/compliance-certifications');
      if (response.ok) {
        setCertifications(await response.json());
      }
    } catch (error) {
      console.error('Error loading certifications:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Compliance Certifications</h1>
          <p className="text-muted-foreground">Track organizational certifications and licenses</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Certification
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Certifications</CardTitle>
          <CardDescription>Manage compliance certifications and their renewal</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {certifications.map((cert) => (
                <Card key={cert.certification_id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <Award className="h-8 w-8 text-primary" />
                      <div className="flex gap-2">
                        {cert.is_expired && (
                          <Badge variant="destructive">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            Expired
                          </Badge>
                        )}
                        <Badge variant={cert.certification_status === 'active' ? 'default' : 'secondary'}>
                          {cert.certification_status}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <h3 className="font-semibold">{cert.certification_name}</h3>
                    <p className="text-sm text-muted-foreground">{cert.certification_type}</p>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Number:</span>
                        <span className="font-medium">{cert.certification_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Issuing Body:</span>
                        <span className="font-medium">{cert.issuing_body}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Issue Date:</span>
                        <span>{new Date(cert.issue_date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Expiry Date:</span>
                        <span>{new Date(cert.expiry_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
