/**
 * Create New Litigation Case Component
 * Form for creating a new litigation case
 */

import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Space,
  Row,
  Col,
  message,
  Steps,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { createCase } from '../../services/legal/litigationService';

const { TextArea } = Input;
const { Option } = Select;
const { Step } = Steps;

const CreateCase = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      const caseData = {
        case_number: values.case_number,
        case_title: values.case_title,
        case_type: values.case_type,
        case_sub_type: values.case_sub_type,
        priority: values.priority || 'medium',
        court_name: values.court_name,
        court_location: values.court_location,
        bench: values.bench,
        judge_name: values.judge_name,
        description: values.description,
        subject_matter: values.subject_matter,
        relief_sought: values.relief_sought,
        claim_amount: values.claim_amount,
        disputed_amount: values.disputed_amount,
        filing_date: values.filing_date.format('YYYY-MM-DD'),
        admission_date: values.admission_date
          ? values.admission_date.format('YYYY-MM-DD')
          : null,
        first_hearing_date: values.first_hearing_date
          ? values.first_hearing_date.format('YYYY-MM-DD')
          : null,
        limitation_date: values.limitation_date
          ? values.limitation_date.format('YYYY-MM-DD')
          : null,
        primary_advocate: values.primary_advocate,
        primary_advocate_contact: values.primary_advocate_contact,
        advocate_firm: values.advocate_firm,
        risk_level: values.risk_level,
        business_impact: values.business_impact,
        potential_liability: values.potential_liability,
        notes: values.notes,
      };

      const response = await createCase(caseData);
      if (response.success) {
        message.success('Case created successfully');
        navigate(`/legal/litigation/cases/${response.data.id}`);
      }
    } catch (error) {
      message.error('Failed to create case');
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      title: 'Basic Information',
      content: (
        <>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="case_number"
                label="Case Number"
                rules={[{ required: true, message: 'Please enter case number' }]}
              >
                <Input placeholder="e.g., CS/123/2024" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="case_type"
                label="Case Type"
                rules={[{ required: true, message: 'Please select case type' }]}
              >
                <Select placeholder="Select case type">
                  <Option value="civil">Civil</Option>
                  <Option value="criminal">Criminal</Option>
                  <Option value="arbitration">Arbitration</Option>
                  <Option value="recovery">Recovery</Option>
                  <Option value="consumer">Consumer</Option>
                  <Option value="labor">Labor</Option>
                  <Option value="tax">Tax</Option>
                  <Option value="corporate">Corporate</Option>
                  <Option value="property">Property</Option>
                  <Option value="intellectual_property">Intellectual Property</Option>
                  <Option value="banking">Banking</Option>
                  <Option value="regulatory">Regulatory</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="case_title"
            label="Case Title"
            rules={[{ required: true, message: 'Please enter case title' }]}
          >
            <Input placeholder="e.g., ABC Bank vs XYZ Company" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="case_sub_type" label="Case Sub Type">
                <Input placeholder="e.g., Loan Recovery" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="priority"
                label="Priority"
                initialValue="medium"
              >
                <Select>
                  <Option value="low">Low</Option>
                  <Option value="medium">Medium</Option>
                  <Option value="high">High</Option>
                  <Option value="critical">Critical</Option>
                  <Option value="urgent">Urgent</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Brief description of the case" />
          </Form.Item>
        </>
      ),
    },
    {
      title: 'Court Details',
      content: (
        <>
          <Form.Item
            name="court_name"
            label="Court Name"
            rules={[{ required: true, message: 'Please enter court name' }]}
          >
            <Input placeholder="e.g., High Court of Delhi" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="court_location" label="Court Location">
                <Input placeholder="e.g., New Delhi" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="bench" label="Bench">
                <Input placeholder="e.g., Division Bench" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="judge_name" label="Judge Name">
            <Input placeholder="e.g., Hon'ble Justice Smith" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="filing_date"
                label="Filing Date"
                rules={[{ required: true, message: 'Please select filing date' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="admission_date" label="Admission Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="first_hearing_date" label="First Hearing Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="limitation_date" label="Limitation Date">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </>
      ),
    },
    {
      title: 'Case Details',
      content: (
        <>
          <Form.Item name="subject_matter" label="Subject Matter">
            <TextArea rows={3} placeholder="Main subject matter of the case" />
          </Form.Item>

          <Form.Item name="relief_sought" label="Relief Sought">
            <TextArea rows={3} placeholder="Relief or remedy being sought" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="claim_amount" label="Claim Amount (₹)">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="disputed_amount" label="Disputed Amount (₹)">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="risk_level" label="Risk Level">
            <Select placeholder="Select risk level">
              <Option value="Low">Low</Option>
              <Option value="Medium">Medium</Option>
              <Option value="High">High</Option>
            </Select>
          </Form.Item>

          <Form.Item name="business_impact" label="Business Impact">
            <TextArea rows={2} placeholder="Impact on business operations" />
          </Form.Item>

          <Form.Item name="potential_liability" label="Potential Liability (₹)">
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              placeholder="0.00"
            />
          </Form.Item>
        </>
      ),
    },
    {
      title: 'Legal Team',
      content: (
        <>
          <Form.Item name="primary_advocate" label="Primary Advocate">
            <Input placeholder="Advocate name" />
          </Form.Item>

          <Form.Item name="advocate_firm" label="Law Firm">
            <Input placeholder="Law firm name" />
          </Form.Item>

          <Form.Item
            name="primary_advocate_contact"
            label="Advocate Contact"
          >
            <Input placeholder="Phone number or email" />
          </Form.Item>

          <Form.Item name="notes" label="Notes">
            <TextArea rows={4} placeholder="Any additional notes or remarks" />
          </Form.Item>
        </>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Header */}
          <div>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/legal/litigation')}
              style={{ marginBottom: 16 }}
            >
              Back to Cases
            </Button>
            <h1>Create New Litigation Case</h1>
          </div>

          {/* Steps */}
          <Steps current={currentStep}>
            {steps.map((step) => (
              <Step key={step.title} title={step.title} />
            ))}
          </Steps>

          {/* Form */}
          <Form form={form} layout="vertical">
            <div style={{ marginTop: 24 }}>{steps[currentStep].content}</div>
          </Form>

          {/* Navigation */}
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              {currentStep > 0 && (
                <Button onClick={() => setCurrentStep(currentStep - 1)}>
                  Previous
                </Button>
              )}
              {currentStep < steps.length - 1 && (
                <Button
                  type="primary"
                  onClick={() => setCurrentStep(currentStep + 1)}
                >
                  Next
                </Button>
              )}
              {currentStep === steps.length - 1 && (
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  loading={loading}
                  onClick={handleSubmit}
                >
                  Create Case
                </Button>
              )}
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default CreateCase;
