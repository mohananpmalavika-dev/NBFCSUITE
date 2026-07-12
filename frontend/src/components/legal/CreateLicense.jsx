/**
 * Create/Edit License Component
 * Form for creating or editing a license
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Switch,
  Button,
  Row,
  Col,
  message,
  Space,
  Divider,
  Tag,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import moment from 'moment';
import {
  createLicense,
  updateLicense,
  getLicenseById,
} from '../../services/legal/licenseService';

const { TextArea } = Input;
const { Option } = Select;

const CreateLicense = () => {
  const navigate = useNavigate();
  const { licenseId } = useParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [isPerpetual, setIsPerpetual] = useState(false);
  const [isRenewable, setIsRenewable] = useState(true);
  const isEditMode = !!licenseId;

  // Fetch license data if editing
  useEffect(() => {
    if (isEditMode) {
      fetchLicense();
    }
  }, [licenseId]);

  const fetchLicense = async () => {
    setLoading(true);
    try {
      const response = await getLicenseById(licenseId);
      if (response.success) {
        const license = response.data;
        form.setFieldsValue({
          ...license,
          issue_date: moment(license.issue_date),
          expiry_date: license.expiry_date ? moment(license.expiry_date) : null,
          application_date: license.application_date
            ? moment(license.application_date)
            : null,
          effective_date: license.effective_date
            ? moment(license.effective_date)
            : null,
        });
        setIsPerpetual(license.is_perpetual);
        setIsRenewable(license.is_renewable);
      } else {
        message.error(response.error);
        navigate('/legal/licenses');
      }
    } catch (error) {
      message.error('Failed to fetch license');
      navigate('/legal/licenses');
    } finally {
      setLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const licenseData = {
        ...values,
        issue_date: values.issue_date.format('YYYY-MM-DD'),
        expiry_date: values.expiry_date
          ? values.expiry_date.format('YYYY-MM-DD')
          : null,
        application_date: values.application_date
          ? values.application_date.format('YYYY-MM-DD')
          : null,
        effective_date: values.effective_date
          ? values.effective_date.format('YYYY-MM-DD')
          : null,
      };

      const response = isEditMode
        ? await updateLicense(licenseId, licenseData)
        : await createLicense(licenseData);

      if (response.success) {
        message.success(
          `License ${isEditMode ? 'updated' : 'created'} successfully`
        );
        navigate('/legal/licenses');
      } else {
        message.error(response.error);
      }
    } catch (error) {
      message.error(`Failed to ${isEditMode ? 'update' : 'create'} license`);
    } finally {
      setLoading(false);
    }
  };

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
              <h1 style={{ margin: 0 }}>
                {isEditMode ? 'Edit License' : 'Add New License'}
              </h1>
              <p style={{ margin: 0, color: '#666' }}>
                {isEditMode
                  ? 'Update license information'
                  : 'Register a new license'}
              </p>
            </div>
          </Space>
        </Col>
      </Row>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            is_renewable: true,
            is_perpetual: false,
            auto_renewal_enabled: false,
            renewal_notice_days: 60,
            renewal_submission_deadline_days: 30,
            alert_enabled: true,
            alert_days_before_expiry: [90, 60, 30, 15, 7],
            reminder_frequency: 'weekly',
            currency: 'INR',
            tags: [],
            alert_recipients: [],
            escalation_to: [],
          }}
        >
          {/* Basic Information */}
          <Divider orientation="left">Basic Information</Divider>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="license_number"
                label="License Number"
                rules={[
                  { required: true, message: 'Please enter license number' },
                ]}
              >
                <Input placeholder="Enter license number" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="license_name"
                label="License Name"
                rules={[{ required: true, message: 'Please enter license name' }]}
              >
                <Input placeholder="Enter license name" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="license_type"
                label="License Type"
                rules={[{ required: true, message: 'Please select license type' }]}
              >
                <Select placeholder="Select license type">
                  <Option value="nbfc_registration">NBFC Registration</Option>
                  <Option value="rbi_license">RBI License</Option>
                  <Option value="sebi_license">SEBI License</Option>
                  <Option value="business_license">Business License</Option>
                  <Option value="trade_license">Trade License</Option>
                  <Option value="professional_license">
                    Professional License
                  </Option>
                  <Option value="environmental_license">
                    Environmental License
                  </Option>
                  <Option value="fire_safety">Fire Safety</Option>
                  <Option value="pollution_control">Pollution Control</Option>
                  <Option value="labor_license">Labor License</Option>
                  <Option value="gst_registration">GST Registration</Option>
                  <Option value="import_export_license">
                    Import/Export License
                  </Option>
                  <Option value="software_license">Software License</Option>
                  <Option value="data_protection">Data Protection</Option>
                  <Option value="regulatory">Regulatory</Option>
                  <Option value="operational">Operational</Option>
                  <Option value="other">Other</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="license_category" label="License Category">
                <Input placeholder="Additional categorization" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Enter license description" />
          </Form.Item>

          {/* Issuing Authority */}
          <Divider orientation="left">Issuing Authority</Divider>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="issuing_authority"
                label="Issuing Authority"
                rules={[
                  { required: true, message: 'Please enter issuing authority' },
                ]}
              >
                <Input placeholder="e.g., Reserve Bank of India" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="authority_contact_person"
                label="Contact Person"
              >
                <Input placeholder="Name of contact person" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="authority_email" label="Authority Email">
                <Input type="email" placeholder="email@example.com" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="authority_phone" label="Authority Phone">
                <Input placeholder="Phone number" />
              </Form.Item>
            </Col>
          </Row>

          {/* Dates */}
          <Divider orientation="left">Important Dates</Divider>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="application_date" label="Application Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="issue_date"
                label="Issue Date"
                rules={[{ required: true, message: 'Please select issue date' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="effective_date" label="Effective Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="is_perpetual" label="Is Perpetual" valuePropName="checked">
                <Switch onChange={(checked) => setIsPerpetual(checked)} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="expiry_date"
                label="Expiry Date"
                rules={[
                  {
                    required: !isPerpetual,
                    message: 'Please select expiry date',
                  },
                ]}
              >
                <DatePicker style={{ width: '100%' }} disabled={isPerpetual} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="validity_period_months" label="Validity (Months)">
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  placeholder="Number of months"
                />
              </Form.Item>
            </Col>
          </Row>

          {/* Renewal Configuration */}
          <Divider orientation="left">Renewal Configuration</Divider>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item
                name="is_renewable"
                label="Is Renewable"
                valuePropName="checked"
              >
                <Switch onChange={(checked) => setIsRenewable(checked)} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="auto_renewal_enabled"
                label="Auto Renewal"
                valuePropName="checked"
              >
                <Switch disabled={!isRenewable} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="renewal_notice_days"
                label="Renewal Notice Days"
                tooltip="Days before expiry to start renewal process"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  placeholder="e.g., 60"
                  disabled={!isRenewable}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="renewal_submission_deadline_days"
                label="Submission Deadline Days"
                tooltip="Days before expiry to submit renewal application"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  placeholder="e.g., 30"
                  disabled={!isRenewable}
                />
              </Form.Item>
            </Col>
          </Row>

          {/* Financial Information */}
          <Divider orientation="left">Financial Information</Divider>
          <Row gutter={16}>
            <Col xs={24} md={6}>
              <Form.Item name="currency" label="Currency">
                <Select>
                  <Option value="INR">INR</Option>
                  <Option value="USD">USD</Option>
                  <Option value="EUR">EUR</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="application_fee" label="Application Fee">
                <InputNumber
                  style={{ width: '100%' }}
                  prefix="₹"
                  min={0}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="renewal_fee" label="Renewal Fee">
                <InputNumber
                  style={{ width: '100%' }}
                  prefix="₹"
                  min={0}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="annual_fee" label="Annual Fee">
                <InputNumber
                  style={{ width: '100%' }}
                  prefix="₹"
                  min={0}
                  placeholder="0.00"
                />
              </Form.Item>
            </Col>
          </Row>

          {/* Responsible Personnel */}
          <Divider orientation="left">Responsible Personnel</Divider>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="license_holder_name" label="License Holder Name">
                <Input placeholder="Person/Entity holding the license" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="responsible_department" label="Responsible Department">
                <Input placeholder="Department managing this license" />
              </Form.Item>
            </Col>
          </Row>

          {/* Risk Assessment */}
          <Divider orientation="left">Risk Assessment</Divider>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="criticality_level" label="Criticality Level">
                <Select placeholder="Select criticality level">
                  <Option value="Low">Low</Option>
                  <Option value="Medium">Medium</Option>
                  <Option value="High">High</Option>
                  <Option value="Critical">Critical</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="geographical_coverage" label="Geographical Coverage">
                <Select placeholder="Select coverage">
                  <Option value="State">State</Option>
                  <Option value="National">National</Option>
                  <Option value="International">International</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="business_impact" label="Business Impact">
            <TextArea
              rows={2}
              placeholder="Impact if license expires or is revoked"
            />
          </Form.Item>

          {/* Additional Information */}
          <Divider orientation="left">Additional Information</Divider>
          <Form.Item name="scope_of_license" label="Scope of License">
            <TextArea rows={2} placeholder="What does this license cover?" />
          </Form.Item>

          <Form.Item name="restrictions" label="Restrictions">
            <TextArea rows={2} placeholder="Any restrictions or conditions" />
          </Form.Item>

          <Form.Item name="notes" label="Notes">
            <TextArea rows={3} placeholder="Additional notes" />
          </Form.Item>

          {/* Form Actions */}
          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                icon={<SaveOutlined />}
              >
                {isEditMode ? 'Update License' : 'Create License'}
              </Button>
              <Button onClick={() => navigate('/legal/licenses')}>Cancel</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CreateLicense;
