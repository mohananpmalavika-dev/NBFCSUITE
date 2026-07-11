/**
 * Lead Detail Page
 * Detailed view of a single lead with actions and activity tracking
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Descriptions,
  Tag,
  Button,
  Space,
  Tabs,
  Timeline,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  message,
  Spin,
  Badge,
  Divider
} from 'antd';
import {
  ArrowLeftOutlined,
  PhoneOutlined,
  MailOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UserSwitchOutlined,
  DollarOutlined,
  FireOutlined,
  PlusOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import crmService from '../../services/crm.service';
import {
  Lead,
  LeadFollowUp,
  LeadActivity,
  LeadStatus,
  LeadTemperature,
  FollowUpType,
  LeadFollowUpCreate
} from '../../types/crm.types';
import moment from 'moment';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const LeadDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [followUps, setFollowUps] = useState<LeadFollowUp[]>([]);
  const [activities, setActivities] = useState<LeadActivity[]>([]);
  const [loading, setLoading] = useState(false);
  const [followUpModalVisible, setFollowUpModalVisible] = useState(false);
  const [qualifyModalVisible, setQualifyModalVisible] = useState(false);
  const [lostModalVisible, setLostModalVisible] = useState(false);
  const [followUpForm] = Form.useForm();
  const [qualifyForm] = Form.useForm();
  const [lostForm] = Form.useForm();

  useEffect(() => {
    if (id) {
      loadLeadDetails();
      loadFollowUps();
      loadActivities();
    }
  }, [id]);

  const loadLeadDetails = async () => {
    setLoading(true);
    try {
      const data = await crmService.getLead(Number(id));
      setLead(data);
    } catch (error: any) {
      message.error(error.message || 'Failed to load lead details');
    } finally {
      setLoading(false);
    }
  };

  const loadFollowUps = async () => {
    try {
      const response = await crmService.getLeadFollowUps(Number(id));
      setFollowUps(response.items);
    } catch (error: any) {
      message.error('Failed to load follow-ups');
    }
  };

  const loadActivities = async () => {
    try {
      const response = await crmService.getLeadActivities(Number(id));
      setActivities(response.items);
    } catch (error: any) {
      message.error('Failed to load activities');
    }
  };

  const handleCreateFollowUp = async (values: any) => {
    try {
      const followUpData: LeadFollowUpCreate = {
        lead_id: Number(id),
        follow_up_type: values.follow_up_type,
        scheduled_date: values.scheduled_date.toISOString(),
        subject: values.subject,
        description: values.description
      };

      await crmService.createFollowUp(followUpData);
      message.success('Follow-up created successfully');
      followUpForm.resetFields();
      setFollowUpModalVisible(false);
      loadFollowUps();
      loadLeadDetails();
    } catch (error: any) {
      message.error(error.message || 'Failed to create follow-up');
    }
  };


  const handleQualifyLead = async (values: any) => {
    try {
      await crmService.qualifyLead(Number(id), {
        is_qualified: values.is_qualified,
        reason: values.reason
      });
      message.success(`Lead ${values.is_qualified ? 'qualified' : 'disqualified'} successfully`);
      qualifyForm.resetFields();
      setQualifyModalVisible(false);
      loadLeadDetails();
    } catch (error: any) {
      message.error(error.message || 'Failed to update lead');
    }
  };

  const handleMarkLost = async (values: any) => {
    try {
      await crmService.markLeadLost(Number(id), {
        reason: values.reason,
        remarks: values.remarks
      });
      message.success('Lead marked as lost');
      lostForm.resetFields();
      setLostModalVisible(false);
      loadLeadDetails();
    } catch (error: any) {
      message.error(error.message || 'Failed to mark lead as lost');
    }
  };

  const handleConvertLead = () => {
    Modal.confirm({
      title: 'Convert Lead to Customer',
      content: 'Are you sure you want to convert this lead to a customer?',
      onOk: async () => {
        try {
          await crmService.convertLead(Number(id), {
            create_customer: true
          });
          message.success('Lead converted successfully');
          loadLeadDetails();
        } catch (error: any) {
          message.error(error.message || 'Failed to convert lead');
        }
      }
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

  const getTemperatureIcon = (temp: LeadTemperature) => {
    const colors: Record<LeadTemperature, string> = {
      [LeadTemperature.HOT]: '#ff4d4f',
      [LeadTemperature.WARM]: '#faad14',
      [LeadTemperature.COLD]: '#1890ff'
    };
    return <FireOutlined style={{ color: colors[temp] }} />;
  };

  if (loading || !lead) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/crm/leads')}>
              Back
            </Button>
            <h2 style={{ margin: 0 }}>
              {lead.full_name} - {lead.lead_code}
            </h2>
            <Tag color={getStatusColor(lead.status)}>{lead.status.toUpperCase()}</Tag>
            <Badge
              count={lead.lead_score}
              style={{ backgroundColor: lead.lead_temperature === LeadTemperature.HOT ? '#ff4d4f' : '#1890ff' }}
            />
            {getTemperatureIcon(lead.lead_temperature)}
          </Space>
        </Col>
        <Col>
          <Space>
            <Button icon={<PhoneOutlined />} href={`tel:${lead.mobile}`}>
              Call
            </Button>
            {lead.email && (
              <Button icon={<MailOutlined />} href={`mailto:${lead.email}`}>
                Email
              </Button>
            )}
            <Button icon={<ReloadOutlined />} onClick={loadLeadDetails}>
              Refresh
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Action Buttons */}
      <Card style={{ marginBottom: '16px' }}>
        <Space wrap>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setFollowUpModalVisible(true)}
          >
            Schedule Follow-up
          </Button>
          <Button
            icon={<CheckCircleOutlined />}
            onClick={() => setQualifyModalVisible(true)}
            disabled={lead.is_qualified}
          >
            Qualify Lead
          </Button>
          <Button
            icon={<DollarOutlined />}
            onClick={handleConvertLead}
            disabled={lead.is_converted || !lead.is_qualified}
          >
            Convert to Customer
          </Button>
          <Button
            danger
            icon={<CloseCircleOutlined />}
            onClick={() => setLostModalVisible(true)}
            disabled={lead.is_lost}
          >
            Mark as Lost
          </Button>
        </Space>
      </Card>


      {/* Tabs */}
      <Tabs defaultActiveKey="details">
        <TabPane tab="Lead Details" key="details">
          <Card>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="Lead Code">{lead.lead_code}</Descriptions.Item>
              <Descriptions.Item label="Source">
                <Tag>{lead.source.replace('_', ' ').toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Full Name">{lead.full_name}</Descriptions.Item>
              <Descriptions.Item label="Mobile">{lead.mobile}</Descriptions.Item>
              <Descriptions.Item label="Email">{lead.email || '-'}</Descriptions.Item>
              <Descriptions.Item label="Alternate Mobile">{lead.alternate_mobile || '-'}</Descriptions.Item>
              <Descriptions.Item label="Product Interest">{lead.product_interest || '-'}</Descriptions.Item>
              <Descriptions.Item label="Loan Amount">
                {lead.loan_amount_required ? `₹${lead.loan_amount_required.toLocaleString()}` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Monthly Income">
                {lead.monthly_income ? `₹${lead.monthly_income.toLocaleString()}` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Occupation">{lead.occupation || '-'}</Descriptions.Item>
              <Descriptions.Item label="Company">{lead.company_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Pincode">{lead.pincode || '-'}</Descriptions.Item>
              <Descriptions.Item label="Lead Score">
                <Badge count={lead.lead_score} />
              </Descriptions.Item>
              <Descriptions.Item label="Temperature">
                <Space>
                  {getTemperatureIcon(lead.lead_temperature)}
                  {lead.lead_temperature.toUpperCase()}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Priority">
                <Tag color={lead.priority === 'urgent' ? 'red' : 'blue'}>
                  {lead.priority.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Qualified">
                {lead.is_qualified ? (
                  <Tag color="green">YES</Tag>
                ) : (
                  <Tag color="red">NO</Tag>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Assigned To">{lead.assigned_to_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Follow-up Count">{lead.follow_up_count}</Descriptions.Item>
              <Descriptions.Item label="Next Follow-up">
                {lead.next_follow_up_date ? moment(lead.next_follow_up_date).format('DD MMM YYYY, hh:mm A') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Last Contacted">
                {lead.last_contacted_date ? moment(lead.last_contacted_date).format('DD MMM YYYY, hh:mm A') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Created At">
                {moment(lead.created_at).format('DD MMM YYYY, hh:mm A')}
              </Descriptions.Item>
              <Descriptions.Item label="Remarks" span={2}>{lead.remarks || '-'}</Descriptions.Item>
            </Descriptions>

            {lead.score_breakdown && (
              <>
                <Divider>Score Breakdown</Divider>
                <Descriptions bordered column={3}>
                  {Object.entries(lead.score_breakdown).map(([key, value]) => (
                    <Descriptions.Item key={key} label={key.replace('_', ' ').toUpperCase()}>
                      {value}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              </>
            )}
          </Card>
        </TabPane>

        <TabPane tab={`Follow-ups (${followUps.length})`} key="followups">
          <Card>
            <Timeline>
              {followUps.map((followUp) => (
                <Timeline.Item
                  key={followUp.id}
                  color={
                    followUp.status === 'completed' ? 'green' :
                    followUp.status === 'overdue' ? 'red' : 'blue'
                  }
                >
                  <p><strong>{followUp.subject}</strong></p>
                  <p>Type: <Tag>{followUp.follow_up_type.replace('_', ' ').toUpperCase()}</Tag></p>
                  <p>Scheduled: {moment(followUp.scheduled_date).format('DD MMM YYYY, hh:mm A')}</p>
                  <p>Status: <Tag color={followUp.status === 'completed' ? 'green' : 'orange'}>
                    {followUp.status.toUpperCase()}
                  </Tag></p>
                  {followUp.description && <p>{followUp.description}</p>}
                  {followUp.outcome && (
                    <p style={{ color: '#52c41a' }}><strong>Outcome:</strong> {followUp.outcome}</p>
                  )}
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </TabPane>

        <TabPane tab={`Activity Log (${activities.length})`} key="activities">
          <Card>
            <Timeline>
              {activities.map((activity) => (
                <Timeline.Item key={activity.id}>
                  <p><strong>{activity.activity_title}</strong></p>
                  <p style={{ fontSize: '12px', color: '#888' }}>
                    {moment(activity.activity_date).format('DD MMM YYYY, hh:mm A')}
                    {activity.performed_by_name && ` by ${activity.performed_by_name}`}
                  </p>
                  {activity.activity_description && <p>{activity.activity_description}</p>}
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </TabPane>
      </Tabs>


      {/* Follow-up Modal */}
      <Modal
        title="Schedule Follow-up"
        open={followUpModalVisible}
        onCancel={() => {
          followUpForm.resetFields();
          setFollowUpModalVisible(false);
        }}
        onOk={() => followUpForm.submit()}
      >
        <Form form={followUpForm} layout="vertical" onFinish={handleCreateFollowUp}>
          <Form.Item
            name="follow_up_type"
            label="Follow-up Type"
            rules={[{ required: true, message: 'Please select type' }]}
          >
            <Select placeholder="Select type">
              {Object.values(FollowUpType).map((type) => (
                <Option key={type} value={type}>
                  {type.replace('_', ' ').toUpperCase()}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="scheduled_date"
            label="Scheduled Date & Time"
            rules={[{ required: true, message: 'Please select date and time' }]}
          >
            <DatePicker
              showTime
              format="DD MMM YYYY, hh:mm A"
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="subject"
            label="Subject"
            rules={[{ required: true, message: 'Please enter subject' }]}
          >
            <Input placeholder="Enter subject" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Enter description" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Qualify Modal */}
      <Modal
        title="Qualify Lead"
        open={qualifyModalVisible}
        onCancel={() => {
          qualifyForm.resetFields();
          setQualifyModalVisible(false);
        }}
        onOk={() => qualifyForm.submit()}
      >
        <Form form={qualifyForm} layout="vertical" onFinish={handleQualifyLead}>
          <Form.Item
            name="is_qualified"
            label="Action"
            rules={[{ required: true, message: 'Please select action' }]}
          >
            <Select placeholder="Select action">
              <Option value={true}>Qualify Lead</Option>
              <Option value={false}>Disqualify Lead</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="reason"
            label="Reason"
            rules={[{ required: true, message: 'Please enter reason' }]}
          >
            <TextArea rows={3} placeholder="Enter reason for qualification/disqualification" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Lost Modal */}
      <Modal
        title="Mark Lead as Lost"
        open={lostModalVisible}
        onCancel={() => {
          lostForm.resetFields();
          setLostModalVisible(false);
        }}
        onOk={() => lostForm.submit()}
      >
        <Form form={lostForm} layout="vertical" onFinish={handleMarkLost}>
          <Form.Item
            name="reason"
            label="Reason"
            rules={[{ required: true, message: 'Please enter reason' }]}
          >
            <Select placeholder="Select reason">
              <Option value="Not Interested">Not Interested</Option>
              <Option value="Already has Loan">Already has Loan</Option>
              <Option value="Better offer elsewhere">Better offer elsewhere</Option>
              <Option value="Not eligible">Not eligible</Option>
              <Option value="Cannot provide documents">Cannot provide documents</Option>
              <Option value="Other">Other</Option>
            </Select>
          </Form.Item>

          <Form.Item name="remarks" label="Additional Remarks">
            <TextArea rows={3} placeholder="Enter additional remarks" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default LeadDetailPage;
