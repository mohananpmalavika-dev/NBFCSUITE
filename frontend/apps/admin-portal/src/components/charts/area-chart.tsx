'use client'

import { AreaChart as RechartsAreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface AreaChartProps {
  data: any[]
  xKey: string
  areas: {
    key: string
    color: string
    name: string
  }[]
  height?: number
}

export function AreaChart({ data, xKey, areas, height = 300 }: AreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsAreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        {areas.map((area) => (
          <Area
            key={area.key}
            type="monotone"
            dataKey={area.key}
            stroke={area.color}
            fill={area.color}
            fillOpacity={0.6}
            name={area.name}
          />
        ))}
      </RechartsAreaChart>
    </ResponsiveContainer>
  )
}
