/**
 * Leads List Page
 * Main page for viewing and managing leads
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
  Badge
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  FilterOutlined,
  MoreOutlined,
  PhoneOutlined,
  MailOutlined,
  UserOutlined,
  FireOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import crmService from '../../services/crm.service';
import {
  Lead,
  LeadStatus,
  LeadSource,
  LeadPriority,
  LeadTemperature,
  LeadFilters
} from '../../types/crm.types';
import CreateLeadModal from './components/CreateLeadModal';

const { Search } = Input;
const { Option } = Select;

const LeadsPage: React.FC = () => {
  const navigate = useNavigate();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<LeadFilters>({
    page: 1,
    page_size: 20
  });
  const [createModalVisible, setCreateModalVisible] = useState(false);

  useEffect(() => {
    loadLeads();
  }, [filters]);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const response = await crmService.listLeads(filters);
      setLeads(response.items);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.message || 'Failed to load leads');
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

  const getStatusColor = (status: LeadStatus): string => {
    const colors: Record<LeadStatus, string> = {
      [LeadStatus.NEW]: 'blue',
      [LeadStatus.CONTACTED]: 'cyan',
      [LeadStatus.QUALIFIED]: 'green',
      [LeadStatus.UNQUALIFIED]: 'red',
      [LeadStatus.NURTURING]: 'orange',
      [LeadStatus.CONVERTED]: 'success',
      [LeadStatus.LOST]: 'error',
      [LeadStatus.DUPLICATE]: 'default',
      [LeadStatus.INVALID]: 'default'
    };
    return colors[status] || 'default';
  };


  const getTemperatureColor = (temp: LeadTemperature): string => {
    const colors: Record<LeadTemperature, string> = {
      [LeadTemperature.HOT]: '#ff4d4f',
      [LeadTemperature.WARM]: '#faad14',
      [LeadTemperature.COLD]: '#1890ff'
    };
    return colors[temp];
  };

  const getPriorityColor = (priority: LeadPriority): string => {
    const colors: Record<LeadPriority, string> = {
      [LeadPriority.URGENT]: 'red',
      [LeadPriority.HIGH]: 'orange',
      [LeadPriority.MEDIUM]: 'blue',
      [LeadPriority.LOW]: 'default'
    };
    return colors[priority];
  };

  const handleRowAction = (action: string, lead: Lead) => {
    switch (action) {
      case 'view':
        navigate(`/crm/leads/${lead.id}`);
        break;
      case 'edit':
        navigate(`/crm/leads/${lead.id}/edit`);
        break;
      case 'call':
        window.location.href = `tel:${lead.mobile}`;
        break;
      case 'email':
        if (lead.email) {
          window.location.href = `mailto:${lead.email}`;
        }
        break;
      default:
        break;
    }
  };

  const getActionMenu = (lead: Lead) => (
    <Menu onClick={({ key }) => handleRowAction(key, lead)}>
      <Menu.Item key="view" icon={<UserOutlined />}>
        View Details
      </Menu.Item>
      <Menu.Item key="call" icon={<PhoneOutlined />}>
        Call {lead.mobile}
      </Menu.Item>
      {lead.email && (
        <Menu.Item key="email" icon={<MailOutlined />}>
          Send Email
        </Menu.Item>
      )}
      <Menu.Divider />
      <Menu.Item key="edit">Edit Lead</Menu.Item>
    </Menu>
  );

  const columns: ColumnsType<Lead> = [
    {
      title: 'Lead Code',
      dataIndex: 'lead_code',
      key: 'lead_code',
      fixed: 'left',
      width: 120,
      render: (code: string, record: Lead) => (
        <a onClick={() => navigate(`/crm/leads/${record.id}`)}>{code}</a>
      )
    },
    {
      title: 'Name',
      dataIndex: 'full_name',
      key: 'full_name',
      width: 200,
      render: (name: string, record: Lead) => (
        <Space>
          {name}
          {record.lead_temperature === LeadTemperature.HOT && (
            <FireOutlined style={{ color: '#ff4d4f' }} />
          )}
        </Space>
      )
    },
    {
      title: 'Mobile',
      dataIndex: 'mobile',
      key: 'mobile',
      width: 130
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      width: 200,
      ellipsis: true
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      width: 120,
      render: (source: LeadSource) => (
        <Tag>{source.replace('_', ' ').toUpperCase()}</Tag>
      )
    },
    {
      title: 'Product Interest',
      dataIndex: 'product_interest',
      key: 'product_interest',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Score',
      dataIndex: 'lead_score',
      key: 'lead_score',
      width: 80,
      align: 'center',
      render: (score: number, record: Lead) => (
        <Badge
          count={score}
          style={{
            backgroundColor: getTemperatureColor(record.lead_temperature)
          }}
        />
      ),
      sorter: true
    },

    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: LeadStatus) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: LeadPriority) => (
        <Tag color={getPriorityColor(priority)}>
          {priority.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Assigned To',
      dataIndex: 'assigned_to_name',
      key: 'assigned_to_name',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Next Follow-up',
      dataIndex: 'next_follow_up_date',
      key: 'next_follow_up_date',
      width: 150,
      render: (date: string) => date ? new Date(date).toLocaleDateString() : '-'
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => new Date(date).toLocaleDateString()
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 80,
      render: (_: any, record: Lead) => (
        <Dropdown overlay={getActionMenu(record)} trigger={['click']}>
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
          <Col>
            <h2>Lead Management</h2>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              Create Lead
            </Button>
          </Col>
        </Row>

        {/* Filters */}
        <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
          <Col xs={24} sm={12} md={6}>
            <Search
              placeholder="Search leads..."
              allowClear
              onSearch={handleSearch}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="Status"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('status', value)}
            >
              {Object.values(LeadStatus).map((status) => (
                <Option key={status} value={status}>
                  {status.toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="Source"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('source', value)}
            >
              {Object.values(LeadSource).map((source) => (
                <Option key={source} value={source}>
                  {source.replace('_', ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="Priority"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('priority', value)}
            >
              {Object.values(LeadPriority).map((priority) => (
                <Option key={priority} value={priority}>
                  {priority.toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="Temperature"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('temperature', value)}
            >
              {Object.values(LeadTemperature).map((temp) => (
                <Option key={temp} value={temp}>
                  {temp.toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={2}>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadLeads}
              style={{ width: '100%' }}
            >
              Refresh
            </Button>
          </Col>
        </Row>

        {/* Table */}
        <Table
          columns={columns}
          dataSource={leads}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1800 }}
          pagination={{
            current: filters.page,
            pageSize: filters.page_size,
            total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} leads`
          }}
          onChange={handleTableChange}
        />
      </Card>

      {/* Create Lead Modal */}
      <CreateLeadModal
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={() => {
          setCreateModalVisible(false);
          loadLeads();
        }}
      />
    </div>
  );
};

export default LeadsPage;
