/**
 * Create Lead Modal Component
 * Form for creating new leads
 */

import React, { useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Row,
  Col
} from 'antd';
import crmService from '../../../services/crm.service';
import { LeadCreate, LeadSource } from '../../../types/crm.types';

const { Option } = Select;
const { TextArea } = Input;

interface CreateLeadModalProps {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateLeadModal: React.FC<CreateLeadModalProps> = ({
  visible,
  onClose,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const leadData: LeadCreate = {
        source: values.source,
        source_details: values.source_details,
        first_name: values.first_name,
        last_name: values.last_name,
        email: values.email,
        mobile: values.mobile,
        alternate_mobile: values.alternate_mobile,
        pincode: values.pincode,
        product_interest: values.product_interest,
        loan_amount_required: values.loan_amount_required,
        monthly_income: values.monthly_income,
        occupation: values.occupation,
        company_name: values.company_name,
        remarks: values.remarks
      };

      await crmService.createLead(leadData);
      message.success('Lead created successfully');
      form.resetFields();
      onSuccess();
    } catch (error: any) {
      message.error(error.message || 'Failed to create lead');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title="Create New Lead"
      open={visible}
      onCancel={handleCancel}
      onOk={() => form.submit()}
      confirmLoading={loading}
      width={800}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="source"
              label="Lead Source"
              rules={[{ required: true, message: 'Please select source' }]}
            >
              <Select placeholder="Select source">
                {Object.values(LeadSource).map((source) => (
                  <Option key={source} value={source}>
                    {source.replace('_', ' ').toUpperCase()}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="source_details"
              label="Source Details"
            >
              <Input placeholder="Campaign name, referral source, etc." />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="first_name"
              label="First Name"
              rules={[{ required: true, message: 'Please enter first name' }]}
            >
              <Input placeholder="Enter first name" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="last_name"
              label="Last Name"
            >
              <Input placeholder="Enter last name" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="mobile"
              label="Mobile Number"
              rules={[
                { required: true, message: 'Please enter mobile number' },
                { pattern: /^[0-9]{10,15}$/, message: 'Invalid mobile number' }
              ]}
            >
              <Input placeholder="Enter mobile number" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="email"
              label="Email"
              rules={[{ type: 'email', message: 'Invalid email' }]}
            >
              <Input placeholder="Enter email" />
            </Form.Item>
          </Col>
        </Row>


        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="product_interest"
              label="Product Interest"
            >
              <Input placeholder="Loan type, deposit, etc." />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="loan_amount_required"
              label="Loan Amount Required"
            >
              <InputNumber
                placeholder="Enter amount"
                style={{ width: '100%' }}
                min={0}
                formatter={(value) => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={(value) => value!.replace(/₹\s?|(,*)/g, '')}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="monthly_income"
              label="Monthly Income"
            >
              <InputNumber
                placeholder="Enter monthly income"
                style={{ width: '100%' }}
                min={0}
                formatter={(value) => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={(value) => value!.replace(/₹\s?|(,*)/g, '')}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="occupation"
              label="Occupation"
            >
              <Input placeholder="Enter occupation" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="company_name"
              label="Company Name"
            >
              <Input placeholder="Enter company name" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="pincode"
              label="Pincode"
            >
              <Input placeholder="Enter pincode" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="remarks"
          label="Remarks"
        >
          <TextArea
            rows={3}
            placeholder="Enter any additional remarks"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateLeadModal;


        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="product_interest"
              label="Product Interest"
            >
              <Input placeholder="e.g., Personal Loan, Home Loan" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="loan_amount_required"
              label="Loan Amount Required"
            >
              <InputNumber
                placeholder="Enter amount"
                style={{ width: '100%' }}
                min={0}
                formatter={value => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => value!.replace(/₹\s?|(,*)/g, '')}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="monthly_income"
              label="Monthly Income"
            >
              <InputNumber
                placeholder="Enter monthly income"
                style={{ width: '100%' }}
                min={0}
                formatter={value => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => value!.replace(/₹\s?|(,*)/g, '')}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="occupation"
              label="Occupation"
            >
              <Input placeholder="Enter occupation" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="company_name"
              label="Company Name"
            >
              <Input placeholder="Enter company name" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="pincode"
              label="Pincode"
            >
              <Input placeholder="Enter pincode" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="remarks"
          label="Remarks"
        >
          <TextArea rows={3} placeholder="Enter any additional notes" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateLeadModal;
