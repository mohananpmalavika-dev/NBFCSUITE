/**
 * Signatures Page
 * Manage e-signature requests and sign documents
 */

import React, { useEffect, useState, useRef } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  message,
  Badge,
  Descriptions,
  Alert
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  FileOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import SignatureCanvas from 'react-signature-canvas';
import dmsService from '../../services/dms.service';
import {
  DocumentSignature,
  SignatureStatus
} from '../../types/dms.types';
import { formatDateTime } from '../../lib/utils';

const SignaturesPage: React.FC = () => {
  const navigate = useNavigate();
  const signaturePadRef = useRef<any>(null);
  const [signatures, setSignatures] = useState<DocumentSignature[]>([]);
  const [loading, setLoading] = useState(false);
  const [signModalVisible, setSignModalVisible] = useState(false);
  const [declineModalVisible, setDeclineModalVisible] = useState(false);
  const [selectedSignature, setSelectedSignature] = useState<DocumentSignature | null>(null);
  const [declineReason, setDeclineReason] = useState('');

  useEffect(() => {
    loadSignatures();
  }, []);

  const loadSignatures = async () => {
    setLoading(true);
    try {
      const response = await dmsService.getPendingSignatures();
      setSignatures(response.items || []);
    } catch (error: any) {
      message.error(error.message || 'Failed to load signatures');
    } finally {
      setLoading(false);
    }
  };

  const handleSign = (signature: DocumentSignature) => {
    setSelectedSignature(signature);
    setSignModalVisible(true);
  };

  const handleDecline = (signature: DocumentSignature) => {
    setSelectedSignature(signature);
    setDeclineModalVisible(true);
  };

  const submitSignature = async () => {
    if (!selectedSignature || !signaturePadRef.current) return;

    if (signaturePadRef.current.isEmpty()) {
      message.warning('Please provide your signature');
      return;
    }

    try {
      const signatureData = signaturePadRef.current.toDataURL();
      await dmsService.signDocument(selectedSignature.id, {
        signature_data: signatureData,
        signature_location: 'Web Application'
      });
      message.success('Document signed successfully');
      setSignModalVisible(false);
      setSelectedSignature(null);
      signaturePadRef.current?.clear();
      loadSignatures();
    } catch (error: any) {
      message.error(error.message || 'Failed to sign document');
    }
  };

  const submitDecline = async () => {
    if (!selectedSignature || !declineReason.trim()) {
      message.warning('Please provide a reason for declining');
      return;
    }

    try {
      await dmsService.declineSignature(selectedSignature.id, declineReason);
      message.success('Signature request declined');
      setDeclineModalVisible(false);
      setSelectedSignature(null);
      setDeclineReason('');
      loadSignatures();
    } catch (error: any) {
      message.error(error.message || 'Failed to decline signature');
    }
  };

  const clearSignature = () => {
    signaturePadRef.current?.clear();
  };

  const getStatusColor = (status: SignatureStatus): string => {
    const colors: Record<SignatureStatus, string> = {
      [SignatureStatus.PENDING]: 'warning',
      [SignatureStatus.SIGNED]: 'success',
      [SignatureStatus.DECLINED]: 'error',
      [SignatureStatus.EXPIRED]: 'default'
    };
    return colors[status] || 'default';
  };

  const isExpired = (expiresAt?: string): boolean => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  const columns: ColumnsType<DocumentSignature> = [
    {
      title: 'Document',
      key: 'document',
      render: (_, record) => (
        <Space>
          <FileOutlined />
          <a onClick={() => navigate(`/dms/documents/${record.document_id}`)}>
            Document #{record.document_id}
          </a>
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: SignatureStatus) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Order',
      dataIndex: 'signature_order',
      key: 'signature_order',
      render: (order: number) => (
        <Badge count={order} style={{ backgroundColor: '#1890ff' }} />
      ),
    },
    {
      title: 'Requested By',
      dataIndex: 'requested_by_name',
      key: 'requested_by_name',
    },
    {
      title: 'Requested At',
      dataIndex: 'requested_at',
      key: 'requested_at',
      render: (date: string) => formatDateTime(date),
    },
    {
      title: 'Expires At',
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (date: string) => {
        if (!date) return 'No expiry';
        const expired = isExpired(date);
        return (
          <Tag color={expired ? 'error' : 'default'}>
            {expired ? 'EXPIRED' : formatDateTime(date)}
          </Tag>
        );
      },
    },
    {
      title: 'Signed At',
      dataIndex: 'signed_at',
      key: 'signed_at',
      render: (date: string) => date ? formatDateTime(date) : 'N/A',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => {
        if (record.status === SignatureStatus.PENDING && !isExpired(record.expires_at)) {
          return (
            <Space>
              <Button
                type="primary"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleSign(record)}
              >
                Sign
              </Button>
              <Button
                danger
                size="small"
                icon={<CloseCircleOutlined />}
                onClick={() => handleDecline(record)}
              >
                Decline
              </Button>
              <Button
                size="small"
                icon={<EyeOutlined />}
                onClick={() => navigate(`/dms/documents/${record.document_id}`)}
              >
                View
              </Button>
            </Space>
          );
        }
        return (
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/dms/documents/${record.document_id}`)}
          >
            View
          </Button>
        );
      },
    },
  ];

  const pendingCount = signatures.filter(
    s => s.status === SignatureStatus.PENDING && !isExpired(s.expires_at)
  ).length;

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Space>
              <h2 style={{ margin: 0 }}>Signature Requests</h2>
              <Badge count={pendingCount} style={{ backgroundColor: '#faad14' }} />
            </Space>
            <Button onClick={loadSignatures} loading={loading}>
              Refresh
            </Button>
          </Space>

          <Table
            columns={columns}
            dataSource={signatures}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showTotal: (total) => `Total ${total} signature requests`,
            }}
          />
        </Space>
      </Card>

      {/* Sign Modal */}
      <Modal
        title="Sign Document"
        open={signModalVisible}
        onCancel={() => {
          setSignModalVisible(false);
          setSelectedSignature(null);
          clearSignature();
        }}
        onOk={submitSignature}
        okText="Sign Document"
        okButtonProps={{ icon: <CheckCircleOutlined /> }}
        width={700}
      >
        {selectedSignature && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Alert
              message="Electronic Signature"
              description="By signing this document electronically, you agree that your electronic signature has the same legal effect as a handwritten signature."
              type="info"
              showIcon
            />

            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="Document">
                Document #{selectedSignature.document_id}
              </Descriptions.Item>
              <Descriptions.Item label="Signer Email">
                {selectedSignature.signer_email}
              </Descriptions.Item>
              <Descriptions.Item label="Signature Order">
                {selectedSignature.signature_order}
              </Descriptions.Item>
              <Descriptions.Item label="Requested By">
                {selectedSignature.requested_by_name}
              </Descriptions.Item>
            </Descriptions>

            <div>
              <div style={{ marginBottom: '8px' }}>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <strong>Your Signature:</strong>
                  <Button size="small" onClick={clearSignature}>
                    Clear
                  </Button>
                </Space>
              </div>
              <div style={{ border: '2px dashed #d9d9d9', borderRadius: '4px' }}>
                <SignatureCanvas
                  ref={signaturePadRef}
                  canvasProps={{
                    width: 650,
                    height: 200,
                    className: 'signature-canvas',
                    style: { width: '100%', height: '200px' }
                  }}
                  backgroundColor="white"
                />
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#8c8c8c' }}>
                Draw your signature above using your mouse or touchscreen
              </div>
            </div>
          </Space>
        )}
      </Modal>

      {/* Decline Modal */}
      <Modal
        title="Decline Signature Request"
        open={declineModalVisible}
        onCancel={() => {
          setDeclineModalVisible(false);
          setSelectedSignature(null);
          setDeclineReason('');
        }}
        onOk={submitDecline}
        okText="Decline"
        okButtonProps={{ danger: true }}
      >
        {selectedSignature && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="Document">
                Document #{selectedSignature.document_id}
              </Descriptions.Item>
              <Descriptions.Item label="Requested By">
                {selectedSignature.requested_by_name}
              </Descriptions.Item>
            </Descriptions>

            <div>
              <label><strong>Reason for Declining (Required):</strong></label>
              <Input.TextArea
                rows={4}
                placeholder="Please provide a reason for declining this signature request..."
                value={declineReason}
                onChange={(e) => setDeclineReason(e.target.value)}
              />
            </div>
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default SignaturesPage;
