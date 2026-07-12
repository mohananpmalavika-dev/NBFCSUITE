/**
 * Upload Document Modal Component
 * Modal for uploading new documents
 */

import React, { useState } from 'react';
import { Modal, Form, Input, Select, Upload, DatePicker, message, Space, Tag } from 'antd';
import { UploadOutlined, InboxOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import dmsService from '../../../services/dms.service';
import { DocumentType, DocumentStatus, AccessLevel } from '../../../types/dms.types';

const { TextArea } = Input;
const { Option } = Select;
const { Dragger } = Upload;

interface UploadDocumentModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

const UploadDocumentModal: React.FC<UploadDocumentModalProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');

  const handleUpload = async () => {
    try {
      const values = await form.validateFields();
      
      if (fileList.length === 0) {
        message.warning('Please select a file to upload');
        return;
      }

      setUploading(true);

      const documentData = {
        title: values.title,
        description: values.description,
        document_type: values.document_type,
        status: values.status || DocumentStatus.DRAFT,
        access_level: values.access_level || AccessLevel.INTERNAL,
        customer_id: values.customer_id,
        loan_id: values.loan_id,
        policy_id: values.policy_id,
        expiry_date: values.expiry_date?.format('YYYY-MM-DD'),
        tags: tags,
        file: fileList[0].originFileObj as File,
      };

      await dmsService.createDocument(documentData);
      message.success('Document uploaded successfully');
      form.resetFields();
      setFileList([]);
      setTags([]);
      onSuccess();
    } catch (error: any) {
      if (error.errorFields) {
        message.error('Please fill in all required fields');
      } else {
        message.error(error.message || 'Failed to upload document');
      }
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    setFileList([]);
    setTags([]);
    onCancel();
  };

  const uploadProps = {
    onRemove: () => {
      setFileList([]);
    },
    beforeUpload: (file: File) => {
      setFileList([file as any]);
      return false;
    },
    fileList,
    maxCount: 1,
  };

  const addTag = () => {
    if (tagInput && !tags.includes(tagInput)) {
      setTags([...tags, tagInput]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <Modal
      title="Upload Document"
      open={visible}
      onCancel={handleCancel}
      onOk={handleUpload}
      confirmLoading={uploading}
      okText="Upload"
      width={700}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        name="upload_document"
      >
        <Form.Item
          name="title"
          label="Document Title"
          rules={[{ required: true, message: 'Please enter document title' }]}
        >
          <Input placeholder="Enter document title" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
        >
          <TextArea rows={3} placeholder="Enter document description (optional)" />
        </Form.Item>

        <Form.Item
          name="document_type"
          label="Document Type"
          rules={[{ required: true, message: 'Please select document type' }]}
        >
          <Select placeholder="Select document type">
            {Object.values(DocumentType).map(type => (
              <Option key={type} value={type}>
                {type.replace(/_/g, ' ').toUpperCase()}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="status"
          label="Status"
          initialValue={DocumentStatus.DRAFT}
        >
          <Select>
            {Object.values(DocumentStatus).map(status => (
              <Option key={status} value={status}>
                {status.replace(/_/g, ' ').toUpperCase()}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="access_level"
          label="Access Level"
          initialValue={AccessLevel.INTERNAL}
        >
          <Select>
            {Object.values(AccessLevel).map(level => (
              <Option key={level} value={level}>
                {level.toUpperCase()}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="expiry_date"
          label="Expiry Date (Optional)"
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item label="Tags (Optional)">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input.Group compact>
              <Input
                style={{ width: 'calc(100% - 100px)' }}
                placeholder="Add a tag"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onPressEnter={addTag}
              />
              <button
                type="button"
                onClick={addTag}
                style={{
                  width: '100px',
                  padding: '4px 15px',
                  border: '1px solid #d9d9d9',
                  borderLeft: 0,
                  backgroundColor: '#fff',
                  cursor: 'pointer',
                }}
              >
                Add Tag
              </button>
            </Input.Group>
            {tags.length > 0 && (
              <div>
                {tags.map(tag => (
                  <Tag
                    key={tag}
                    closable
                    onClose={() => removeTag(tag)}
                  >
                    {tag}
                  </Tag>
                ))}
              </div>
            )}
          </Space>
        </Form.Item>

        <Form.Item
          name="customer_id"
          label="Customer ID (Optional)"
        >
          <Input type="number" placeholder="Enter customer ID" />
        </Form.Item>

        <Form.Item
          name="loan_id"
          label="Loan ID (Optional)"
        >
          <Input type="number" placeholder="Enter loan ID" />
        </Form.Item>

        <Form.Item
          name="policy_id"
          label="Policy ID (Optional)"
        >
          <Input type="number" placeholder="Enter policy ID" />
        </Form.Item>

        <Form.Item
          label="File"
          rules={[{ required: true, message: 'Please select a file' }]}
        >
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint">
              Support for single file upload. Max file size: 50MB
            </p>
          </Dragger>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UploadDocumentModal;
