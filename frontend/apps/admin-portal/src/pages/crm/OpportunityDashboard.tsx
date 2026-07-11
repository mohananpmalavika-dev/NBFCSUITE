/**
 * Opportunity Dashboard Component
 * Overview of pipeline metrics, win/loss analysis, and sales forecasting
 */

import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin, Alert, Progress, Table, Tag } from 'antd';
import {
  DollarOutlined,
  TrophyOutlined,
  CloseCircleOutlined,
  RiseOutlined,
  FallOutlined,
  ClockCircleOutlined,
  FireOutlined,
  WarningOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import { Column, Pie } from '@ant-design/plots';
import opportunityService from '../../services/opportunity.service';
import {
  OpportunityDashboardStats,
  PipelineAnalytics,
  WinLossAnalysis,
  OpportunityStage
} from '../../types/crm.types';

const OpportunityDashboard: React.FC = () => {
  const [stats, setStats] = useState<OpportunityDashboardStats | null>(null);
  const [pipelineAnalytics, setPipelineAnalytics] = useState<PipelineAnalytics[]>([]);
  const [winLossAnalysis, setWinLossAnalysis] = useState<WinLossAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Load dashboard stats
      const statsData = await opportunityService.getDashboardStats();
      setStats(statsData);

      // Load pipeline analytics
      const analyticsData = await opportunityService.getPipelineAnalytics();
      setPipelineAnalytics(analyticsData);

      // Load win/loss analysis for current quarter
      const currentYear = new Date().getFullYear();
      const currentQuarter = Math.ceil((new Date().getMonth() + 1) / 3);
      const period = `${currentYear}-Q${currentQuarter}`;
      
      try {
        const winLossData = await opportunityService.getWinLossAnalysis(period);
        setWinLossAnalysis(winLossData);
      } catch (err) {
        console.warn('Win/loss analysis not available:', err);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStageColor = (stage: OpportunityStage): string => {
    const colors: Record<OpportunityStage, string> = {
      [OpportunityStage.PROSPECTING]: '#8c8c8c',
      [OpportunityStage.QUALIFICATION]: '#1890ff',
      [OpportunityStage.NEEDS_ANALYSIS]: '#13c2c2',
      [OpportunityStage.PROPOSAL]: '#fa8c16',
      [OpportunityStage.NEGOTIATION]: '#faad14',
      [OpportunityStage.CLOSED_WON]: '#52c41a',
      [OpportunityStage.CLOSED_LOST]: '#ff4d4f'
    };
    return colors[stage] || '#8c8c8c';
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

  // Prepare pipeline funnel data
  const pipelineFunnelData = pipelineAnalytics.map(item => ({
    stage: item.stage.replace(/_/g, ' ').toUpperCase(),
    count: item.count,
    value: item.total_value
  }));

  // Prepare stage distribution pie data
  const stageDistributionData = [
    { type: 'Prospecting', value: stats.prospecting_count },
    { type: 'Qualification', value: stats.qualification_count },
    { type: 'Needs Analysis', value: stats.needs_analysis_count },
    { type: 'Proposal', value: stats.proposal_count },
    { type: 'Negotiation', value: stats.negotiation_count }
  ].filter(item => item.value > 0);

  // Prepare win/loss data
  const winLossData = [
    { type: 'Won', value: stats.won_count },
    { type: 'Lost', value: stats.lost_count }
  ];

  // Pipeline funnel config
  const pipelineConfig = {
    data: pipelineFunnelData,
    xField: 'stage',
    yField: 'value',
    seriesField: 'stage',
    color: ({ stage }: any) => {
      const stageKey = stage.toLowerCase().replace(/ /g, '_') as OpportunityStage;
      return getStageColor(stageKey);
    },
    label: {
      position: 'top' as const,
      style: {
        fill: '#000000',
        opacity: 0.6,
      },
      formatter: (datum: any) => formatCurrency(datum.value)
    },
    xAxis: {
      label: {
        autoHide: false,
        autoRotate: false,
      },
    },
    meta: {
      stage: {
        alias: 'Pipeline Stage',
      },
      value: {
        alias: 'Total Value',
        formatter: (v: number) => formatCurrency(v),
      },
    },
  };

  // Stage distribution pie config
  const stageDistributionConfig = {
    appendPadding: 10,
    data: stageDistributionData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [
      {
        type: 'element-active',
      },
    ],
  };

  // Win/Loss pie config
  const winLossConfig = {
    appendPadding: 10,
    data: winLossData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    color: ['#52c41a', '#ff4d4f'],
    label: {
      type: 'inner',
      content: '{name}\n{value}',
      style: {
        fontSize: 14,
        textAlign: 'center',
      },
    },
    interactions: [
      {
        type: 'element-active',
      },
    ],
    legend: {
      position: 'bottom' as const,
    },
  };

  return (
    <div style={{ padding: '24px' }}>
      <h2>Opportunity Dashboard</h2>
      
      {/* Key Performance Indicators */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        {/* Total Pipeline Value */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Pipeline Value"
              value={stats.total_pipeline_value}
              prefix="₹"
              valueStyle={{ color: '#1890ff' }}
              formatter={(value) => formatCurrency(Number(value)).replace('₹', '')}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              {stats.active_opportunities} active opportunities
            </div>
          </Card>
        </Col>

        {/* Weighted Pipeline Value */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Weighted Pipeline"
              value={stats.weighted_pipeline_value}
              prefix="₹"
              valueStyle={{ color: '#52c41a' }}
              formatter={(value) => formatCurrency(Number(value)).replace('₹', '')}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Probability-adjusted value
            </div>
          </Card>
        </Col>

        {/* Won Opportunities */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Won Deals"
              value={stats.won_count}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#52c41a' }}>
              Value: {formatCurrency(stats.won_value)}
            </div>
          </Card>
        </Col>

        {/* Win Rate */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Win Rate"
              value={stats.win_rate}
              suffix="%"
              precision={1}
              valueStyle={{ color: stats.win_rate >= 50 ? '#52c41a' : '#faad14' }}
            />
            <Progress
              percent={stats.win_rate}
              showInfo={false}
              strokeColor={stats.win_rate >= 50 ? '#52c41a' : '#faad14'}
            />
          </Card>
        </Col>
      </Row>

      {/* Secondary Metrics */}
      <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
        {/* High Probability Opportunities */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="High Probability (>70%)"
              value={stats.high_probability_count}
              prefix={<FireOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Value: {formatCurrency(stats.high_probability_value)}
            </div>
          </Card>
        </Col>

        {/* Closing This Month */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Closing This Month"
              value={stats.closing_this_month_count}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Value: {formatCurrency(stats.closing_this_month_value)}
            </div>
          </Card>
        </Col>

        {/* Overdue Opportunities */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Overdue"
              value={stats.overdue_count}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Past expected close date
            </div>
          </Card>
        </Col>

        {/* Average Days in Pipeline */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Avg Days in Pipeline"
              value={stats.avg_days_in_pipeline}
              suffix="days"
              precision={0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
              Sales cycle duration
            </div>
          </Card>
        </Col>
      </Row>

      {/* Pipeline Funnel Chart */}
      <Row gutter={16} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Pipeline Funnel by Stage" extra={<Tag color="blue">Active Opportunities</Tag>}>
            <Column {...pipelineConfig} />
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Stage Distribution">
            <Pie {...stageDistributionConfig} />
          </Card>
        </Col>
      </Row>

      {/* Pipeline Analytics Table */}
      <Row gutter={16} style={{ marginTop: '16px' }}>
        <Col xs={24}>
          <Card title="Pipeline Analytics by Stage">
            <Table
              dataSource={pipelineAnalytics}
              rowKey="stage"
              pagination={false}
              columns={[
                {
                  title: 'Stage',
                  dataIndex: 'stage',
                  key: 'stage',
                  render: (stage: OpportunityStage) => (
                    <Tag color={getStageColor(stage)}>
                      {stage.replace(/_/g, ' ').toUpperCase()}
                    </Tag>
                  )
                },
                {
                  title: 'Count',
                  dataIndex: 'count',
                  key: 'count',
                  align: 'center'
                },
                {
                  title: 'Total Value',
                  dataIndex: 'total_value',
                  key: 'total_value',
                  align: 'right',
                  render: (value: number) => formatCurrency(value)
                },
                {
                  title: 'Avg Value',
                  dataIndex: 'avg_value',
                  key: 'avg_value',
                  align: 'right',
                  render: (value: number) => formatCurrency(value)
                },
                {
                  title: 'Avg Days',
                  dataIndex: 'avg_days_in_stage',
                  key: 'avg_days_in_stage',
                  align: 'center',
                  render: (days: number) => `${Math.round(days)} days`
                }
              ]}
            />
          </Card>
        </Col>
      </Row>

      {/* Win/Loss Analysis */}
      <Row gutter={16} style={{ marginTop: '16px' }}>
        <Col xs={24} lg={8}>
          <Card title="Win/Loss Distribution">
            <Pie {...winLossConfig} />
            <div style={{ marginTop: '16px', textAlign: 'center' }}>
              <Statistic
                title="Total Closed"
                value={stats.won_count + stats.lost_count}
                valueStyle={{ fontSize: '20px' }}
              />
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          {winLossAnalysis && (
            <Card title={`Win/Loss Analysis - ${winLossAnalysis.period}`}>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Deals Won"
                    value={winLossAnalysis.won_count}
                    prefix={<TrophyOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                  <div style={{ marginTop: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#888' }}>Total Value</div>
                    <div style={{ fontWeight: 600 }}>{formatCurrency(winLossAnalysis.won_value)}</div>
                  </div>
                  <div style={{ marginTop: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#888' }}>Avg Deal Size</div>
                    <div style={{ fontWeight: 600 }}>{formatCurrency(winLossAnalysis.avg_won_value)}</div>
                  </div>
                </Col>

                <Col span={8}>
                  <Statistic
                    title="Deals Lost"
                    value={winLossAnalysis.lost_count}
                    prefix={<CloseCircleOutlined />}
                    valueStyle={{ color: '#ff4d4f' }}
                  />
                  <div style={{ marginTop: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#888' }}>Total Value</div>
                    <div style={{ fontWeight: 600 }}>{formatCurrency(winLossAnalysis.lost_value)}</div>
                  </div>
                </Col>

                <Col span={8}>
                  <Statistic
                    title="Avg Days to Win"
                    value={Math.round(winLossAnalysis.avg_days_to_win)}
                    suffix="days"
                    prefix={<ClockCircleOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
              </Row>

              {winLossAnalysis.top_competitors.length > 0 && (
                <>
                  <Divider />
                  <h4>Top Competitors</h4>
                  <Table
                    dataSource={winLossAnalysis.top_competitors}
                    rowKey="name"
                    pagination={false}
                    size="small"
                    columns={[
                      {
                        title: 'Competitor',
                        dataIndex: 'name',
                        key: 'name'
                      },
                      {
                        title: 'Losses',
                        dataIndex: 'losses',
                        key: 'losses',
                        align: 'center'
                      }
                    ]}
                  />
                </>
              )}

              {Object.keys(winLossAnalysis.loss_reasons).length > 0 && (
                <>
                  <Divider />
                  <h4>Loss Reasons</h4>
                  {Object.entries(winLossAnalysis.loss_reasons).map(([reason, count]) => (
                    <div key={reason} style={{ marginBottom: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span>{reason.replace(/_/g, ' ').toUpperCase()}</span>
                        <span style={{ fontWeight: 600 }}>{count}</span>
                      </div>
                      <Progress
                        percent={(count / winLossAnalysis.lost_count) * 100}
                        showInfo={false}
                        strokeColor="#ff4d4f"
                      />
                    </div>
                  ))}
                </>
              )}
            </Card>
          )}
        </Col>
      </Row>

      {/* Activity Metrics */}
      <Row gutter={16} style={{ marginTop: '16px' }}>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="Activities This Week"
              value={stats.activities_this_week}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="Opportunities Without Activity (7+ days)"
              value={stats.opportunities_without_activity_7days}
              prefix={<FallOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#ff4d4f' }}>
              Need immediate attention
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default OpportunityDashboard;
