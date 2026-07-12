/**
 * DMS Dashboard Page
 * Overview and statistics for Document Management System
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Space,
  Button,
  Timeline,
  Progress,
  Empty
} from 'antd';
import {
  FileOutlined,
  FolderOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  EditOutlined,
  WarningOutlined,
  DatabaseOutlined,
  FileDoneOutlined,
  FileProtectOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { Pie, Column } from '@ant-design/plots';
import dmsService from '../../services/dms.service';
import { DMSDashboardStats } from '../../types/dms.types';
import { formatDate, formatDateTime } from '../../lib/utils';

const DMSDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DMSDashboardStats | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await dmsService.getDashboard();
      setStats(data);
    } catch (error: any) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div style={{ padding: '24px' }}>
        <Card loading={loading}>Loading dashboard...</Card>
      </div>
    );
  }

  const documentTypeData = stats.documents_by_type.map(item => ({
    type: item.type.replace(/_/g, ' ').toUpperCase(),
    value: item.count
  }));

  const documentStatusData = stats.documents_by_status.map(item => ({
    status: item.status.replace(/_/g, ' ').toUpperCase(),
    count: item.count
  }));

  const pieConfig = {
    data: documentTypeData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} ({percentage})',
    },
    interactions: [{ type: 'element-active' }],
  };

  const columnConfig = {
    data: documentStatusData,
    xField: 'status',
    yField: 'count',
    label: {
      position: 'middle',
      style: {
        fill: '#FFFFFF',
        opacity: 0.6,
      },
    },
    xAxis: {
      label: {
        autoHide: true,
        autoRotate: false,
      },
    },
    meta: {
      status: {
        alias: 'Status',
      },
      count: {
        alias: 'Count',
      },
    },
  };

  const activityColumns = [
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => (
        <Tag>{action.replace(/_/g, ' ').toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Document',
      dataIndex: 'document_title',
      key: 'document_title',
      render: (title: string, record: any) => (
        <a onClick={() => navigate(`/dms/documents/${record.id}`)}>
          {title}
        </a>
      ),
    },
    {
      title: 'User',
      dataIndex: 'performed_by',
      key: 'performed_by',
    },
    {
      title: 'Time',
      dataIndex: 'performed_at',
      key: 'performed_at',
      render: (date: string) => formatDateTime(date),
    },
  ];

  const expiringColumns = [
    {
      title: 'Document',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: any) => (
        <a onClick={() => navigate(`/dms/documents/${record.id}`)}>
          {title}
        </a>
      ),
    },
    {
      title: 'Expiry Date',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      render: (date: string) => (
        <Tag color="warning">{formatDate(date)}</Tag>
      ),
    },
    {
      title: 'Days Left',
      dataIndex: 'days_until_expiry',
      key: 'days_until_expiry',
      render: (days: number) => (
        <Tag color={days <= 7 ? 'error' : days <= 30 ? 'warning' : 'default'}>
          {days} days
        </Tag>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Row gutter={16}>
          <Col span={24}>
            <h2>Document Management Dashboard</h2>
          </Col>
        </Row>

        {/* Key Metrics */}
        <Row gutter={16}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Documents"
                value={stats.total_documents}
                prefix={<FileOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Storage"
                value={stats.total_size}
                prefix={<DatabaseOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Pending Approvals"
                value={stats.pending_approvals}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#faad14' }}
                suffix={
                  <Button
                    type="link"
                    size="small"
                    onClick={() => navigate('/dms/approvals')}
                  >
                    View
                  </Button>
                }
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Pending Signatures"
                value={stats.pending_signatures}
                prefix={<EditOutlined />}
                valueStyle={{ color: '#f5222d' }}
                suffix={
                  <Button
                    type="link"
                    size="small"
                    onClick={() => navigate('/dms/signatures')}
                  >
                    View
                  </Button>
                }
              />
            </Card>
          </Col>
        </Row>

        {/* Charts */}
        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Card title="Documents by Type" bordered={false}>
              {documentTypeData.length > 0 ? (
                <Pie {...pieConfig} />
              ) : (
                <Empty description="No document data available" />
              )}
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Documents by Status" bordered={false}>
              {documentStatusData.length > 0 ? (
                <Column {...columnConfig} />
              ) : (
                <Empty description="No status data available" />
              )}
            </Card>
          </Col>
        </Row>

        {/* Recent Activity */}
        <Row gutter={16}>
          <Col xs={24} lg={12}>
            <Card
              title={
                <Space>
                  <ClockCircleOutlined />
                  Recent Activity
                </Space>
              }
              extra={
                <Button type="link" onClick={() => navigate('/dms/documents')}>
                  View All
                </Button>
              }
            >
              {stats.recent_activity.length > 0 ? (
                <Table
                  columns={activityColumns}
                  dataSource={stats.recent_activity}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              ) : (
                <Empty description="No recent activity" />
              )}
            </Card>
          </Col>

          {/* Expiring Documents */}
          <Col xs={24} lg={12}>
            <Card
              title={
                <Space>
                  <WarningOutlined />
                  Expiring Soon
                </Space>
              }
              extra={
                stats.expiring_documents.length > 0 && (
                  <Tag color="warning">{stats.expiring_documents.length} documents</Tag>
                )
              }
            >
              {stats.expiring_documents.length > 0 ? (
                <Table
                  columns={expiringColumns}
                  dataSource={stats.expiring_documents}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              ) : (
                <Empty description="No expiring documents" />
              )}
            </Card>
          </Col>
        </Row>

        {/* Quick Actions */}
        <Row gutter={16}>
          <Col span={24}>
            <Card title="Quick Actions">
              <Space size="large" wrap>
                <Button
                  type="primary"
                  icon={<FileOutlined />}
                  size="large"
                  onClick={() => navigate('/dms/documents')}
                >
                  Browse Documents
                </Button>
                <Button
                  icon={<ClockCircleOutlined />}
                  size="large"
                  onClick={() => navigate('/dms/approvals')}
                >
                  Pending Approvals ({stats.pending_approvals})
                </Button>
                <Button
                  icon={<EditOutlined />}
                  size="large"
                  onClick={() => navigate('/dms/signatures')}
                >
                  Pending Signatures ({stats.pending_signatures})
                </Button>
                <Button
                  icon={<FileProtectOutlined />}
                  size="large"
                  onClick={() => navigate('/dms/templates')}
                >
                  Workflow Templates
                </Button>
              </Space>
            </Card>
          </Col>
        </Row>
      </Space>
    </div>
  );
};

export default DMSDashboard;
