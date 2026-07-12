/**
 * License Management Dashboard
 * Overview of all licenses with statistics, renewals, and compliance tracking
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
  Progress,
  Alert,
} from 'antd';
import {
  PlusOutlined,
  FileTextOutlined,
  CalendarOutlined,
  DollarOutlined,
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import {
  getLicenses,
  getExpiringLicenses,
  getNonCompliantLicenses,
  getStatistics,
  formatCurrency,
  formatDate,
  getLicenseStatusColor,
  getRenewalStatusColor,
  getComplianceStatusColor,
} from '../../services/legal/licenseService';

const { Search } = Input;
const { Option } = Select;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

const LicenseDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [licenses, setLicenses] = useState([]);
  const [expiringLicenses, setExpiringLicenses] = useState([]);
  const [nonCompliantLicenses, setNonCompliantLicenses] = useState([]);
  const [totalLicenses, setTotalLicenses] = useState(0);
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    status: null,
    license_type: null,
    renewal_status: null,
    compliance_status: null,
    search_query: null,
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

  // Fetch licenses
  const fetchLicenses = async () => {
    setLoading(true);
    try {
      const response = await getLicenses(filters);
      if (response.success) {
        setLicenses(response.data.items);
        setTotalLicenses(response.data.total);
      }
    } catch (error) {
      message.error('Failed to fetch licenses');
    } finally {
      setLoading(false);
    }
  };

  // Fetch expiring licenses
  const fetchExpiringLicenses = async () => {
    try {
      const response = await getExpiringLicenses(30);
      if (response.success) {
        setExpiringLicenses(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch expiring licenses');
    }
  };

  // Fetch non-compliant licenses
  const fetchNonCompliantLicenses = async () => {
    try {
      const response = await getNonCompliantLicenses();
      if (response.success) {
        setNonCompliantLicenses(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch non-compliant licenses');
    }
  };

  useEffect(() => {
    fetchStatistics();
    fetchExpiringLicenses();
    fetchNonCompliantLicenses();
  }, []);

  useEffect(() => {
    fetchLicenses();
  }, [filters]);

  // Handle search
  const handleSearch = (value) => {
    setFilters({ ...filters, search_query: value, page: 1 });
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value, page: 1 });
  };

  // Handle pagination
  const handleTableChange = (pagination) => {
    setFilters({
      ...filters,
      page: pagination.current,
      page_size: pagination.pageSize,
    });
  };

  // Calculate days until expiry color
  const getDaysUntilExpiryColor = (days) => {
    if (days === null) return 'default';
    if (days < 0) return 'red';
    if (days <= 7) return 'red';
    if (days <= 30) return 'orange';
    if (days <= 60) return 'gold';
    return 'green';
  };

  // Licenses table columns
  const licenseColumns = [
    {
      title: 'License Number',
      dataIndex: 'license_number',
      key: 'license_number',
      fixed: 'left',
      width: 150,
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/legal/licenses/${record.id}`)}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'License Name',
      dataIndex: 'license_name',
      key: 'license_name',
      width: 250,
      ellipsis: true,
    },
    {
      title: 'Type',
      dataIndex: 'license_type',
      key: 'license_type',
      width: 150,
      render: (type) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag color={getLicenseStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Issuing Authority',
      dataIndex: 'issuing_authority',
      key: 'issuing_authority',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Issue Date',
      dataIndex: 'issue_date',
      key: 'issue_date',
      width: 120,
      render: (date) => formatDate(date),
    },
    {
      title: 'Expiry Date',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      width: 120,
      render: (date, record) => (
        <Space direction="vertical" size="small">
          <span>{date ? formatDate(date) : 'Perpetual'}</span>
          {record.days_until_expiry !== null && (
            <Tag color={getDaysUntilExpiryColor(record.days_until_expiry)}>
              {record.days_until_expiry < 0
                ? `Expired ${Math.abs(record.days_until_expiry)} days ago`
                : `${record.days_until_expiry} days left`}
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: 'Renewal Status',
      dataIndex: 'renewal_status',
      key: 'renewal_status',
      width: 150,
      render: (status) => (
        <Tag color={getRenewalStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Compliance Status',
      dataIndex: 'compliance_status',
      key: 'compliance_status',
      width: 150,
      render: (status) => (
        <Tag color={getComplianceStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Criticality',
      dataIndex: 'criticality_level',
      key: 'criticality_level',
      width: 100,
      render: (level) => {
        if (!level) return '-';
        const colors = {
          Low: 'green',
          Medium: 'blue',
          High: 'orange',
          Critical: 'red',
        };
        return <Tag color={colors[level]}>{level}</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            onClick={() => navigate(`/legal/licenses/${record.id}`)}
          >
            View
          </Button>
          {record.requires_renewal_action && (
            <Button
              size="small"
              type="primary"
              onClick={() => navigate(`/legal/licenses/${record.id}/renew`)}
            >
              Renew
            </Button>
          )}
        </Space>
      ),
    },
  ];

  // Expiring licenses columns
  const expiringColumns = [
    {
      title: 'License',
      dataIndex: 'license_name',
      key: 'license_name',
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/legal/licenses/${record.id}`)}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'Number',
      dataIndex: 'license_number',
      key: 'license_number',
    },
    {
      title: 'Type',
      dataIndex: 'license_type',
      key: 'license_type',
      render: (type) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Expiry Date',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      render: (date) => formatDate(date),
    },
    {
      title: 'Days Left',
      dataIndex: 'days_until_expiry',
      key: 'days_until_expiry',
      render: (days) => (
        <Tag color={getDaysUntilExpiryColor(days)}>
          {days < 0 ? `Expired` : `${days} days`}
        </Tag>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          size="small"
          type="primary"
          onClick={() => navigate(`/legal/licenses/${record.id}/renew`)}
        >
          Initiate Renewal
        </Button>
      ),
    },
  ];

  // Non-compliant licenses columns
  const nonCompliantColumns = [
    {
      title: 'License',
      dataIndex: 'license_name',
      key: 'license_name',
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/legal/licenses/${record.id}`)}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'Number',
      dataIndex: 'license_number',
      key: 'license_number',
    },
    {
      title: 'Type',
      dataIndex: 'license_type',
      key: 'license_type',
      render: (type) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Compliance Status',
      dataIndex: 'compliance_status',
      key: 'compliance_status',
      render: (status) => (
        <Tag color={getComplianceStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Last Check',
      dataIndex: 'last_compliance_check_date',
      key: 'last_compliance_check_date',
      render: (date) => (date ? formatDate(date) : '-'),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          size="small"
          type="primary"
          onClick={() =>
            navigate(`/legal/licenses/${record.id}/compliance-check`)
          }
        >
          Check Compliance
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1 style={{ margin: 0 }}>License Management</h1>
          <p style={{ margin: 0, color: '#666' }}>
            License register, renewal reminders, and compliance tracking
          </p>
        </Col>
        <Col>
          <Space>
            <Button icon={<ExportOutlined />}>Export</Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/legal/licenses/new')}
            >
              Add License
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Alert for expiring/expired licenses */}
      {expiringLicenses.length > 0 && (
        <Alert
          message="License Renewals Required"
          description={`${expiringLicenses.length} license(s) are expiring soon or have expired. Please review and initiate renewal process.`}
          type="warning"
          icon={<WarningOutlined />}
          showIcon
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Alert for non-compliant licenses */}
      {nonCompliantLicenses.length > 0 && (
        <Alert
          message="Compliance Issues Detected"
          description={`${nonCompliantLicenses.length} license(s) have compliance issues. Please review and take corrective action.`}
          type="error"
          icon={<CloseCircleOutlined />}
          showIcon
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Statistics Cards */}
      {statistics && (
        <>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Total Licenses"
                  value={statistics.total_licenses}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Active Licenses"
                  value={statistics.active_licenses}
                  valueStyle={{ color: '#52c41a' }}
                  prefix={<CheckCircleOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Expiring Soon"
                  value={statistics.expiring_soon}
                  valueStyle={{ color: '#faad14' }}
                  prefix={<WarningOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Expired"
                  value={statistics.expired_licenses}
                  valueStyle={{ color: '#ff4d4f' }}
                  prefix={<CloseCircleOutlined />}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Pending Renewals"
                  value={statistics.pending_renewals}
                  valueStyle={{ color: '#1890ff' }}
                  prefix={<SyncOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Non-Compliant"
                  value={statistics.non_compliant_licenses}
                  valueStyle={{ color: '#ff4d4f' }}
                  prefix={<CloseCircleOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Renewal Fees Due"
                  value={formatCurrency(statistics.total_renewal_fees_due)}
                  prefix={<DollarOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Avg Renewal Time"
                  value={Math.round(statistics.average_renewal_time_days)}
                  suffix="days"
                  prefix={<CalendarOutlined />}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Main Content Tabs */}
      <Card>
        <Tabs defaultActiveKey="all">
          <TabPane tab="All Licenses" key="all">
            {/* Filters */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col xs={24} sm={12} md={6}>
                <Search
                  placeholder="Search licenses..."
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
                  <Option value="active">Active</Option>
                  <Option value="pending_renewal">Pending Renewal</Option>
                  <Option value="expired">Expired</Option>
                  <Option value="suspended">Suspended</Option>
                  <Option value="cancelled">Cancelled</Option>
                </Select>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Filter by Type"
                  allowClear
                  onChange={(value) =>
                    handleFilterChange('license_type', value)
                  }
                >
                  <Option value="nbfc_registration">NBFC Registration</Option>
                  <Option value="rbi_license">RBI License</Option>
                  <Option value="business_license">Business License</Option>
                  <Option value="professional_license">
                    Professional License
                  </Option>
                  <Option value="regulatory">Regulatory</Option>
                </Select>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Compliance Status"
                  allowClear
                  onChange={(value) =>
                    handleFilterChange('compliance_status', value)
                  }
                >
                  <Option value="compliant">Compliant</Option>
                  <Option value="non_compliant">Non-Compliant</Option>
                  <Option value="partially_compliant">
                    Partially Compliant
                  </Option>
                  <Option value="review_required">Review Required</Option>
                </Select>
              </Col>
            </Row>

            {/* Licenses Table */}
            <Table
              columns={licenseColumns}
              dataSource={licenses}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1800 }}
              pagination={{
                current: filters.page,
                pageSize: filters.page_size,
                total: totalLicenses,
                showSizeChanger: true,
                showTotal: (total) => `Total ${total} licenses`,
              }}
              onChange={handleTableChange}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <WarningOutlined />
                Expiring Soon ({expiringLicenses.length})
              </span>
            }
            key="expiring"
          >
            <Table
              columns={expiringColumns}
              dataSource={expiringLicenses}
              rowKey="id"
              pagination={false}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <CloseCircleOutlined />
                Non-Compliant ({nonCompliantLicenses.length})
              </span>
            }
            key="non-compliant"
          >
            <Table
              columns={nonCompliantColumns}
              dataSource={nonCompliantLicenses}
              rowKey="id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default LicenseDashboard;
