/**
 * Litigation Management Dashboard
 * Overview of all litigation cases with statistics and quick actions
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  Tag,
  Space,
  Input,
  Select,
  DatePicker,
  message,
  Spin,
  Modal,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  FileTextOutlined,
  CalendarOutlined,
  DollarOutlined,
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import {
  getCases,
  getUpcomingHearings,
  getStatistics,
  formatCurrency,
  formatDate,
  formatDateTime,
  getCaseStatusColor,
  getPriorityColor,
} from '../../services/legal/litigationService';

const { Search } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

const LitigationDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [cases, setCases] = useState([]);
  const [upcomingHearings, setUpcomingHearings] = useState([]);
  const [totalCases, setTotalCases] = useState(0);
  const [filters, setFilters] = useState({
    skip: 0,
    limit: 10,
    status: null,
    case_type: null,
    priority: null,
    search: null,
  });

  // Fetch statistics
  const fetchStatistics = async () => {
    try {
      const response = await getStatistics();
      if (response.success) {
        setStatistics(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch statistics');
    }
  };

  // Fetch cases
  const fetchCases = async () => {
    setLoading(true);
    try {
      const response = await getCases(filters);
      if (response.success) {
        setCases(response.data.cases);
        setTotalCases(response.data.total);
      }
    } catch (error) {
      message.error('Failed to fetch cases');
    } finally {
      setLoading(false);
    }
  };

  // Fetch upcoming hearings
  const fetchUpcomingHearings = async () => {
    try {
      const response = await getUpcomingHearings(30, { limit: 5 });
      if (response.success) {
        setUpcomingHearings(response.data.hearings);
      }
    } catch (error) {
      message.error('Failed to fetch upcoming hearings');
    }
  };

  useEffect(() => {
    fetchStatistics();
    fetchUpcomingHearings();
  }, []);

  useEffect(() => {
    fetchCases();
  }, [filters]);

  // Handle search
  const handleSearch = (value) => {
    setFilters({ ...filters, search: value, skip: 0 });
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value, skip: 0 });
  };

  // Handle pagination
  const handleTableChange = (pagination) => {
    setFilters({
      ...filters,
      skip: (pagination.current - 1) * pagination.pageSize,
      limit: pagination.pageSize,
    });
  };

  // Cases table columns
  const caseColumns = [
    {
      title: 'Case Number',
      dataIndex: 'case_number',
      key: 'case_number',
      fixed: 'left',
      width: 150,
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/legal/litigation/cases/${record.id}`)}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'Case Title',
      dataIndex: 'case_title',
      key: 'case_title',
      width: 300,
      ellipsis: true,
    },
    {
      title: 'Type',
      dataIndex: 'case_type',
      key: 'case_type',
      width: 120,
      render: (type) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag color={getCaseStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => (
        <Tag color={getPriorityColor(priority)}>{priority.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Court',
      dataIndex: 'court_name',
      key: 'court_name',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Filing Date',
      dataIndex: 'filing_date',
      key: 'filing_date',
      width: 120,
      render: (date) => formatDate(date),
    },
    {
      title: 'Next Hearing',
      dataIndex: 'next_hearing_date',
      key: 'next_hearing_date',
      width: 150,
      render: (date) => (date ? formatDateTime(date) : '-'),
    },
    {
      title: 'Advocate',
      dataIndex: 'primary_advocate',
      key: 'primary_advocate',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 100,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            onClick={() => navigate(`/legal/litigation/cases/${record.id}`)}
          >
            View
          </Button>
        </Space>
      ),
    },
  ];

  // Upcoming hearings table columns
  const hearingColumns = [
    {
      title: 'Case',
      dataIndex: 'case_id',
      key: 'case_id',
      render: (caseId) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/legal/litigation/cases/${caseId}`)}
        >
          View Case
        </Button>
      ),
    },
    {
      title: 'Hearing #',
      dataIndex: 'hearing_number',
      key: 'hearing_number',
    },
    {
      title: 'Type',
      dataIndex: 'hearing_type',
      key: 'hearing_type',
      render: (type) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Scheduled Date',
      dataIndex: 'scheduled_date',
      key: 'scheduled_date',
      render: (date) => formatDateTime(date),
    },
    {
      title: 'Court Room',
      dataIndex: 'court_room',
      key: 'court_room',
    },
    {
      title: 'Judge',
      dataIndex: 'judge_name',
      key: 'judge_name',
      ellipsis: true,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1 style={{ margin: 0 }}>Litigation Management</h1>
          <p style={{ margin: 0, color: '#666' }}>
            Case tracking, hearing management, and legal expense tracking
          </p>
        </Col>
        <Col>
          <Space>
            <Button icon={<ExportOutlined />}>Export</Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/legal/litigation/cases/new')}
            >
              New Case
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Statistics Cards */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Total Cases"
                value={statistics.total_cases}
                prefix={<FileTextOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Active Cases"
                value={statistics.active_cases}
                valueStyle={{ color: '#1890ff' }}
                prefix={<FileTextOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Upcoming Hearings"
                value={statistics.upcoming_hearings}
                prefix={<CalendarOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Legal Expenses"
                value={formatCurrency(statistics.total_legal_expenses)}
                prefix={<DollarOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Outcome Statistics */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Cases Won"
                value={statistics.won_cases}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Cases Lost"
                value={statistics.lost_cases}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Cases Settled"
                value={statistics.settled_cases}
                valueStyle={{ color: '#13c2c2' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Main Content Tabs */}
      <Card>
        <Tabs defaultActiveKey="cases">
          <TabPane tab="All Cases" key="cases">
            {/* Filters */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col xs={24} sm={12} md={6}>
                <Search
                  placeholder="Search cases..."
                  allowClear
                  onSearch={handleSearch}
                  prefix={<SearchOutlined />}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Filter by Status"
                  allowClear
                  onChange={(value) => handleFilterChange('status', value)}
                >
                  <Option value="filed">Filed</Option>
                  <Option value="admitted">Admitted</Option>
                  <Option value="in_progress">In Progress</Option>
                  <Option value="won">Won</Option>
                  <Option value="lost">Lost</Option>
                  <Option value="settled">Settled</Option>
                </Select>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Filter by Type"
                  allowClear
                  onChange={(value) => handleFilterChange('case_type', value)}
                >
                  <Option value="civil">Civil</Option>
                  <Option value="criminal">Criminal</Option>
                  <Option value="arbitration">Arbitration</Option>
                  <Option value="recovery">Recovery</Option>
                  <Option value="banking">Banking</Option>
                </Select>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Filter by Priority"
                  allowClear
                  onChange={(value) => handleFilterChange('priority', value)}
                >
                  <Option value="low">Low</Option>
                  <Option value="medium">Medium</Option>
                  <Option value="high">High</Option>
                  <Option value="critical">Critical</Option>
                  <Option value="urgent">Urgent</Option>
                </Select>
              </Col>
            </Row>

            {/* Cases Table */}
            <Table
              columns={caseColumns}
              dataSource={cases}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1500 }}
              pagination={{
                current: filters.skip / filters.limit + 1,
                pageSize: filters.limit,
                total: totalCases,
                showSizeChanger: true,
                showTotal: (total) => `Total ${total} cases`,
              }}
              onChange={handleTableChange}
            />
          </TabPane>

          <TabPane tab="Upcoming Hearings" key="hearings">
            <Table
              columns={hearingColumns}
              dataSource={upcomingHearings}
              rowKey="id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default LitigationDashboard;
