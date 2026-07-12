/**
 * License Details Component
 * Detailed view of a license with renewal and compliance tracking
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Descriptions,
  Row,
  Col,
  Button,
  Tag,
  Space,
  Tabs,
  Table,
  Timeline,
  Progress,
  Alert,
  Modal,
  Form,
  Input,
  DatePicker,
  InputNumber,
  Select,
  Upload,
  message,
  Spin,
  Divider,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  CalendarOutlined,
  WarningOutlined,
  UploadOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import moment from 'moment';
import {
  getLicenseById,
  getRenewals,
  getComplianceChecks,
  getDocuments,
  getReminders,
  createRenewal,
  updateRenewal,
  createComplianceCheck,
  addDocument,
  formatCurrency,
  formatDate,
  formatDateTime,
  getLicenseStatusColor,
  getRenewalStatusColor,
  getComplianceStatusColor,
} from '../../services/legal/licenseService';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const LicenseDetails = () => {
  const navigate = useNavigate();
  const { licenseId } = useParams();
  const [loading, setLoading] = useState(false);
  const [license, setLicense] = useState(null);
  const [renewals, setRenewals] = useState([]);
  const [complianceChecks, setComplianceChecks] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [renewalModalVisible, setRenewalModalVisible] = useState(false);
  const [complianceModalVisible, setComplianceModalVisible] = useState(false);
  const [renewalForm] = Form.useForm();
  const [complianceForm] = Form.useForm();

  // Fetch license details
  const fetchLicenseDetails = async () => {
    setLoading(true);
    try {
      const response = await getLicenseById(licenseId);
      if (response.success) {
        setLicense(response.data);
      } else {
        message.error(response.error);
      }
    } catch (error) {
      message.error('Failed to fetch license details');
    } finally {
      setLoading(false);
    }
  };

  // Fetch renewals
  const fetchRenewals = async () => {
    try {
      const response = await getRenewals(licenseId);
      if (response.success) {
        setRenewals(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch renewals');
    }
  };

  // Fetch compliance checks
  const fetchComplianceChecks = async () => {
    try {
      const response = await getComplianceChecks(licenseId);
      if (response.success) {
        setComplianceChecks(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch compliance checks');
    }
  };

  // Fetch documents
  const fetchDocuments = async () => {
    try {
      const response = await getDocuments(licenseId);
      if (response.success) {
        setDocuments(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch documents');
    }
  };

  // Fetch reminders
  const fetchReminders = async () => {
    try {
      const response = await getReminders(licenseId);
      if (response.success) {
        setReminders(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch reminders');
    }
  };

  useEffect(() => {
    fetchLicenseDetails();
    fetchRenewals();
    fetchComplianceChecks();
    fetchDocuments();
    fetchReminders();
  }, [licenseId]);

  // Handle renewal submission
  const handleRenewalSubmit = async (values) => {
    try {
      const response = await createRenewal(licenseId, {
        renewal_due_date: values.renewal_due_date.format('YYYY-MM-DD'),
        application_submitted_date: values.application_submitted_date
          ? values.application_submitted_date.format('YYYY-MM-DD')
          : null,
        application_number: values.application_number,
        renewal_fee_paid: values.renewal_fee_paid,
        notes: values.notes,
      });

      if (response.success) {
        message.success('Renewal initiated successfully');
        setRenewalModalVisible(false);
        renewalForm.resetFields();
        fetchRenewals();
        fetchLicenseDetails();
      } else {
        message.error(response.error);
      }
    } catch (error) {
      message.error('Failed to initiate renewal');
    }
  };

  // Handle compliance check submission
  const handleComplianceSubmit = async (values) => {
    try {
      const response = await createComplianceCheck(licenseId, {
        check_date: values.check_date.format('YYYY-MM-DD'),
        check_type: values.check_type,
        compliance_status: values.compliance_status,
        overall_score: values.overall_score,
        compliant_items: values.compliant_items,
        non_compliant_items: values.non_compliant_items,
        findings: values.findings,
        recommendations: values.recommendations,
        next_check_due_date: values.next_check_due_date
          ? values.next_check_due_date.format('YYYY-MM-DD')
          : null,
        notes: values.notes,
      });

      if (response.success) {
        message.success('Compliance check recorded successfully');
        setComplianceModalVisible(false);
        complianceForm.resetFields();
        fetchComplianceChecks();
        fetchLicenseDetails();
      } else {
        message.error(response.error);
      }
    } catch (error) {
      message.error('Failed to record compliance check');
    }
  };

  // Renewal columns
  const renewalColumns = [
    {
      title: 'Renewal #',
      dataIndex: 'renewal_number',
      key: 'renewal_number',
    },
    {
      title: 'Status',
      dataIndex: 'renewal_status',
      key: 'renewal_status',
      render: (status) => (
        <Tag color={getRenewalStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Due Date',
      dataIndex: 'renewal_due_date',
      key: 'renewal_due_date',
      render: (date) => formatDate(date),
    },
    {
      title: 'Submitted Date',
      dataIndex: 'application_submitted_date',
      key: 'application_submitted_date',
      render: (date) => (date ? formatDate(date) : '-'),
    },
    {
      title: 'Completed Date',
      dataIndex: 'renewal_completed_date',
      key: 'renewal_completed_date',
      render: (date) => (date ? formatDate(date) : '-'),
    },
    {
      title: 'Fee Paid',
      dataIndex: 'renewal_fee_paid',
      key: 'renewal_fee_paid',
      render: (amount) => (amount ? formatCurrency(amount) : '-'),
    },
  ];

  // Compliance check columns
  const complianceColumns = [
    {
      title: 'Check #',
      dataIndex: 'check_number',
      key: 'check_number',
    },
    {
      title: 'Check Date',
      dataIndex: 'check_date',
      key: 'check_date',
      render: (date) => formatDate(date),
    },
    {
      title: 'Type',
      dataIndex: 'check_type',
      key: 'check_type',
    },
    {
      title: 'Status',
      dataIndex: 'compliance_status',
      key: 'compliance_status',
      render: (status) => (
        <Tag color={getComplianceStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Score',
      dataIndex: 'overall_score',
      key: 'overall_score',
      render: (score) => (score ? `${score}%` : '-'),
    },
    {
      title: 'Compliant Items',
      dataIndex: 'compliant_items',
      key: 'compliant_items',
    },
    {
      title: 'Non-Compliant Items',
      dataIndex: 'non_compliant_items',
      key: 'non_compliant_items',
    },
    {
      title: 'Next Check Due',
      dataIndex: 'next_check_due_date',
      key: 'next_check_due_date',
      render: (date) => (date ? formatDate(date) : '-'),
    },
  ];

  // Document columns
  const documentColumns = [
    {
      title: 'Document Name',
      dataIndex: 'document_name',
      key: 'document_name',
    },
    {
      title: 'Type',
      dataIndex: 'document_type',
      key: 'document_type',
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
      render: (size) => (size ? `${(size / 1024).toFixed(2)} KB` : '-'),
    },
    {
      title: 'Uploaded',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      render: (date) => formatDateTime(date),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          size="small"
          icon={<DownloadOutlined />}
          onClick={() => window.open(record.file_url, '_blank')}
        >
          Download
        </Button>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!license) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert message="License not found" type="error" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/legal/licenses')}
            >
              Back
            </Button>
            <div>
              <h1 style={{ margin: 0 }}>{license.license_name}</h1>
              <p style={{ margin: 0, color: '#666' }}>
                License #{license.license_number}
              </p>
            </div>
          </Space>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/legal/licenses/${licenseId}/edit`)}
            >
              Edit
            </Button>
            <Button
              type="primary"
              icon={<SyncOutlined />}
              onClick={() => setRenewalModalVisible(true)}
              disabled={!license.is_renewable}
            >
              Initiate Renewal
            </Button>
            <Button
              icon={<CheckCircleOutlined />}
              onClick={() => setComplianceModalVisible(true)}
            >
              Compliance Check
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Alerts */}
      {license.is_expired && (
        <Alert
          message="License Expired"
          description={`This license expired ${Math.abs(
            license.days_until_expiry
          )} days ago. Immediate action required.`}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      {license.is_expiring_soon && !license.is_expired && (
        <Alert
          message="License Expiring Soon"
          description={`This license will expire in ${license.days_until_expiry} days. Please initiate renewal process.`}
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      {license.compliance_status === 'non_compliant' && (
        <Alert
          message="Non-Compliant"
          description="This license has compliance issues that need attention."
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Main Content */}
      <Row gutter={16}>
        <Col xs={24} lg={16}>
          <Card title="License Details" style={{ marginBottom: 16 }}>
            <Descriptions column={{ xs: 1, sm: 2, md: 2 }} bordered>
              <Descriptions.Item label="License Number">
                {license.license_number}
              </Descriptions.Item>
              <Descriptions.Item label="License Type">
                <Tag>{license.license_type.replace('_', ' ').toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={getLicenseStatusColor(license.status)}>
                  {license.status.replace('_', ' ').toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Renewal Status">
                <Tag color={getRenewalStatusColor(license.renewal_status)}>
                  {license.renewal_status.replace('_', ' ').toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Issuing Authority" span={2}>
                {license.issuing_authority}
              </Descriptions.Item>
              <Descriptions.Item label="Issue Date">
                {formatDate(license.issue_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Expiry Date">
                {license.is_perpetual
                  ? 'Perpetual'
                  : formatDate(license.expiry_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Validity Period">
                {license.validity_period_months
                  ? `${license.validity_period_months} months`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Days Until Expiry">
                {license.days_until_expiry !== null ? (
                  <Tag
                    color={
                      license.days_until_expiry < 0
                        ? 'red'
                        : license.days_until_expiry <= 30
                        ? 'orange'
                        : 'green'
                    }
                  >
                    {license.days_until_expiry < 0
                      ? `Expired ${Math.abs(license.days_until_expiry)} days ago`
                      : `${license.days_until_expiry} days`}
                  </Tag>
                ) : (
                  'N/A'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Compliance Status">
                <Tag color={getComplianceStatusColor(license.compliance_status)}>
                  {license.compliance_status.replace('_', ' ').toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Last Compliance Check">
                {license.last_compliance_check_date
                  ? formatDate(license.last_compliance_check_date)
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Criticality Level">
                {license.criticality_level ? (
                  <Tag
                    color={
                      license.criticality_level === 'Critical'
                        ? 'red'
                        : license.criticality_level === 'High'
                        ? 'orange'
                        : license.criticality_level === 'Medium'
                        ? 'blue'
                        : 'green'
                    }
                  >
                    {license.criticality_level}
                  </Tag>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Renewable">
                {license.is_renewable ? 'Yes' : 'No'}
              </Descriptions.Item>
              <Descriptions.Item label="Application Fee">
                {formatCurrency(license.application_fee)}
              </Descriptions.Item>
              <Descriptions.Item label="Renewal Fee">
                {formatCurrency(license.renewal_fee)}
              </Descriptions.Item>
              <Descriptions.Item label="Annual Fee">
                {formatCurrency(license.annual_fee)}
              </Descriptions.Item>
              <Descriptions.Item label="Responsible Department">
                {license.responsible_department || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="License Holder">
                {license.license_holder_name || '-'}
              </Descriptions.Item>
              {license.description && (
                <Descriptions.Item label="Description" span={2}>
                  {license.description}
                </Descriptions.Item>
              )}
              {license.notes && (
                <Descriptions.Item label="Notes" span={2}>
                  {license.notes}
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>

          {/* Tabs for History */}
          <Card>
            <Tabs defaultActiveKey="renewals">
              <TabPane tab="Renewal History" key="renewals">
                <Table
                  columns={renewalColumns}
                  dataSource={renewals}
                  rowKey="id"
                  pagination={false}
                />
              </TabPane>
              <TabPane tab="Compliance Checks" key="compliance">
                <Table
                  columns={complianceColumns}
                  dataSource={complianceChecks}
                  rowKey="id"
                  pagination={false}
                />
              </TabPane>
              <TabPane tab="Documents" key="documents">
                <Table
                  columns={documentColumns}
                  dataSource={documents}
                  rowKey="id"
                  pagination={false}
                />
              </TabPane>
            </Tabs>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          {/* Alert Statistics */}
          <Card title="Alert & Reminder Status" style={{ marginBottom: 16 }}>
            <Descriptions column={1}>
              <Descriptions.Item label="Total Reminders Sent">
                {license.total_reminders_sent}
              </Descriptions.Item>
              <Descriptions.Item label="Last Alert Sent">
                {license.last_alert_sent
                  ? formatDateTime(license.last_alert_sent)
                  : 'Never'}
              </Descriptions.Item>
              <Descriptions.Item label="Escalation Triggered">
                <Tag color={license.escalation_triggered ? 'red' : 'green'}>
                  {license.escalation_triggered ? 'Yes' : 'No'}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Authority Contact */}
          {license.authority_contact_person && (
            <Card title="Authority Contact" style={{ marginBottom: 16 }}>
              <Descriptions column={1}>
                <Descriptions.Item label="Contact Person">
                  {license.authority_contact_person}
                </Descriptions.Item>
                {license.authority_email && (
                  <Descriptions.Item label="Email">
                    {license.authority_email}
                  </Descriptions.Item>
                )}
                {license.authority_phone && (
                  <Descriptions.Item label="Phone">
                    {license.authority_phone}
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Card>
          )}

          {/* Recent Reminders */}
          {reminders.length > 0 && (
            <Card title="Recent Reminders">
              <Timeline>
                {reminders.slice(0, 5).map((reminder) => (
                  <Timeline.Item
                    key={reminder.id}
                    color={reminder.is_sent ? 'green' : 'blue'}
                  >
                    <p style={{ margin: 0 }}>
                      <strong>{reminder.reminder_type}</strong>
                    </p>
                    <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
                      {formatDateTime(reminder.reminder_date)}
                    </p>
                    <Tag size="small" color={reminder.is_sent ? 'green' : 'blue'}>
                      {reminder.is_sent ? 'Sent' : 'Pending'}
                    </Tag>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          )}
        </Col>
      </Row>

      {/* Renewal Modal */}
      <Modal
        title="Initiate License Renewal"
        open={renewalModalVisible}
        onCancel={() => {
          setRenewalModalVisible(false);
          renewalForm.resetFields();
        }}
        onOk={() => renewalForm.submit()}
        width={600}
      >
        <Form form={renewalForm} layout="vertical" onFinish={handleRenewalSubmit}>
          <Form.Item
            name="renewal_due_date"
            label="Renewal Due Date"
            rules={[{ required: true, message: 'Please select renewal due date' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="application_submitted_date"
            label="Application Submitted Date"
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="application_number" label="Application Number">
            <Input placeholder="Enter application number" />
          </Form.Item>
          <Form.Item name="renewal_fee_paid" label="Renewal Fee Paid">
            <InputNumber
              style={{ width: '100%' }}
              prefix="₹"
              placeholder="Enter amount"
              min={0}
            />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <TextArea rows={4} placeholder="Enter any additional notes" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Compliance Check Modal */}
      <Modal
        title="Record Compliance Check"
        open={complianceModalVisible}
        onCancel={() => {
          setComplianceModalVisible(false);
          complianceForm.resetFields();
        }}
        onOk={() => complianceForm.submit()}
        width={700}
      >
        <Form
          form={complianceForm}
          layout="vertical"
          onFinish={handleComplianceSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="check_date"
                label="Check Date"
                rules={[{ required: true, message: 'Please select check date' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="check_type" label="Check Type">
                <Select placeholder="Select check type">
                  <Option value="Routine">Routine</Option>
                  <Option value="Audit">Audit</Option>
                  <Option value="Inspection">Inspection</Option>
                  <Option value="Self-Assessment">Self-Assessment</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="compliance_status"
                label="Compliance Status"
                rules={[
                  { required: true, message: 'Please select compliance status' },
                ]}
              >
                <Select placeholder="Select status">
                  <Option value="compliant">Compliant</Option>
                  <Option value="non_compliant">Non-Compliant</Option>
                  <Option value="partially_compliant">Partially Compliant</Option>
                  <Option value="review_required">Review Required</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="overall_score" label="Overall Score (%)">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  max={100}
                  placeholder="Enter score"
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="compliant_items" label="Compliant Items">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="Count"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="non_compliant_items" label="Non-Compliant Items">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="Count"
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="findings" label="Findings">
            <TextArea rows={3} placeholder="Describe findings" />
          </Form.Item>
          <Form.Item name="recommendations" label="Recommendations">
            <TextArea rows={3} placeholder="Enter recommendations" />
          </Form.Item>
          <Form.Item name="next_check_due_date" label="Next Check Due Date">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <TextArea rows={2} placeholder="Additional notes" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default LicenseDetails;
