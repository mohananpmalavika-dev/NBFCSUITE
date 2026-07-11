/**
 * Lead Dashboard Component
 * Overview of lead statistics and metrics
 */

import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin, Alert } from 'antd';
import {
  UserAddOutlined,
  PhoneOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  CloseCircleOutlined,
  FireOutlined,
  ClockCircleOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import crmService from '../../services/crm.service';
import { LeadDashboardStats } from '../../types/crm.types';

const LeadDashboard: React.FC = () => {
  const [stats, setStats] = useState<LeadDashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await crmService.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  if (!stats) {
    return null;
  }

  return (
    <div style={{ padding: '24px' }}>
      <h2>Lead Dashboard</h2>
      
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        {/* Total Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Leads"
              value={stats.total_leads}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        {/* New Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="New Leads"
              value={stats.new_leads}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>

        {/* Contacted Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Contacted"
              value={stats.contacted_leads}
              prefix={<PhoneOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>

        {/* Qualified Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Qualified"
              value={stats.qualified_leads}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>


      <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
        {/* Converted Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Converted"
              value={stats.converted_leads}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Conversion Rate: {stats.conversion_rate}%
            </div>
          </Card>
        </Col>

        {/* Lost Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Lost"
              value={stats.lost_leads}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>

        {/* Hot Leads */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Hot Leads"
              value={stats.hot_leads}
              prefix={<FireOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Avg Score: {stats.avg_lead_score}
            </div>
          </Card>
        </Col>

        {/* Overdue Follow-ups */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Overdue Follow-ups"
              value={stats.overdue_follow_ups}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: stats.overdue_follow_ups > 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
        {/* Today's Follow-ups */}
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="Today's Follow-ups"
              value={stats.today_follow_ups}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        {/* Average Conversion Time */}
        {stats.avg_conversion_time_hours && (
          <Col xs={24} sm={12}>
            <Card>
              <Statistic
                title="Avg. Conversion Time"
                value={Math.round(stats.avg_conversion_time_hours / 24)}
                suffix="days"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
};

export default LeadDashboard;
