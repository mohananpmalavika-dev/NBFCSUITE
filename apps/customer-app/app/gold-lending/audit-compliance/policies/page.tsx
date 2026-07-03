'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Clock, FileText } from 'lucide-react';

export default function PoliciesPage() {
  const [acknowledgements, setAcknowledgements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAcknowledgements();
  }, []);

  const loadAcknowledgements = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/gold/audit-compliance/policy-acknowledgements');
      if (response.ok) {
        setAcknowledgements(await response.json());
      }
    } catch (error) {
      console.error('Error loading acknowledgements:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Policy Acknowledgements</h1>
        <p className="text-muted-foreground">Track employee policy acknowledgements and compliance</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Policies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{acknowledgements.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {acknowledgements.filter(a => a.acknowledged_at).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {acknowledgements.filter(a => !a.acknowledged_at).length}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Policy Acknowledgements</CardTitle>
          <CardDescription>View and manage policy acknowledgement status</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-4">
              {acknowledgements.map((ack) => (
                <div key={ack.acknowledgement_id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-start gap-3">
                      {ack.acknowledged_at ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-1" />
                      ) : (
                        <Clock className="h-5 w-5 text-orange-600 mt-1" />
                      )}
                      <div>
                        <h3 className="font-semibold">{ack.policy_name}</h3>
                        <p className="text-sm text-muted-foreground">{ack.policy_type}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {ack.is_mandatory && <Badge variant="destructive">Mandatory</Badge>}
                      <Badge variant={ack.acknowledged_at ? 'default' : 'secondary'}>
                        {ack.acknowledgement_status}
                      </Badge>
                    </div>
                  </div>

                  <p className="text-sm mb-3 ml-8">{ack.policy_description}</p>

                  <div className="grid grid-cols-2 gap-4 text-sm ml-8">
                    <div>
                      <span className="text-muted-foreground">Version:</span>
                      <span className="ml-2 font-medium">{ack.policy_version}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Effective Date:</span>
                      <span className="ml-2">{new Date(ack.policy_effective_date).toLocaleDateString()}</span>
                    </div>
                    {ack.acknowledged_at && (
                      <>
                        <div>
                          <span className="text-muted-foreground">Acknowledged:</span>
                          <span className="ml-2">{new Date(ack.acknowledged_at).toLocaleDateString()}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">IP Address:</span>
                          <span className="ml-2 font-mono text-xs">{ack.acknowledgement_ip}</span>
                        </div>
                      </>
                    )}
                  </div>

                  {!ack.acknowledged_at && (
                    <div className="mt-3 ml-8">
                      <Button size="sm">
                        <FileText className="h-4 w-4 mr-2" />
                        View & Acknowledge
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
