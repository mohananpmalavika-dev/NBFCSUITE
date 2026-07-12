/**
 * Case Details Component
 * Displays complete case information with hearings, expenses, parties, and documents
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Descriptions,
  Tag,
  Button,
  Space,
  Tabs,
  Table,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  message,
  Spin,
  Timeline,
  Statistic,
} from 'antd';
import {
  EditOutlined,
  PlusOutlined,
  CalendarOutlined,
  DollarOutlined,
  TeamOutlined,
  FileTextOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import moment from 'moment';
import {
  getCase,
  updateCase,
  getCaseHearings,
  createHearing,
  updateHearing,
  getCaseExpenses,
  createExpense,
  approveExpense,
  markExpensePaid,
  getCaseParties,
  createParty,
  formatCurrency,
  formatDate,
  formatDateTime,
  getCaseStatusColor,
  getPriorityColor,
  getHearingStatusColor,
} from '../../services/legal/litigationService';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const CaseDetails = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [caseData, setCaseData] = useState(null);
  const [hearings, setHearings] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [parties, setParties] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState(null);
  const [form] = Form.useForm();

  // Fetch case details
  const fetchCaseDetails = async () => {
    setLoading(true);
    try {
      const response = await getCase(caseId, true);
      if (response.success) {
        setCaseData(response.data);
      }
    } catch (error) {
      message.error('Failed to fetch case details');
    } finally {
      setLoading(false);
    }
  };

  // Fetch hearings
  const fetchHearings = async () => {
    try {
      const response = await getCaseHearings(caseId);
      if (response.success) {
        setHearings(response.data.hearings);
      }
    } catch (error) {
      message.error('Failed to fetch hearings');
    }
  };

  // Fetch expenses
  const fetchExpenses = async () => {
    try {
      const response = await getCaseExpenses(caseId);
      if (response.success) {
        setExpenses(response.data.expenses);
      }
    } catch (error) {
      message.error('Failed to fetch expenses');
    }
  };

  // Fetch parties
  const fetchParties = async () => {
    try {
      const response = await getCaseParties(caseId);
      if (response.success) {
        setParties(response.data.parties);
      }
    } catch (error) {
      message.error('Failed to fetch parties');
    }
  };

  useEffect(() => {
    if (caseId) {
      fetchCaseDetails();
      fetchHearings();
      fetchExpenses();
      fetchParties();
    }
  }, [caseId]);

  // Handle modal open
  const handleOpenModal = (type) => {
    setModalType(type);
    setModalVisible(true);
    form.resetFields();
  };

  // Handle modal submit
  const handleModalSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (modalType === 'hearing') {
        const hearingData = {
          case_id: caseId,
          hearing_type: values.hearing_type,
          scheduled_date: values.scheduled_date.toISOString(),
          court_room: values.court_room,
          judge_name: values.judge_name,
          purpose: values.purpose,
          agenda: values.agenda,
          advocate_name: values.advocate_name,
          client_attended: values.client_attended || false,
        };
        const response = await createHearing(hearingData);
        if (response.success) {
          message.success('Hearing scheduled successfully');
          fetchHearings();
          fetchCaseDetails();
        }
      } else if (modalType === 'expense') {
        const expenseData = {
          case_id: caseId,
          expense_category: values.expense_category,
          description: values.description,
          amount: values.amount,
          tax_amount: values.tax_amount || 0,
          expense_date: values.expense_date.format('YYYY-MM-DD'),
          payee_name: values.payee_name,
          payee_contact: values.payee_contact,
          invoice_number: values.invoice_number,
          notes: values.notes,
        };
        const response = await createExpense(expenseData);
        if (response.success) {
          message.success('Expense created successfully');
          fetchExpenses();
        }
      } else if (modalType === 'party') {
        const partyData = {
          case_id: caseId,
          party_role: values.party_role,
          party_name: values.party_name,
          organization_name: values.organization_name,
          email: values.email,
          phone: values.phone,
          address: values.address,
          is_represented: values.is_represented || false,
          advocate_name: values.advocate_name,
          advocate_firm: values.advocate_firm,
        };
        const response = await createParty(partyData);
        if (response.success) {
          message.success('Party added successfully');
          fetchParties();
        }
      }
      
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to submit');
    }
  };

  // Hearings table columns
  const hearingColumns = [
    {
      title: 'Hearing #',
      dataIndex: 'hearing_number',
      key: 'hearing_number',
      width: 100,
    },
    {
      title: 'Type',
      dataIndex: 'hearing_type',
      key: 'hearing_type',
      width: 150,
      render: (type) => <Tag>{type.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'hearing_status',
      key: 'hearing_status',
      width: 120,
      render: (status) => (
        <Tag color={getHearingStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Scheduled Date',
      dataIndex: 'scheduled_date',
      key: 'scheduled_date',
      width: 180,
      render: (date) => formatDateTime(date),
    },
    {
      title: 'Judge',
      dataIndex: 'judge_name',
      key: 'judge_name',
      ellipsis: true,
    },
    {
      title: 'Next Hearing',
      dataIndex: 'next_hearing_date',
      key: 'next_hearing_date',
      width: 180,
      render: (date) => (date ? formatDateTime(date) : '-'),
    },
  ];

  // Expenses table columns
  const expenseColumns = [
    {
      title: 'Expense #',
      dataIndex: 'expense_number',
      key: 'expense_number',
      width: 150,
    },
    {
      title: 'Category',
      dataIndex: 'expense_category',
      key: 'expense_category',
      width: 150,
      render: (cat) => <Tag>{cat.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Amount',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      render: (amount) => formatCurrency(amount),
    },
    {
      title: 'Date',
      dataIndex: 'expense_date',
      key: 'expense_date',
      width: 120,
      render: (date) => formatDate(date),
    },
    {
      title: 'Payee',
      dataIndex: 'payee_name',
      key: 'payee_name',
      ellipsis: true,
    },
    {
      title: 'Status',
      key: 'status',
      width: 100,
      render: (_, record) => {
        if (record.is_paid) return <Tag color="green">PAID</Tag>;
        if (record.is_approved) return <Tag color="blue">APPROVED</Tag>;
        return <Tag color="orange">PENDING</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          {!record.is_approved && (
            <Button
              size="small"
              type="link"
              onClick={() => handleApproveExpense(record.id)}
            >
              Approve
            </Button>
          )}
          {record.is_approved && !record.is_paid && (
            <Button
              size="small"
              type="link"
              onClick={() => handleMarkPaid(record.id)}
            >
              Mark Paid
            </Button>
          )}
        </Space>
      ),
    },
  ];

  // Parties table columns
  const partyColumns = [
    {
      title: 'Role',
      dataIndex: 'party_role',
      key: 'party_role',
      width: 150,
      render: (role) => <Tag color="blue">{role.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Name',
      dataIndex: 'party_name',
      key: 'party_name',
    },
    {
      title: 'Organization',
      dataIndex: 'organization_name',
      key: 'organization_name',
      ellipsis: true,
    },
    {
      title: 'Contact',
      key: 'contact',
      render: (_, record) => (
        <div>
          <div>{record.email}</div>
          <div>{record.phone}</div>
        </div>
      ),
    },
    {
      title: 'Advocate',
      dataIndex: 'advocate_name',
      key: 'advocate_name',
      ellipsis: true,
    },
    {
      title: 'Law Firm',
      dataIndex: 'advocate_firm',
      key: 'advocate_firm',
      ellipsis: true,
    },
  ];

  // Handle approve expense
  const handleApproveExpense = async (expenseId) => {
    try {
      const response = await approveExpense(expenseId);
      if (response.success) {
        message.success('Expense approved');
        fetchExpenses();
      }
    } catch (error) {
      message.error('Failed to approve expense');
    }
  };

  // Handle mark paid
  const handleMarkPaid = async (expenseId) => {
    try {
      const response = await markExpensePaid(
        expenseId,
        moment().format('YYYY-MM-DD')
      );
      if (response.success) {
        message.success('Expense marked as paid');
        fetchExpenses();
      }
    } catch (error) {
      message.error('Failed to mark expense as paid');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!caseData) {
    return <div>Case not found</div>;
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/legal/litigation')}
            >
              Back
            </Button>
            <div>
              <h1 style={{ margin: 0 }}>{caseData.case_number}</h1>
              <p style={{ margin: 0, color: '#666' }}>{caseData.case_title}</p>
            </div>
          </Space>
        </Col>
        <Col>
          <Space>
            <Tag color={getCaseStatusColor(caseData.status)}>
              {caseData.status.replace('_', ' ').toUpperCase()}
            </Tag>
            <Tag color={getPriorityColor(caseData.priority)}>
              {caseData.priority.toUpperCase()}
            </Tag>
            <Button icon={<EditOutlined />}>Edit Case</Button>
          </Space>
        </Col>
      </Row>

      {/* Summary Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Hearings"
              value={caseData.hearings || 0}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Expenses"
              value={formatCurrency(caseData.total_expenses || 0)}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Parties"
              value={caseData.parties || 0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Main Content */}
      <Card>
        <Tabs defaultActiveKey="details">
          <TabPane tab="Case Details" key="details">
            <Descriptions bordered column={2}>
              <Descriptions.Item label="Case Number">
                {caseData.case_number}
              </Descriptions.Item>
              <Descriptions.Item label="Case Type">
                <Tag>{caseData.case_type.replace('_', ' ').toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Court" span={2}>
                {caseData.court_name}
              </Descriptions.Item>
              <Descriptions.Item label="Judge">
                {caseData.judge_name || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Filing Date">
                {formatDate(caseData.filing_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Next Hearing">
                {formatDateTime(caseData.next_hearing_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Claim Amount">
                {formatCurrency(caseData.claim_amount)}
              </Descriptions.Item>
              <Descriptions.Item label="Primary Advocate" span={2}>
                {caseData.primary_advocate}
                {caseData.advocate_firm && ` (${caseData.advocate_firm})`}
              </Descriptions.Item>
              <Descriptions.Item label="Subject Matter" span={2}>
                {caseData.subject_matter || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Notes" span={2}>
                {caseData.notes || '-'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>

          <TabPane
            tab={
              <span>
                <CalendarOutlined /> Hearings ({hearings.length})
              </span>
            }
            key="hearings"
          >
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => handleOpenModal('hearing')}
              style={{ marginBottom: 16 }}
            >
              Schedule Hearing
            </Button>
            <Table
              columns={hearingColumns}
              dataSource={hearings}
              rowKey="id"
              pagination={false}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <DollarOutlined /> Expenses ({expenses.length})
              </span>
            }
            key="expenses"
          >
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => handleOpenModal('expense')}
              style={{ marginBottom: 16 }}
            >
              Add Expense
            </Button>
            <Table
              columns={expenseColumns}
              dataSource={expenses}
              rowKey="id"
              pagination={false}
              summary={(pageData) => {
                const total = pageData.reduce(
                  (sum, record) => sum + parseFloat(record.total_amount),
                  0
                );
                return (
                  <Table.Summary.Row>
                    <Table.Summary.Cell colSpan={3}>
                      <strong>Total</strong>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell>
                      <strong>{formatCurrency(total)}</strong>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell colSpan={4} />
                  </Table.Summary.Row>
                );
              }}
            />
          </TabPane>

          <TabPane
            tab={
              <span>
                <TeamOutlined /> Parties ({parties.length})
              </span>
            }
            key="parties"
          >
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => handleOpenModal('party')}
              style={{ marginBottom: 16 }}
            >
              Add Party
            </Button>
            <Table
              columns={partyColumns}
              dataSource={parties}
              rowKey="id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* Modals */}
      <Modal
        title={
          modalType === 'hearing'
            ? 'Schedule Hearing'
            : modalType === 'expense'
            ? 'Add Expense'
            : 'Add Party'
        }
        visible={modalVisible}
        onOk={handleModalSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          {modalType === 'hearing' && (
            <>
              <Form.Item
                name="hearing_type"
                label="Hearing Type"
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="first_hearing">First Hearing</Option>
                  <Option value="regular_hearing">Regular Hearing</Option>
                  <Option value="interim_application">Interim Application</Option>
                  <Option value="evidence_recording">Evidence Recording</Option>
                  <Option value="argument">Argument</Option>
                  <Option value="final_argument">Final Argument</Option>
                  <Option value="judgment">Judgment</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="scheduled_date"
                label="Scheduled Date & Time"
                rules={[{ required: true }]}
              >
                <DatePicker showTime style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="court_room" label="Court Room">
                <Input />
              </Form.Item>
              <Form.Item name="judge_name" label="Judge Name">
                <Input />
              </Form.Item>
              <Form.Item name="purpose" label="Purpose">
                <TextArea rows={2} />
              </Form.Item>
              <Form.Item name="agenda" label="Agenda">
                <TextArea rows={2} />
              </Form.Item>
              <Form.Item name="advocate_name" label="Advocate Name">
                <Input />
              </Form.Item>
            </>
          )}

          {modalType === 'expense' && (
            <>
              <Form.Item
                name="expense_category"
                label="Category"
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="court_fees">Court Fees</Option>
                  <Option value="advocate_fees">Advocate Fees</Option>
                  <Option value="consultation_fees">Consultation Fees</Option>
                  <Option value="documentation">Documentation</Option>
                  <Option value="travel">Travel</Option>
                  <Option value="expert_witness">Expert Witness</Option>
                  <Option value="misc">Miscellaneous</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="description"
                label="Description"
                rules={[{ required: true }]}
              >
                <TextArea rows={2} />
              </Form.Item>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="amount"
                    label="Amount"
                    rules={[{ required: true }]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      prefix="₹"
                      min={0}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="tax_amount" label="Tax Amount">
                    <InputNumber
                      style={{ width: '100%' }}
                      prefix="₹"
                      min={0}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item
                name="expense_date"
                label="Expense Date"
                rules={[{ required: true }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item
                name="payee_name"
                label="Payee Name"
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
              <Form.Item name="payee_contact" label="Payee Contact">
                <Input />
              </Form.Item>
              <Form.Item name="invoice_number" label="Invoice Number">
                <Input />
              </Form.Item>
              <Form.Item name="notes" label="Notes">
                <TextArea rows={2} />
              </Form.Item>
            </>
          )}

          {modalType === 'party' && (
            <>
              <Form.Item
                name="party_role"
                label="Party Role"
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="petitioner">Petitioner</Option>
                  <Option value="respondent">Respondent</Option>
                  <Option value="plaintiff">Plaintiff</Option>
                  <Option value="defendant">Defendant</Option>
                  <Option value="witness">Witness</Option>
                  <Option value="advocate">Advocate</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="party_name"
                label="Name"
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
              <Form.Item name="organization_name" label="Organization">
                <Input />
              </Form.Item>
              <Form.Item name="email" label="Email">
                <Input type="email" />
              </Form.Item>
              <Form.Item name="phone" label="Phone">
                <Input />
              </Form.Item>
              <Form.Item name="address" label="Address">
                <TextArea rows={2} />
              </Form.Item>
              <Form.Item name="advocate_name" label="Advocate Name">
                <Input />
              </Form.Item>
              <Form.Item name="advocate_firm" label="Law Firm">
                <Input />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default CaseDetails;
