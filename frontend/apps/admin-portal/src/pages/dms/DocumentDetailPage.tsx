/**
 * Document Detail Page
 * View and manage individual document details
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Descriptions,
  Button,
  Space,
  Tag,
  Tabs,
  Table,
  Timeline,
  Comment,
  Form,
  Input,
  message,
  Modal,
  Upload,
  Divider,
  Row,
  Col,
  Statistic,
  Badge,
  Tooltip,
  Avatar
} from 'antd';
import {
  DownloadOutlined,
  EditOutlined,
  DeleteOutlined,
  ShareAltOutlined,
  FileOutlined,
  UploadOutlined,
  EyeOutlined,
  HistoryOutlined,
  CommentOutlined,
  LockOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ArrowLeftOutlined,
  SendOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import dmsService from '../../services/dms.service';
import {
  Document,
  DocumentVersion,
  DocumentComment,
  DocumentAuditLog,
  DocumentWorkflow,
  DocumentPermission,
  DocumentStatus,
  AccessLevel
} from '../../types/dms.types';
import { formatBytes, formatDate, formatDateTime } from '../../lib/utils';

const { TabPane } = Tabs;
const { TextArea } = Input;

const DocumentDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [document, setDocument] = useState<Document | null>(null);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [comments, setComments] = useState<DocumentComment[]>([]);
  const [auditLogs, setAuditLogs] = useState<DocumentAuditLog[]>([]);
  const [workflows, setWorkflows] = useState<DocumentWorkflow[]>([]);
  const [permissions, setPermissions] = useState<DocumentPermission[]>([]);
  const [loading, setLoading] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (id) {
      loadDocument();
      loadVersions();
      loadComments();
      loadWorkflows();
      loadPermissions();
    }
  }, [id]);

  const loadDocument = async () => {
    setLoading(true);
    try {
      const data = await dmsService.getDocument(Number(id));
      setDocument(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const loadVersions = async () => {
    try {
      const data = await dmsService.listVersions(Number(id));
      setVersions(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load versions');
    }
  };

  const loadComments = async () => {
    try {
      const data = await dmsService.getDocumentComments(Number(id));
      setComments(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load comments');
    }
  };

  const loadWorkflows = async () => {
    try {
      const data = await dmsService.getDocumentWorkflows(Number(id));
      setWorkflows(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load workflows');
    }
  };

  const loadPermissions = async () => {
    try {
      const data = await dmsService.getDocumentPermissions(Number(id));
      setPermissions(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load permissions');
    }
  };

  const handleDownload = async (versionId?: number) => {
    if (!document) return;
    try {
      const blob = await dmsService.downloadDocument(document.id, versionId);
      dmsService.triggerDownload(blob, document.file_name);
      message.success('Document downloaded successfully');
    } catch (error: any) {
      message.error(error.message || 'Failed to download document');
    }
  };

  const handleAddComment = async () => {
    if (!commentText.trim() || !id) return;
    try {
      await dmsService.addComment({
        document_id: Number(id),
        comment_text: commentText,
        is_internal: false
      });
      setCommentText('');
      loadComments();
      message.success('Comment added successfully');
    } catch (error: any) {
      message.error(error.message || 'Failed to add comment');
    }
  };

  const handleUploadVersion = async (file: File) => {
    if (!id) return;
    try {
      await dmsService.uploadVersion(Number(id), {
        file,
        change_description: form.getFieldValue('change_description')
      });
      setUploadModalVisible(false);
      form.resetFields();
      loadDocument();
      loadVersions();
      message.success('New version uploaded successfully');
    } catch (error: any) {
      message.error(error.message || 'Failed to upload version');
    }
  };

  const handleDelete = async () => {
    if (!document) return;
    Modal.confirm({
      title: 'Delete Document',
      content: 'Are you sure you want to delete this document? This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        try {
          await dmsService.deleteDocument(document.id);
          message.success('Document deleted successfully');
          navigate('/dms/documents');
        } catch (error: any) {
          message.error(error.message || 'Failed to delete document');
        }
      }
    });
  };

  const getStatusColor = (status: DocumentStatus): string => {
    const colors: Record<DocumentStatus, string> = {
      [DocumentStatus.DRAFT]: 'default',
      [DocumentStatus.PENDING_REVIEW]: 'processing',
      [DocumentStatus.UNDER_REVIEW]: 'warning',
      [DocumentStatus.APPROVED]: 'success',
      [DocumentStatus.REJECTED]: 'error',
      [DocumentStatus.ARCHIVED]: 'default',
      [DocumentStatus.EXPIRED]: 'error'
    };
    return colors[status] || 'default';
  };

  if (loading || !document) {
    return <div style={{ padding: '24px' }}>Loading...</div>;
  }

  const versionColumns = [
    {
      title: 'Version',
      dataIndex: 'version_number',
      key: 'version_number',
      render: (version: number, record: DocumentVersion) => (
        <Space>
          <Badge count={`v${version}`} style={{ backgroundColor: record.is_current ? '#52c41a' : '#1890ff' }} />
          {record.is_current && <Tag color="success">Current</Tag>}
        </Space>
      ),
    },
    {
      title: 'File Name',
      dataIndex: 'file_name',
      key: 'file_name',
    },
    {
      title: 'Size',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => formatBytes(size),
    },
    {
      title: 'Change Description',
      dataIndex: 'change_description',
      key: 'change_description',
    },
    {
      title: 'Uploaded By',
      dataIndex: 'uploaded_by_name',
      key: 'uploaded_by_name',
    },
    {
      title: 'Uploaded At',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      render: (date: string) => formatDateTime(date),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: DocumentVersion) => (
        <Button
          type="link"
          icon={<DownloadOutlined />}
          onClick={() => handleDownload(record.id)}
        >
          Download
        </Button>
      ),
    },
  ];

  const permissionColumns = [
    {
      title: 'User/Role',
      key: 'entity',
      render: (_: any, record: DocumentPermission) => (
        record.user_name || record.role_name || 'N/A'
      ),
    },
    {
      title: 'Permission',
      dataIndex: 'permission_type',
      key: 'permission_type',
      render: (type: string) => <Tag>{type.toUpperCase()}</Tag>,
    },
    {
      title: 'Granted By',
      dataIndex: 'granted_by_name',
      key: 'granted_by_name',
    },
    {
      title: 'Granted At',
      dataIndex: 'granted_at',
      key: 'granted_at',
      render: (date: string) => formatDateTime(date),
    },
    {
      title: 'Expires At',
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (date: string) => date ? formatDateTime(date) : 'Never',
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/dms/documents')}
              >
                Back
              </Button>
              <FileOutlined style={{ fontSize: '24px' }} />
              <div>
                <h2 style={{ margin: 0 }}>{document.title}</h2>
                <span style={{ color: '#8c8c8c' }}>{document.file_name}</span>
              </div>
            </Space>
            <Space>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => handleDownload()}
              >
                Download
              </Button>
              <Button
                icon={<UploadOutlined />}
                onClick={() => setUploadModalVisible(true)}
              >
                Upload Version
              </Button>
              <Button
                icon={<EditOutlined />}
                onClick={() => navigate(`/dms/documents/${document.id}/edit`)}
              >
                Edit
              </Button>
              <Button
                icon={<ShareAltOutlined />}
                onClick={() => navigate(`/dms/documents/${document.id}/permissions`)}
              >
                Share
              </Button>
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={handleDelete}
              >
                Delete
              </Button>
            </Space>
          </Space>
        </Card>

        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Current Version"
                value={document.current_version_number}
                prefix="v"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="File Size"
                value={formatBytes(document.file_size)}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Versions"
                value={versions.length}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Comments"
                value={comments.length}
              />
            </Card>
          </Col>
        </Row>

        <Card>
          <Descriptions title="Document Information" bordered column={2}>
            <Descriptions.Item label="Status">
              <Tag color={getStatusColor(document.status)}>
                {document.status.replace(/_/g, ' ').toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Access Level">
              <Tag>{document.access_level.toUpperCase()}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Document Type">
              {document.document_type.replace(/_/g, ' ').toUpperCase()}
            </Descriptions.Item>
            <Descriptions.Item label="MIME Type">
              {document.mime_type}
            </Descriptions.Item>
            <Descriptions.Item label="Created By">
              {document.created_by_name}
            </Descriptions.Item>
            <Descriptions.Item label="Created At">
              {formatDateTime(document.created_at)}
            </Descriptions.Item>
            <Descriptions.Item label="Last Updated">
              {formatDateTime(document.updated_at)}
            </Descriptions.Item>
            <Descriptions.Item label="Updated By">
              {document.updated_by_name || 'N/A'}
            </Descriptions.Item>
            {document.expiry_date && (
              <Descriptions.Item label="Expiry Date" span={2}>
                <Tag color={new Date(document.expiry_date) < new Date() ? 'error' : 'warning'}>
                  {formatDate(document.expiry_date)}
                </Tag>
              </Descriptions.Item>
            )}
            {document.description && (
              <Descriptions.Item label="Description" span={2}>
                {document.description}
              </Descriptions.Item>
            )}
            {document.tags && document.tags.length > 0 && (
              <Descriptions.Item label="Tags" span={2}>
                {document.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
              </Descriptions.Item>
            )}
          </Descriptions>
        </Card>

        <Card>
          <Tabs defaultActiveKey="versions">
            <TabPane tab="Version History" key="versions">
              <Table
                columns={versionColumns}
                dataSource={versions}
                rowKey="id"
                pagination={false}
              />
            </TabPane>

            <TabPane tab={`Comments (${comments.length})`} key="comments">
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Card>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <TextArea
                      rows={3}
                      placeholder="Add a comment..."
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                    />
                    <Button
                      type="primary"
                      icon={<SendOutlined />}
                      onClick={handleAddComment}
                      disabled={!commentText.trim()}
                    >
                      Add Comment
                    </Button>
                  </Space>
                </Card>

                {comments.map(comment => (
                  <Comment
                    key={comment.id}
                    author={comment.created_by_name}
                    avatar={<Avatar>{comment.created_by_name?.charAt(0)}</Avatar>}
                    content={<p>{comment.comment_text}</p>}
                    datetime={formatDateTime(comment.created_at)}
                  />
                ))}
              </Space>
            </TabPane>

            <TabPane tab={`Workflows (${workflows.length})`} key="workflows">
              <Timeline>
                {workflows.map(workflow => (
                  <Timeline.Item
                    key={workflow.id}
                    color={workflow.status === 'approved' ? 'green' : workflow.status === 'rejected' ? 'red' : 'blue'}
                  >
                    <p><strong>{workflow.workflow_name}</strong></p>
                    <p>Status: <Tag>{workflow.status.toUpperCase()}</Tag></p>
                    <p>Stage: {workflow.current_stage} of {workflow.total_stages}</p>
                    <p>Initiated by: {workflow.initiated_by_name}</p>
                    <p>Initiated at: {formatDateTime(workflow.initiated_at)}</p>
                  </Timeline.Item>
                ))}
              </Timeline>
            </TabPane>

            <TabPane tab={`Permissions (${permissions.length})`} key="permissions">
              <Table
                columns={permissionColumns}
                dataSource={permissions}
                rowKey="id"
                pagination={false}
              />
            </TabPane>
          </Tabs>
        </Card>
      </Space>

      <Modal
        title="Upload New Version"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="change_description"
            label="Change Description"
          >
            <TextArea rows={3} placeholder="Describe what changed in this version..." />
          </Form.Item>
          <Form.Item>
            <Upload
              beforeUpload={(file) => {
                handleUploadVersion(file);
                return false;
              }}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>Select File</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DocumentDetailPage;
