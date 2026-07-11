/**
 * Opportunity Detail Page
 * Comprehensive view with stage tracking, activities, products, and competitors
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Descriptions,
  Tag,
  Button,
  Space,
  Timeline,
  Table,
  Tabs,
  Progress,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  message,
  Divider,
  Steps,
  Badge,
  Statistic
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  PhoneOutlined,
  MailOutlined,
  DollarOutlined,
  CalendarOutlined,
  UserOutlined,
  RiseOutlined,
  FallOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import moment from 'moment';
import opportunityService from '../../services/opportunity.service';
import {
  Opportunity,
  OpportunityStage,
  OpportunityPriority,
  StageTransitionRequest,
  OpportunityActivity,
  OpportunityProduct,
  OpportunityCompetitor,
  StageHistory,
  OpportunityActivityCreate,
  ActivityOutcome
} from '../../types/crm.types';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;
const { Step } = Steps;

const OpportunityDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [stageHistory, setStageHistory] = useState<StageHistory[]>([]);
  const [activities, setActivities] = useState<OpportunityActivity[]>([]);
  const [products, setProducts] = useState<OpportunityProduct[]>([]);
  const [competitors, setCompetitors] = useState<OpportunityCompetitor[]>([]);
  const [loading, setLoading] = useState(false);
  const [stageModalVisible, setStageModalVisible] = useState(false);
  const [activityModalVisible, setActivityModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [activityForm] = Form.useForm();

  useEffect(() => {
    if (id) {
      loadOpportunity();
      loadStageHistory();
      loadActivities();
      loadProducts();
      loadCompetitors();
    }
  }, [id]);

  const loadOpportunity = async () => {
    setLoading(true);
    try {
      const data = await opportunityService.getOpportunity(Number(id));
      setOpportunity(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load opportunity');
    } finally {
      setLoading(false);
    }
  };

  const loadStageHistory = async () => {
    try {
      const data = await opportunityService.getStageHistory(Number(id));
      setStageHistory(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load stage history');
    }
  };

  const loadActivities = async () => {
    try {
      const response = await opportunityService.getActivities(Number(id));
      setActivities(response.items);
    } catch (error: any) {
      message.error(error.message || 'Failed to load activities');
    }
  };

  const loadProducts = async () => {
    try {
      const data = await opportunityService.getProducts(Number(id));
      setProducts(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load products');
    }
  };

  const loadCompetitors = async () => {
    try {
      const data = await opportunityService.getCompetitors(Number(id));
      setCompetitors(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load competitors');
    }
  };

  const handleStageTransition = async (values: any) => {
    try {
      const request: StageTransitionRequest = {
        to_stage: values.to_stage,
        win_probability: values.win_probability,
        change_reason: values.change_reason,
        notes: values.notes
      };
      
      await opportunityService.transitionStage(Number(id), request);
      message.success('Stage updated successfully');
      setStageModalVisible(false);
      form.resetFields();
      loadOpportunity();
      loadStageHistory();
    } catch (error: any) {
      message.error(error.message || 'Failed to update stage');
    }
  };

  const handleCreateActivity = async (values: any) => {
    try {
      const activityData: OpportunityActivityCreate = {
        opportunity_id: Number(id),
        activity_type: values.activity_type,
        activity_title: values.activity_title,
        activity_description: values.activity_description,
        activity_date: values.activity_date?.toISOString(),
        duration_minutes: values.duration_minutes,
        outcome: values.outcome,
        outcome_details: values.outcome_details,
        next_action: values.next_action
      };
      
      await opportunityService.createActivity(activityData);
      message.success('Activity logged successfully');
      setActivityModalVisible(false);
      activityForm.resetFields();
      loadActivities();
      loadOpportunity();
    } catch (error: any) {
      message.error(error.message || 'Failed to log activity');
    }
  };

  const formatCurrency = (amount: number, currency: string = 'INR'): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
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

  const getStageSteps = () => {
    const stages = [
      OpportunityStage.PROSPECTING,
      OpportunityStage.QUALIFICATION,
      OpportunityStage.NEEDS_ANALYSIS,
      OpportunityStage.PROPOSAL,
      OpportunityStage.NEGOTIATION
    ];
    
    if (!opportunity) return 0;
    
    const currentIndex = stages.indexOf(opportunity.current_stage);
    return currentIndex >= 0 ? currentIndex : 0;
  };

  if (loading || !opportunity) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Loading...</div>;
  }

  const isOverdue = new Date(opportunity.expected_close_date) < new Date() && opportunity.is_active;

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/crm/opportunities')}
              >
                Back
              </Button>
              <div>
                <h2 style={{ margin: 0 }}>{opportunity.name}</h2>
                <div style={{ color: '#888', fontSize: '14px' }}>
                  {opportunity.opportunity_code}
                </div>
              </div>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<EditOutlined />}
                onClick={() => navigate(`/crm/opportunities/${id}/edit`)}
              >
                Edit
              </Button>
              {opportunity.is_active && (
                <>
                  <Button
                    type="primary"
                    icon={<RiseOutlined />}
                    onClick={() => setStageModalVisible(true)}
                  >
                    Change Stage
                  </Button>
                  <Button
                    icon={<CheckCircleOutlined />}
                    style={{ color: '#52c41a', borderColor: '#52c41a' }}
                    onClick={() => {
                      Modal.confirm({
                        title: 'Mark as Won',
                        content: 'Mark this opportunity as won?',
                        onOk: async () => {
                          await opportunityService.markWon(Number(id), {
                            won_value: opportunity.estimated_value,
                            won_reason: 'Deal closed successfully'
                          });
                          message.success('Opportunity marked as won');
                          loadOpportunity();
                        }
                      });
                    }}
                  >
                    Mark Won
                  </Button>
                  <Button
                    icon={<CloseCircleOutlined />}
                    danger
                    onClick={() => {
                      Modal.confirm({
                        title: 'Mark as Lost',
                        content: 'Mark this opportunity as lost?',
                        onOk: async () => {
                          await opportunityService.markLost(Number(id), {
                            loss_reason: 'price_too_high' as any,
                            loss_reason_details: 'Price was too high'
                          });
                          message.success('Opportunity marked as lost');
                          loadOpportunity();
                        }
                      });
                    }}
                  >
                    Mark Lost
                  </Button>
                </>
              )}
            </Space>
          </Col>
        </Row>
      </Card>


      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Estimated Value"
              value={opportunity.estimated_value}
              prefix="₹"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Win Probability"
              value={opportunity.win_probability}
              suffix="%"
              valueStyle={{ color: opportunity.win_probability >= 70 ? '#52c41a' : '#faad14' }}
            />
            <Progress
              percent={opportunity.win_probability}
              showInfo={false}
              strokeColor={opportunity.win_probability >= 70 ? '#52c41a' : '#faad14'}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Days in Pipeline"
              value={opportunity.days_in_pipeline}
              suffix="days"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Expected Close"
              value={moment(opportunity.expected_close_date).format('MMM DD, YYYY')}
              valueStyle={{
                fontSize: '20px',
                color: isOverdue ? '#ff4d4f' : '#52c41a'
              }}
              prefix={isOverdue ? <WarningOutlined /> : <CalendarOutlined />}
            />
            {isOverdue && (
              <div style={{ marginTop: 8, color: '#ff4d4f', fontSize: '12px' }}>
                Overdue by {moment().diff(moment(opportunity.expected_close_date), 'days')} days
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Pipeline Progress */}
      {opportunity.is_active && !opportunity.is_won && !opportunity.is_lost && (
        <Card title="Pipeline Progress" style={{ marginBottom: '16px' }}>
          <Steps current={getStageSteps()} style={{ marginBottom: '24px' }}>
            <Step title="Prospecting" />
            <Step title="Qualification" />
            <Step title="Needs Analysis" />
            <Step title="Proposal" />
            <Step title="Negotiation" />
          </Steps>
          <div style={{ textAlign: 'center' }}>
            <Tag color={getStageColor(opportunity.current_stage)} style={{ fontSize: '16px', padding: '8px 16px' }}>
              Current Stage: {opportunity.current_stage.replace(/_/g, ' ').toUpperCase()}
            </Tag>
            <div style={{ marginTop: 8, color: '#888' }}>
              {opportunity.days_in_current_stage} days in current stage
            </div>
          </div>
        </Card>
      )}

      {/* Status Banner */}
      {(opportunity.is_won || opportunity.is_lost) && (
        <Card style={{ marginBottom: '16px', backgroundColor: opportunity.is_won ? '#f6ffed' : '#fff1f0' }}>
          <Row align="middle" gutter={16}>
            <Col>
              {opportunity.is_won ? (
                <TrophyOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
              ) : (
                <CloseCircleOutlined style={{ fontSize: '48px', color: '#ff4d4f' }} />
              )}
            </Col>
            <Col flex={1}>
              <h3 style={{ margin: 0, color: opportunity.is_won ? '#52c41a' : '#ff4d4f' }}>
                {opportunity.is_won ? 'Opportunity Won!' : 'Opportunity Lost'}
              </h3>
              <div style={{ marginTop: 4 }}>
                {opportunity.is_won && opportunity.won_value && (
                  <div>Won Value: {formatCurrency(opportunity.won_value, opportunity.currency)}</div>
                )}
                {opportunity.is_lost && opportunity.loss_reason && (
                  <div>Reason: {opportunity.loss_reason.replace(/_/g, ' ')}</div>
                )}
                {opportunity.actual_close_date && (
                  <div style={{ color: '#888', fontSize: '12px' }}>
                    Closed on: {moment(opportunity.actual_close_date).format('MMM DD, YYYY')}
                  </div>
                )}
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Card>
        <Tabs defaultActiveKey="details">
          <TabPane tab="Details" key="details">
            <Row gutter={16}>
              <Col xs={24} md={12}>
                <Descriptions title="Opportunity Information" bordered column={1}>
                  <Descriptions.Item label="Type">
                    {opportunity.opportunity_type.replace(/_/g, ' ').toUpperCase()}
                  </Descriptions.Item>
                  <Descriptions.Item label="Source">
                    {opportunity.source.replace(/_/g, ' ').toUpperCase()}
                  </Descriptions.Item>
                  <Descriptions.Item label="Priority">
                    <Tag color={getPriorityColor(opportunity.priority)}>
                      {opportunity.priority.toUpperCase()}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="Owner">
                    <UserOutlined /> {opportunity.owner_name || 'Unassigned'}
                  </Descriptions.Item>
                  <Descriptions.Item label="Description">
                    {opportunity.description || '-'}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
              <Col xs={24} md={12}>
                <Descriptions title="Contact Information" bordered column={1}>
                  <Descriptions.Item label="Contact Name">
                    {opportunity.contact_name}
                  </Descriptions.Item>
                  <Descriptions.Item label="Company">
                    {opportunity.company_name || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="Mobile">
                    <Space>
                      {opportunity.contact_mobile}
                      <Button
                        type="link"
                        size="small"
                        icon={<PhoneOutlined />}
                        onClick={() => window.location.href = `tel:${opportunity.contact_mobile}`}
                      >
                        Call
                      </Button>
                    </Space>
                  </Descriptions.Item>
                  <Descriptions.Item label="Email">
                    {opportunity.contact_email ? (
                      <Space>
                        {opportunity.contact_email}
                        <Button
                          type="link"
                          size="small"
                          icon={<MailOutlined />}
                          onClick={() => window.location.href = `mailto:${opportunity.contact_email}`}
                        >
                          Email
                        </Button>
                      </Space>
                    ) : '-'}
                  </Descriptions.Item>
                </Descriptions>

                <Divider />

                <Descriptions title="Qualification (BANT)" bordered column={1}>
                  <Descriptions.Item label="Budget">
                    {opportunity.budget_confirmed ? (
                      <Tag color="green">Confirmed</Tag>
                    ) : (
                      <Tag color="orange">Not Confirmed</Tag>
                    )}
                  </Descriptions.Item>
                  <Descriptions.Item label="Authority">
                    {opportunity.authority_confirmed ? (
                      <Tag color="green">Confirmed</Tag>
                    ) : (
                      <Tag color="orange">Not Confirmed</Tag>
                    )}
                  </Descriptions.Item>
                  <Descriptions.Item label="Need">
                    {opportunity.need_confirmed ? (
                      <Tag color="green">Confirmed</Tag>
                    ) : (
                      <Tag color="orange">Not Confirmed</Tag>
                    )}
                  </Descriptions.Item>
                  <Descriptions.Item label="Timeline">
                    {opportunity.timeline_confirmed ? (
                      <Tag color="green">Confirmed</Tag>
                    ) : (
                      <Tag color="orange">Not Confirmed</Tag>
                    )}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>

            {opportunity.next_step && (
              <>
                <Divider />
                <Descriptions title="Next Steps" bordered column={1}>
                  <Descriptions.Item label="Next Action">
                    {opportunity.next_step}
                  </Descriptions.Item>
                </Descriptions>
              </>
            )}
          </TabPane>

          <TabPane tab={`Activities (${activities.length})`} key="activities">
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setActivityModalVisible(true)}
              style={{ marginBottom: '16px' }}
            >
              Log Activity
            </Button>

            <Timeline>
              {activities.map((activity) => (
                <Timeline.Item
                  key={activity.id}
                  color={activity.is_key_milestone ? 'green' : 'blue'}
                  dot={activity.is_key_milestone ? <TrophyOutlined /> : undefined}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>{activity.activity_title}</div>
                    <div style={{ color: '#888', fontSize: '12px', marginTop: 4 }}>
                      {moment(activity.activity_date).format('MMM DD, YYYY HH:mm')} • {activity.performed_by_name}
                    </div>
                    {activity.activity_description && (
                      <div style={{ marginTop: 8 }}>{activity.activity_description}</div>
                    )}
                    {activity.outcome && (
                      <Tag color={activity.outcome === 'positive' ? 'green' : 'default'} style={{ marginTop: 8 }}>
                        {activity.outcome.toUpperCase()}
                      </Tag>
                    )}
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </TabPane>

          <TabPane tab={`Products (${products.length})`} key="products">
            <Table
              dataSource={products}
              rowKey="id"
              columns={[
                {
                  title: 'Product',
                  dataIndex: 'product_name',
                  key: 'product_name'
                },
                {
                  title: 'Quantity',
                  dataIndex: 'quantity',
                  key: 'quantity',
                  width: 100
                },
                {
                  title: 'Unit Price',
                  dataIndex: 'unit_price',
                  key: 'unit_price',
                  width: 150,
                  render: (price) => formatCurrency(price, opportunity.currency)
                },
                {
                  title: 'Discount',
                  dataIndex: 'discount_percent',
                  key: 'discount_percent',
                  width: 100,
                  render: (discount) => `${discount}%`
                },
                {
                  title: 'Line Total',
                  dataIndex: 'line_total',
                  key: 'line_total',
                  width: 150,
                  render: (total) => formatCurrency(total, opportunity.currency)
                }
              ]}
              pagination={false}
              summary={(pageData) => {
                const total = pageData.reduce((sum, product) => sum + product.line_total, 0);
                return (
                  <Table.Summary.Row>
                    <Table.Summary.Cell index={0} colSpan={4} align="right">
                      <strong>Total:</strong>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={1}>
                      <strong>{formatCurrency(total, opportunity.currency)}</strong>
                    </Table.Summary.Cell>
                  </Table.Summary.Row>
                );
              }}
            />
          </TabPane>

          <TabPane tab={`Competitors (${competitors.length})`} key="competitors">
            <Table
              dataSource={competitors}
              rowKey="id"
              columns={[
                {
                  title: 'Competitor',
                  dataIndex: 'competitor_name',
                  key: 'competitor_name'
                },
                {
                  title: 'Product',
                  dataIndex: 'competitor_product',
                  key: 'competitor_product'
                },
                {
                  title: 'Position',
                  dataIndex: 'position',
                  key: 'position',
                  render: (position) => (
                    <Tag color={position === 'strong' ? 'red' : position === 'weak' ? 'green' : 'default'}>
                      {position.toUpperCase()}
                    </Tag>
                  )
                },
                {
                  title: 'Price',
                  dataIndex: 'competitor_price',
                  key: 'competitor_price',
                  render: (price) => price ? formatCurrency(price, opportunity.currency) : '-'
                }
              ]}
              pagination={false}
            />
          </TabPane>

          <TabPane tab="Stage History" key="stage-history">
            <Timeline>
              {stageHistory.map((history) => (
                <Timeline.Item
                  key={history.id}
                  color={history.is_forward ? 'green' : 'red'}
                  dot={history.is_forward ? <RiseOutlined /> : <FallOutlined />}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>
                      {history.from_stage && `${history.from_stage.replace(/_/g, ' ').toUpperCase()} → `}
                      {history.to_stage.replace(/_/g, ' ').toUpperCase()}
                    </div>
                    <div style={{ color: '#888', fontSize: '12px', marginTop: 4 }}>
                      {moment(history.stage_entered_date).format('MMM DD, YYYY HH:mm')}
                      {history.changed_by_name && ` • ${history.changed_by_name}`}
                    </div>
                    {history.days_in_stage !== null && (
                      <div style={{ marginTop: 4 }}>
                        Duration: {history.days_in_stage} days
                      </div>
                    )}
                    {history.probability_after !== null && (
                      <div style={{ marginTop: 4 }}>
                        Probability: {history.probability_before}% → {history.probability_after}%
                      </div>
                    )}
                    {history.notes && (
                      <div style={{ marginTop: 8, fontStyle: 'italic' }}>
                        {history.notes}
                      </div>
                    )}
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </TabPane>
        </Tabs>
      </Card>

      {/* Stage Transition Modal */}
      <Modal
        title="Change Opportunity Stage"
        visible={stageModalVisible}
        onCancel={() => {
          setStageModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleStageTransition}
        >
          <Form.Item
            label="New Stage"
            name="to_stage"
            rules={[{ required: true, message: 'Please select a stage' }]}
          >
            <Select placeholder="Select stage">
              {Object.values(OpportunityStage).filter(s => 
                s !== OpportunityStage.CLOSED_WON && s !== OpportunityStage.CLOSED_LOST
              ).map(stage => (
                <Option key={stage} value={stage}>
                  {stage.replace(/_/g, ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Win Probability (%)"
            name="win_probability"
          >
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="Reason for Change"
            name="change_reason"
          >
            <Input placeholder="Why is this stage changing?" />
          </Form.Item>

          <Form.Item
            label="Notes"
            name="notes"
          >
            <TextArea rows={3} placeholder="Additional notes..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Activity Modal */}
      <Modal
        title="Log Activity"
        visible={activityModalVisible}
        onCancel={() => {
          setActivityModalVisible(false);
          activityForm.resetFields();
        }}
        onOk={() => activityForm.submit()}
        width={600}
      >
        <Form
          form={activityForm}
          layout="vertical"
          onFinish={handleCreateActivity}
        >
          <Form.Item
            label="Activity Type"
            name="activity_type"
            rules={[{ required: true, message: 'Please select activity type' }]}
          >
            <Select placeholder="Select type">
              <Option value="call">Phone Call</Option>
              <Option value="email">Email</Option>
              <Option value="meeting">Meeting</Option>
              <Option value="demo">Product Demo</Option>
              <Option value="proposal">Proposal Sent</Option>
              <Option value="negotiation">Negotiation</Option>
              <Option value="other">Other</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Title"
            name="activity_title"
            rules={[{ required: true, message: 'Please enter title' }]}
          >
            <Input placeholder="Brief title of the activity" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="activity_description"
          >
            <TextArea rows={3} placeholder="Detailed description..." />
          </Form.Item>

          <Form.Item
            label="Activity Date"
            name="activity_date"
          >
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="Duration (minutes)"
            name="duration_minutes"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="Outcome"
            name="outcome"
          >
            <Select placeholder="Select outcome">
              <Option value={ActivityOutcome.POSITIVE}>Positive</Option>
              <Option value={ActivityOutcome.NEUTRAL}>Neutral</Option>
              <Option value={ActivityOutcome.NEGATIVE}>Negative</Option>
              <Option value={ActivityOutcome.NO_ANSWER}>No Answer</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Next Action"
            name="next_action"
          >
            <TextArea rows={2} placeholder="What needs to happen next?" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OpportunityDetailPage;
