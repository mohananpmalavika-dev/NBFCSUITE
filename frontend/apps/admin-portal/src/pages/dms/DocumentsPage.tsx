/**
 * Documents List Page
 * Main page for viewing and managing documents
 */

import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  message,
  Dropdown,
  Menu,
  Card,
  Row,
  Col,
  Upload,
  Tooltip,
  Badge,
  Popconfirm
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  FilterOutlined,
  DownloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  FileOutlined,
  FolderOutlined,
  UploadOutlined,
  MoreOutlined,
  ShareAltOutlined,
  LockOutlined,
  UnlockOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dmsService from '../../services/dms.service';
import {
  Document,
  DocumentType,
  DocumentStatus,
  AccessLevel,
  DocumentFilters
} from '../../types/dms.types';
import UploadDocumentModal from './components/UploadDocumentModal';
import { formatBytes, formatDate } from '../../lib/utils';

const { Search } = Input;
const { Option } = Select;

const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<DocumentFilters>({
    page: 1,
    page_size: 20
  });
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  useEffect(() => {
    loadDocuments();
  }, [filters]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await dmsService.listDocuments(filters);
      setDocuments(response.items);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, search: value, page: 1 });
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters({ ...filters, [key]: value, page: 1 });
  };

  const handleTableChange = (pagination: any) => {
    setFilters({
      ...filters,
      page: pagination.current,
      page_size: pagination.pageSize
    });
  };

  const handleDownload = async (doc: Document) => {
    try {
      const blob = await dmsService.downloadDocument(doc.id);
      dmsService.triggerDownload(blob, doc.file_name);
      message.success('Document downloaded successfully');
    } catch (error: any) {
      message.error(error.message || 'Failed to download document');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await dmsService.deleteDocument(id);
      message.success('Document deleted successfully');
      loadDocuments();
    } catch (error: any) {
      message.error(error.message || 'Failed to delete document');
    }
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

  const getAccessLevelIcon = (level: AccessLevel) => {
    const icons: Record<AccessLevel, React.ReactNode> = {
      [AccessLevel.PRIVATE]: <LockOutlined style={{ color: '#ff4d4f' }} />,
      [AccessLevel.INTERNAL]: <LockOutlined style={{ color: '#faad14' }} />,
      [AccessLevel.RESTRICTED]: <LockOutlined style={{ color: '#1890ff' }} />,
      [AccessLevel.PUBLIC]: <UnlockOutlined style={{ color: '#52c41a' }} />
    };
    return icons[level];
  };

  const handleRowAction = (action: string, doc: Document) => {
    switch (action) {
      case 'view':
        navigate(`/dms/documents/${doc.id}`);
        break;
      case 'edit':
        navigate(`/dms/documents/${doc.id}/edit`);
        break;
      case 'download':
        handleDownload(doc);
        break;
      case 'share':
        navigate(`/dms/documents/${doc.id}/permissions`);
        break;
      case 'workflow':
        navigate(`/dms/documents/${doc.id}/workflow`);
        break;
      case 'signature':
        navigate(`/dms/documents/${doc.id}/signature`);
        break;
      default:
        break;
    }
  };

  const getActionMenu = (doc: Document) => (
    <Menu onClick={({ key }) => handleRowAction(key, doc)}>
      <Menu.Item key="view" icon={<EyeOutlined />}>
        View Details
      </Menu.Item>
      <Menu.Item key="download" icon={<DownloadOutlined />}>
        Download
      </Menu.Item>
      <Menu.Item key="edit" icon={<EditOutlined />}>
        Edit
      </Menu.Item>
      <Menu.Item key="share" icon={<ShareAltOutlined />}>
        Permissions
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="workflow">
        Start Workflow
      </Menu.Item>
      <Menu.Item key="signature">
        Request Signature
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="delete" danger>
        Delete
      </Menu.Item>
    </Menu>
  );

  const columns: ColumnsType<Document> = [
    {
      title: 'Document',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (text, record) => (
        <Space direction="vertical" size={0}>
          <Space>
            <FileOutlined />
            <a onClick={() => navigate(`/dms/documents/${record.id}`)}>
              {text}
            </a>
          </Space>
          <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
            {record.file_name}
          </span>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'document_type',
      key: 'document_type',
      width: 150,
      render: (type: DocumentType) => (
        <Tag>{type.replace(/_/g, ' ').toUpperCase()}</Tag>
      ),
      filters: Object.values(DocumentType).map(type => ({
        text: type.replace(/_/g, ' ').toUpperCase(),
        value: type
      })),
      onFilter: (value, record) => record.document_type === value,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: DocumentStatus) => (
        <Tag color={getStatusColor(status)}>
          {status.replace(/_/g, ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Access',
      dataIndex: 'access_level',
      key: 'access_level',
      width: 100,
      align: 'center',
      render: (level: AccessLevel) => (
        <Tooltip title={level.toUpperCase()}>
          {getAccessLevelIcon(level)}
        </Tooltip>
      ),
    },
    {
      title: 'Size',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatBytes(size),
    },
    {
      title: 'Version',
      dataIndex: 'current_version_number',
      key: 'current_version_number',
      width: 80,
      align: 'center',
      render: (version: number) => (
        <Badge count={`v${version}`} style={{ backgroundColor: '#1890ff' }} />
      ),
    },
    {
      title: 'Created By',
      dataIndex: 'created_by_name',
      key: 'created_by_name',
      width: 130,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Space>
          <Tooltip title="Download">
            <Button
              type="text"
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => handleDownload(record)}
            />
          </Tooltip>
          <Dropdown overlay={getActionMenu(record)} trigger={['click']}>
            <Button type="text" size="small" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Space>
                <h2 style={{ margin: 0 }}>Documents</h2>
                <Badge count={total} style={{ backgroundColor: '#1890ff' }} />
              </Space>
              <Space>
                <Button
                  type="primary"
                  icon={<UploadOutlined />}
                  onClick={() => setUploadModalVisible(true)}
                >
                  Upload Document
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadDocuments}
                  loading={loading}
                >
                  Refresh
                </Button>
              </Space>
            </Space>
          </Col>

          <Col xs={24} sm={24} md={8} lg={6}>
            <Search
              placeholder="Search documents..."
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={handleSearch}
            />
          </Col>

          <Col xs={12} sm={8} md={6} lg={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="Document Type"
              allowClear
              onChange={(value) => handleFilterChange('document_type', value)}
            >
              {Object.values(DocumentType).map(type => (
                <Option key={type} value={type}>
                  {type.replace(/_/g, ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>

          <Col xs={12} sm={8} md={6} lg={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="Status"
              allowClear
              onChange={(value) => handleFilterChange('status', value)}
            >
              {Object.values(DocumentStatus).map(status => (
                <Option key={status} value={status}>
                  {status.replace(/_/g, ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>

          <Col xs={12} sm={8} md={6} lg={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="Access Level"
              allowClear
              onChange={(value) => handleFilterChange('access_level', value)}
            >
              {Object.values(AccessLevel).map(level => (
                <Option key={level} value={level}>
                  {level.toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{
            current: filters.page,
            pageSize: filters.page_size,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} documents`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1400 }}
        />
      </Card>

      <UploadDocumentModal
        visible={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        onSuccess={() => {
          setUploadModalVisible(false);
          loadDocuments();
        }}
      />
    </div>
  );
};

export default DocumentsPage;
