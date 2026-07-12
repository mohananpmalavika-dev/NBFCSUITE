/**
 * Approvals Page
 * Manage pending document approvals and workflows
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  message,
  Input,
  Descriptions,
  Timeline,
  Badge,
  Tabs,
  Select
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  SwapOutlined,
  FileOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dmsService from '../../services/dms.service';
import {
  DocumentWorkflow,
  DocumentApproval,
  ApprovalStatus,
  WorkflowStatus
} from '../../types/dms.types';
import { formatDateTime } from '../../lib/utils';

const { TextArea } = Input;
const { TabPane } = Tabs;
const { Option } = Select;

const ApprovalsPage: React.FC = () => {
  const navigate = useNavigate();
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionModalVisible, setActionModalVisible] = useState(false);
  const [delegateModalVisible, setDelegateModalVisible] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<DocumentWorkflow | null>(null);
  const [comments, setComments] = useState('');
  const [delegateUserId, setDelegateUserId] = useState<number | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject'>('approve');

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const response = await dmsService.getPendingApprovals();
      setApprovals(response.items || []);
    } catch (error: any) {
      message.error(error.message || 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (workflow: DocumentWorkflow) => {
    setSelectedWorkflow(workflow);
    setActionType('approve');
    setActionModalVisible(true);
  };

  const handleReject = async (workflow: DocumentWorkflow) => {
    setSelectedWorkflow(workflow);
    setActionType('reject');
    setActionModalVisible(true);
  };

  const handleDelegate = async (workflow: DocumentWorkflow) => {
    setSelectedWorkflow(workflow);
    setDelegateModalVisible(true);
  };

  const submitAction = async () => {
    if (!selectedWorkflow) return;

    try {
      if (actionType === 'approve') {
        await dmsService.approveWorkflow(selectedWorkflow.id, { comments });
        message.success('Workflow approved successfully');
      } else {
        await dmsService.rejectWorkflow(selectedWorkflow.id, { comments });
        message.success('Workflow rejected successfully');
      }
      setActionModalVisible(false);
      setComments('');
      setSelectedWorkflow(null);
      loadApprovals();
    } catch (error: any) {
      message.error(error.message || `Failed to ${actionType} workflow`);
    }
  };

  const submitDelegation = async () => {
    if (!selectedWorkflow || !delegateUserId) return;

    try {
      await dmsService.delegateWorkflow(selectedWorkflow.id, {
        delegate_to_id: delegateUserId,
        comments
      });
      message.success('Workflow delegated successfully');
      setDelegateModalVisible(false);
      setDelegateUserId(null);
      setComments('');
      setSelectedWorkflow(null);
      loadApprovals();
    } catch (error: any) {
      message.error(error.message || 'Failed to delegate workflow');
    }
  };

  const getStatusColor = (status: WorkflowStatus): string => {
    const colors: Record<WorkflowStatus, string> = {
      [WorkflowStatus.PENDING]: 'warning',
      [WorkflowStatus.IN_PROGRESS]: 'processing',
      [WorkflowStatus.APPROVED]: 'success',
      [WorkflowStatus.REJECTED]: 'error',
      [WorkflowStatus.CANCELLED]: 'default'
    };
    return colors[status] || 'default';
  };

  const columns: ColumnsType<DocumentWorkflow> = [
    {
      title: 'Document',
      key: 'document',
      render: (_, record) => (
        <Space>
          <FileOutlined />
          <a onClick={() => navigate(`/dms/documents/${record.document_id}`)}>
            {record.document?.title || 'N/A'}
          </a>
        </Space>
      ),
    },
    {
      title: 'Workflow',
      dataIndex: 'workflow_name',
      key: 'workflow_name',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: WorkflowStatus) => (
        <Tag color={getStatusColor(status)}>
          {status.replace(/_/g, ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Stage',
      key: 'stage',
      render: (_, record) => (
        <Badge
          count={`${record.current_stage}/${record.total_stages}`}
          style={{ backgroundColor: '#1890ff' }}
        />
      ),
    },
    {
      title: 'Initiated By',
      dataIndex: 'initiated_by_name',
      key: 'initiated_by_name',
    },
    {
      title: 'Initiated At',
      dataIndex: 'initiated_at',
      key: 'initiated_at',
      render: (date: string) => formatDateTime(date),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<CheckCircleOutlined />}
            onClick={() => handleApprove(record)}
          >
            Approve
          </Button>
          <Button
            danger
            size="small"
            icon={<CloseCircleOutlined />}
            onClick={() => handleReject(record)}
          >
            Reject
          </Button>
          <Button
            size="small"
            icon={<SwapOutlined />}
            onClick={() => handleDelegate(record)}
          >
            Delegate
          </Button>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/dms/documents/${record.document_id}`)}
          >
            View
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Space>
              <h2 style={{ margin: 0 }}>Pending Approvals</h2>
              <Badge count={approvals.length} style={{ backgroundColor: '#faad14' }} />
            </Space>
            <Button
              onClick={loadApprovals}
              loading={loading}
            >
              Refresh
            </Button>
          </Space>

          <Table
            columns={columns}
            dataSource={approvals}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showTotal: (total) => `Total ${total} approvals`,
            }}
          />
        </Space>
      </Card>

      {/* Action Modal (Approve/Reject) */}
      <Modal
        title={actionType === 'approve' ? 'Approve Workflow' : 'Reject Workflow'}
        open={actionModalVisible}
        onCancel={() => {
          setActionModalVisible(false);
          setComments('');
          setSelectedWorkflow(null);
        }}
        onOk={submitAction}
        okText={actionType === 'approve' ? 'Approve' : 'Reject'}
        okButtonProps={{
          danger: actionType === 'reject',
          icon: actionType === 'approve' ? <CheckCircleOutlined /> : <CloseCircleOutlined />
        }}
      >
        {selectedWorkflow && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="Document">
                {selectedWorkflow.document?.title}
              </Descriptions.Item>
              <Descriptions.Item label="Workflow">
                {selectedWorkflow.workflow_name}
              </Descriptions.Item>
              <Descriptions.Item label="Stage">
                {selectedWorkflow.current_stage} of {selectedWorkflow.total_stages}
              </Descriptions.Item>
              <Descriptions.Item label="Initiated By">
                {selectedWorkflow.initiated_by_name}
              </Descriptions.Item>
            </Descriptions>

            {selectedWorkflow.stages && selectedWorkflow.stages.length > 0 && (
              <div>
                <h4>Workflow Timeline</h4>
                <Timeline>
                  {selectedWorkflow.stages.map((stage: any, index: number) => (
                    <Timeline.Item
                      key={index}
                      color={
                        index < selectedWorkflow.current_stage - 1
                          ? 'green'
                          : index === selectedWorkflow.current_stage - 1
                          ? 'blue'
                          : 'gray'
                      }
                    >
                      <p><strong>Stage {index + 1}</strong></p>
                      <p>{stage.name || `Stage ${index + 1}`}</p>
                    </Timeline.Item>
                  ))}
                </Timeline>
              </div>
            )}

            <div>
              <label><strong>Comments {actionType === 'reject' && '(Required)'}:</strong></label>
              <TextArea
                rows={4}
                placeholder={`Add your comments for ${actionType === 'approve' ? 'approval' : 'rejection'}...`}
                value={comments}
                onChange={(e) => setComments(e.target.value)}
              />
            </div>
          </Space>
        )}
      </Modal>

      {/* Delegate Modal */}
      <Modal
        title="Delegate Approval"
        open={delegateModalVisible}
        onCancel={() => {
          setDelegateModalVisible(false);
          setDelegateUserId(null);
          setComments('');
          setSelectedWorkflow(null);
        }}
        onOk={submitDelegation}
        okText="Delegate"
        okButtonProps={{ disabled: !delegateUserId }}
      >
        {selectedWorkflow && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="Document">
                {selectedWorkflow.document?.title}
              </Descriptions.Item>
              <Descriptions.Item label="Workflow">
                {selectedWorkflow.workflow_name}
              </Descriptions.Item>
            </Descriptions>

            <div>
              <label><strong>Delegate To (User ID):</strong></label>
              <Input
                type="number"
                placeholder="Enter user ID to delegate to"
                value={delegateUserId || ''}
                onChange={(e) => setDelegateUserId(Number(e.target.value))}
              />
            </div>

            <div>
              <label><strong>Comments:</strong></label>
              <TextArea
                rows={3}
                placeholder="Add delegation notes..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
              />
            </div>
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default ApprovalsPage;
