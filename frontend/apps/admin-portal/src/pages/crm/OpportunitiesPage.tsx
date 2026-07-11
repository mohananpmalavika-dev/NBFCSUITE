/**
 * Opportunities List Page
 * Main page for viewing and managing opportunities with pipeline view
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
  Badge,
  Tabs,
  Statistic
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  MoreOutlined,
  DollarOutlined,
  PhoneOutlined,
  MailOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  AppstoreOutlined,
  BarsOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import opportunityService from '../../services/opportunity.service';
import {
  Opportunity,
  OpportunityStage,
  OpportunitySource,
  OpportunityPriority,
  OpportunityType,
  OpportunityFilters
} from '../../types/crm.types';

const { Search } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

type ViewMode = 'table' | 'kanban';

const OpportunitiesPage: React.FC = () => {
  const navigate = useNavigate();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [filters, setFilters] = useState<OpportunityFilters>({
    page: 1,
    page_size: 20,
    is_active: true
  });

  useEffect(() => {
    loadOpportunities();
  }, [filters]);

  const loadOpportunities = async () => {
    setLoading(true);
    try {
      const response = await opportunityService.listOpportunities(filters);
      setOpportunities(response.items);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.message || 'Failed to load opportunities');
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

  const getStageColor = (stage: OpportunityStage): string => {
    const colors: Record<OpportunityStage, string> = {
      [OpportunityStage.PROSPECTING]: 'default',
      [OpportunityStage.QUALIFICATION]: 'blue',
      [OpportunityStage.NEEDS_ANALYSIS]: 'cyan',
      [OpportunityStage.PROPOSAL]: 'orange',
      [OpportunityStage.NEGOTIATION]: 'gold',
      [OpportunityStage.CLOSED_WON]: 'green',
      [OpportunityStage.CLOSED_LOST]: 'red'
    };
    return colors[stage] || 'default';
  };

  const getPriorityColor = (priority: OpportunityPriority): string => {
    const colors: Record<OpportunityPriority, string> = {
      [OpportunityPriority.CRITICAL]: 'red',
      [OpportunityPriority.HIGH]: 'orange',
      [OpportunityPriority.MEDIUM]: 'blue',
      [OpportunityPriority.LOW]: 'default'
    };
    return colors[priority];
  };

  const formatCurrency = (amount: number, currency: string = 'INR'): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleRowAction = (action: string, opportunity: Opportunity) => {
    switch (action) {
      case 'view':
        navigate(`/crm/opportunities/${opportunity.id}`);
        break;
      case 'edit':
        navigate(`/crm/opportunities/${opportunity.id}/edit`);
        break;
      case 'call':
        window.location.href = `tel:${opportunity.contact_mobile}`;
        break;
      case 'email':
        if (opportunity.contact_email) {
          window.location.href = `mailto:${opportunity.contact_email}`;
        }
        break;
      case 'mark-won':
        handleMarkWon(opportunity);
        break;
      case 'mark-lost':
        handleMarkLost(opportunity);
        break;
      default:
        break;
    }
  };

  const handleMarkWon = (opportunity: Opportunity) => {
    Modal.confirm({
      title: 'Mark Opportunity as Won',
      content: 'Are you sure you want to mark this opportunity as won?',
      onOk: async () => {
        try {
          await opportunityService.markWon(opportunity.id, {
            won_value: opportunity.estimated_value,
            won_reason: 'Deal closed successfully'
          });
          message.success('Opportunity marked as won');
          loadOpportunities();
        } catch (error: any) {
          message.error(error.message || 'Failed to mark opportunity as won');
        }
      }
    });
  };

  const handleMarkLost = (opportunity: Opportunity) => {
    // Would typically show a modal to collect loss reason
    Modal.confirm({
      title: 'Mark Opportunity as Lost',
      content: 'Are you sure you want to mark this opportunity as lost?',
      onOk: async () => {
        try {
          await opportunityService.markLost(opportunity.id, {
            loss_reason: 'price_too_high' as any,
            loss_reason_details: 'Price was too high for customer budget'
          });
          message.success('Opportunity marked as lost');
          loadOpportunities();
        } catch (error: any) {
          message.error(error.message || 'Failed to mark opportunity as lost');
        }
      }
    });
  };

  const getActionMenu = (opportunity: Opportunity) => (
    <Menu>
      <Menu.Item
        key="view"
        icon={<EyeOutlined />}
        onClick={() => handleRowAction('view', opportunity)}
      >
        View Details
      </Menu.Item>
      <Menu.Item
        key="edit"
        icon={<EditOutlined />}
        onClick={() => handleRowAction('edit', opportunity)}
      >
        Edit
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item
        key="call"
        icon={<PhoneOutlined />}
        onClick={() => handleRowAction('call', opportunity)}
      >
        Call
      </Menu.Item>
      {opportunity.contact_email && (
        <Menu.Item
          key="email"
          icon={<MailOutlined />}
          onClick={() => handleRowAction('email', opportunity)}
        >
          Email
        </Menu.Item>
      )}
      <Menu.Divider />
      {opportunity.is_active && (
        <>
          <Menu.Item
            key="mark-won"
            icon={<CheckCircleOutlined />}
            onClick={() => handleRowAction('mark-won', opportunity)}
          >
            Mark as Won
          </Menu.Item>
          <Menu.Item
            key="mark-lost"
            icon={<CloseCircleOutlined />}
            onClick={() => handleRowAction('mark-lost', opportunity)}
          >
            Mark as Lost
          </Menu.Item>
        </>
      )}
    </Menu>
  );


  const columns: ColumnsType<Opportunity> = [
    {
      title: 'Opportunity',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      fixed: 'left',
      render: (name: string, record: Opportunity) => (
        <div>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>
            <a onClick={() => navigate(`/crm/opportunities/${record.id}`)}>
              {name}
            </a>
          </div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            {record.opportunity_code}
          </div>
        </div>
      )
    },
    {
      title: 'Contact',
      dataIndex: 'contact_name',
      key: 'contact_name',
      width: 200,
      render: (name: string, record: Opportunity) => (
        <div>
          <div>{name}</div>
          {record.company_name && (
            <div style={{ fontSize: '12px', color: '#888' }}>{record.company_name}</div>
          )}
        </div>
      )
    },
    {
      title: 'Value',
      dataIndex: 'estimated_value',
      key: 'estimated_value',
      width: 150,
      align: 'right',
      render: (value: number, record: Opportunity) => (
        <div>
          <div style={{ fontWeight: 600 }}>
            {formatCurrency(value, record.currency)}
          </div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            {record.win_probability}% probability
          </div>
        </div>
      ),
      sorter: true
    },
    {
      title: 'Stage',
      dataIndex: 'current_stage',
      key: 'current_stage',
      width: 150,
      render: (stage: OpportunityStage) => (
        <Tag color={getStageColor(stage)}>
          {stage.replace(/_/g, ' ').toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: OpportunityPriority) => (
        <Tag color={getPriorityColor(priority)}>
          {priority.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Owner',
      dataIndex: 'owner_name',
      key: 'owner_name',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Expected Close',
      dataIndex: 'expected_close_date',
      key: 'expected_close_date',
      width: 120,
      render: (date: string) => {
        const closeDate = new Date(date);
        const today = new Date();
        const isOverdue = closeDate < today;
        
        return (
          <div style={{ color: isOverdue ? '#ff4d4f' : undefined }}>
            {new Date(date).toLocaleDateString()}
          </div>
        );
      }
    },
    {
      title: 'Days in Pipeline',
      dataIndex: 'days_in_pipeline',
      key: 'days_in_pipeline',
      width: 120,
      align: 'center',
      render: (days: number) => (
        <Badge count={days} style={{ backgroundColor: '#108ee9' }} />
      )
    },
    {
      title: 'Status',
      key: 'status',
      width: 100,
      render: (_: any, record: Opportunity) => {
        if (record.is_won) {
          return <Tag color="green">WON</Tag>;
        }
        if (record.is_lost) {
          return <Tag color="red">LOST</Tag>;
        }
        if (record.is_active) {
          return <Tag color="blue">ACTIVE</Tag>;
        }
        return <Tag>INACTIVE</Tag>;
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 80,
      render: (_: any, record: Opportunity) => (
        <Dropdown overlay={getActionMenu(record)} trigger={['click']}>
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      )
    }
  ];

  const renderKanbanView = () => {
    const stages = [
      OpportunityStage.PROSPECTING,
      OpportunityStage.QUALIFICATION,
      OpportunityStage.NEEDS_ANALYSIS,
      OpportunityStage.PROPOSAL,
      OpportunityStage.NEGOTIATION
    ];

    const getOpportunitiesByStage = (stage: OpportunityStage) => {
      return opportunities.filter(opp => opp.current_stage === stage);
    };

    return (
      <div style={{ display: 'flex', gap: '16px', overflowX: 'auto', padding: '16px 0' }}>
        {stages.map(stage => {
          const stageOpps = getOpportunitiesByStage(stage);
          const stageValue = stageOpps.reduce((sum, opp) => sum + opp.estimated_value, 0);
          
          return (
            <Card
              key={stage}
              title={
                <div>
                  <div>{stage.replace(/_/g, ' ').toUpperCase()}</div>
                  <div style={{ fontSize: '12px', fontWeight: 'normal', color: '#888' }}>
                    {stageOpps.length} opportunities • {formatCurrency(stageValue)}
                  </div>
                </div>
              }
              style={{ minWidth: '300px', maxWidth: '350px' }}
              bodyStyle={{ padding: '8px', maxHeight: '600px', overflowY: 'auto' }}
            >
              {stageOpps.map(opp => (
                <Card
                  key={opp.id}
                  size="small"
                  style={{ marginBottom: '8px', cursor: 'pointer' }}
                  onClick={() => navigate(`/crm/opportunities/${opp.id}`)}
                  hoverable
                >
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontWeight: 600, marginBottom: 4 }}>{opp.name}</div>
                    <div style={{ fontSize: '12px', color: '#888' }}>
                      {opp.company_name || opp.contact_name}
                    </div>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <DollarOutlined style={{ marginRight: 4 }} />
                    <span style={{ fontWeight: 600 }}>
                      {formatCurrency(opp.estimated_value, opp.currency)}
                    </span>
                    <span style={{ marginLeft: 8, fontSize: '12px', color: '#888' }}>
                      {opp.win_probability}%
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Tag color={getPriorityColor(opp.priority)} size="small">
                      {opp.priority.toUpperCase()}
                    </Tag>
                    <span style={{ fontSize: '12px', color: '#888' }}>
                      {opp.days_in_pipeline}d
                    </span>
                  </div>
                </Card>
              ))}
            </Card>
          );
        })}
      </div>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
          <Col>
            <h2>Opportunity Management</h2>
          </Col>
          <Col>
            <Space>
              <Button
                icon={viewMode === 'table' ? <AppstoreOutlined /> : <BarsOutlined />}
                onClick={() => setViewMode(viewMode === 'table' ? 'kanban' : 'table')}
              >
                {viewMode === 'table' ? 'Kanban View' : 'Table View'}
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/crm/opportunities/create')}
              >
                Create Opportunity
              </Button>
            </Space>
          </Col>
        </Row>

        {/* Summary Stats */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Total Opportunities"
                value={total}
                prefix={<DollarOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Total Value"
                value={opportunities.reduce((sum, opp) => sum + opp.estimated_value, 0)}
                prefix="₹"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Weighted Value"
                value={opportunities.reduce(
                  (sum, opp) => sum + (opp.estimated_value * opp.win_probability / 100),
                  0
                )}
                prefix="₹"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Avg Probability"
                value={
                  opportunities.length > 0
                    ? opportunities.reduce((sum, opp) => sum + opp.win_probability, 0) /
                      opportunities.length
                    : 0
                }
                suffix="%"
                precision={0}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Filters */}
        <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
          <Col xs={24} sm={12} md={6}>
            <Search
              placeholder="Search opportunities..."
              allowClear
              onSearch={handleSearch}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="Stage"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('stage', value)}
            >
              {Object.values(OpportunityStage).map((stage) => (
                <Option key={stage} value={stage}>
                  {stage.replace(/_/g, ' ').toUpperCase()}
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
              {Object.values(OpportunityPriority).map((priority) => (
                <Option key={priority} value={priority}>
                  {priority.toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="Type"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('opportunity_type', value)}
            >
              {Object.values(OpportunityType).map((type) => (
                <Option key={type} value={type}>
                  {type.replace(/_/g, ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={3}>
            <Select
              placeholder="Status"
              allowClear
              style={{ width: '100%' }}
              onChange={(value) => handleFilterChange('is_active', value)}
            >
              <Option value={true}>Active</Option>
              <Option value={false}>Closed</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={3}>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadOpportunities}
              style={{ width: '100%' }}
            >
              Refresh
            </Button>
          </Col>
        </Row>

        {/* Content - Table or Kanban */}
        {viewMode === 'table' ? (
          <Table
            columns={columns}
            dataSource={opportunities}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1800 }}
            pagination={{
              current: filters.page,
              pageSize: filters.page_size,
              total: total,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} opportunities`
            }}
            onChange={handleTableChange}
          />
        ) : (
          renderKanbanView()
        )}
      </Card>
    </div>
  );
};

export default OpportunitiesPage;
