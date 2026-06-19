<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart, GaugeChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { statsApi, helpApi } from '@/api'
import type { StatsOverview, HelpRequest, DeviceStats, FamilyEfficiency, RiskStats } from '@/types'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  ToolboxComponent
])

import type { PracticeStats } from '@/types'

const overview = ref<StatsOverview | null>(null)
const recentHelps = ref<HelpRequest[]>([])
const timeline = ref<{ date: string; count: number }[]>([])
const practiceStats = ref<PracticeStats | null>(null)
const deviceStats = ref<DeviceStats | null>(null)
const familyEfficiency = ref<FamilyEfficiency[]>([])
const riskStats = ref<RiskStats | null>(null)

const typeColors = {
  '看不清字': '#667eea',
  '找不到入口': '#11998e',
  '误触广告': '#f5576c',
  '不会切换网络': '#f59e0b',
  '支付设置': '#8b5cf6',
  '声音太小': '#06b6d4',
  '不会拍照': '#ec4899',
  '其他问题': '#94a3b8'
}

const problemTypeOption = computed(() => {
  const data = overview.value?.problem_types || []
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    legend: {
      bottom: 0,
      left: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 12
        },
        data: data.map((item) => ({
          value: item.count,
          name: item.type,
          itemStyle: { color: (typeColors as any)[item.type] || '#667eea' }
        }))
      }
    ]
  }
})

const durationGaugeOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 60,
      progress: { show: true, width: 18 },
      axisLine: { lineStyle: { width: 18, color: [[1, '#e2e8f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, '0%'],
        fontSize: 36,
        fontWeight: 'bold',
        formatter: '{value} 分钟',
        color: '#667eea'
      },
      data: [{ value: overview.value?.average_duration_minutes || 0 }]
    }
  ]
}))

const repeatRateOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      progress: { show: true, width: 18, itemStyle: { color: '#f5576c' } },
      axisLine: { lineStyle: { width: 18, color: [[1, '#e2e8f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, '0%'],
        fontSize: 36,
        fontWeight: 'bold',
        formatter: '{value}%',
        color: '#f5576c'
      },
      data: [{ value: overview.value?.repeat_rate_percent || 0 }]
    }
  ]
}))

const independentRateOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      progress: { show: true, width: 18, itemStyle: { color: '#11998e' } },
      axisLine: { lineStyle: { width: 18, color: [[1, '#e2e8f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, '0%'],
        fontSize: 36,
        fontWeight: 'bold',
        formatter: '{value}%',
        color: '#11998e'
      },
      data: [{ value: overview.value?.independent_rate_percent || 0 }]
    }
  ]
}))

const practiceCompletionRateOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      progress: { show: true, width: 18, itemStyle: { color: '#8b5cf6' } },
      axisLine: { lineStyle: { width: 18, color: [[1, '#e2e8f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: false },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, '0%'],
        fontSize: 36,
        fontWeight: 'bold',
        formatter: '{value}%',
        color: '#8b5cf6'
      },
      data: [{ value: practiceStats.value?.completion_rate_percent || 0 }]
    }
  ]
}))

const timelineOption = computed(() => {
  const data = timeline.value || []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map((d) => d.date),
      axisLabel: { fontSize: 11 },
      axisLine: { lineStyle: { color: '#e2e8f0' } }
    },
    yAxis: {
      type: 'value',
      name: '求助次数',
      nameTextStyle: { fontSize: 12, color: '#64748b' },
      axisLabel: { fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [
      {
        type: 'line',
        data: data.map((d) => d.count),
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#667eea' },
        itemStyle: { color: '#667eea' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.35)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.02)' }
            ]
          }
        }
      }
    ]
  }
})

const brandDistributionOption = computed(() => {
  const data = deviceStats.value?.brand_distribution || []
  const brandColors = ['#667eea', '#f5576c', '#f59e0b', '#11998e', '#8b5cf6', '#ec4899', '#06b6d4']
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    legend: {
      bottom: 0,
      left: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '68%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 12
      },
      data: data.map((item, idx) => ({
        value: item.count,
        name: item.brand,
        itemStyle: { color: brandColors[idx % brandColors.length] }
      }))
    }]
  }
})

const brandDurationOption = computed(() => {
  const data = deviceStats.value?.brand_avg_duration || []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.brand),
      axisLabel: { fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '分钟',
      nameTextStyle: { fontSize: 12, color: '#64748b' },
      axisLabel: { fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.avg_duration),
      barWidth: 36,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        }
      }
    }]
  }
})

const brandProblemOption = computed(() => {
  const data = deviceStats.value?.brand_problem_distribution || []
  if (data.length === 0) return {}
  const brands = [...new Set(data.map(d => d.brand))]
  const types = [...new Set(data.map(d => d.problem_type))]
  const typeColorList = ['#667eea', '#11998e', '#f5576c', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#94a3b8']
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      bottom: 0,
      textStyle: { fontSize: 11 }
    },
    grid: { left: 60, right: 20, top: 30, bottom: 60 },
    xAxis: {
      type: 'category',
      data: brands,
      axisLabel: { fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '次数',
      nameTextStyle: { fontSize: 12, color: '#64748b' },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: types.map((type, idx) => ({
      name: type,
      type: 'bar',
      stack: 'total',
      data: brands.map(b => {
        const found = data.find(d => d.brand === b && d.problem_type === type)
        return found ? found.count : 0
      }),
      itemStyle: { color: typeColorList[idx % typeColorList.length] }
    }))
  }
})

const familyResponseTimeOption = computed(() => {
  const data = familyEfficiency.value
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        return `${item.name}<br/>平均响应时长：${item.value} 分钟`
      }
    },
    grid: { left: 60, right: 20, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.family_member.name),
      axisLabel: { fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '分钟',
      nameTextStyle: { fontSize: 12, color: '#64748b' },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.avg_response_minutes),
      barWidth: 36,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        }
      }
    }]
  }
})

const familyResolutionTimeOption = computed(() => {
  const data = familyEfficiency.value
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        return `${item.name}<br/>平均解决时长：${item.value} 分钟`
      }
    },
    grid: { left: 60, right: 20, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.family_member.name),
      axisLabel: { fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '分钟',
      nameTextStyle: { fontSize: 12, color: '#64748b' },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.avg_resolution_minutes),
      barWidth: 36,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#059669' }
          ]
        }
      }
    }]
  }
})

const familyVolumeOption = computed(() => {
  const data = familyEfficiency.value
  return {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.name}<br/>处理数量：${params.value} 次<br/>占比：${params.percent}%`
      }
    },
    legend: {
      bottom: 0,
      left: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 12
        },
        data: data.map((d, idx) => {
          const colors = ['#667eea', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4']
          return {
            value: d.total_count,
            name: d.family_member.name,
            itemStyle: { color: colors[idx % colors.length] }
          }
        })
      }
    ]
  }
})

const scamTypeDistributionOption = computed(() => {
  const data = riskStats.value?.scam_type_distribution || []
  const scamColors = ['#ef4444', '#f59e0b', '#667eea', '#8b5cf6', '#06b6d4', '#ec4899']
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    legend: {
      bottom: 0,
      left: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '72%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 12
      },
      data: data.map((item, idx) => ({
        value: item.count,
        name: item.scam_type,
        itemStyle: { color: scamColors[idx % scamColors.length] }
      }))
    }]
  }
})

const disposalDistributionOption = computed(() => {
  const data = riskStats.value?.disposal_distribution || []
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
    legend: {
      bottom: 0,
      left: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '72%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 12
      },
      data: data.map((item, idx) => {
        const colors = ['#10b981', '#ef4444', '#f59e0b', '#64748b', '#667eea']
        return {
          value: item.count,
          name: item.disposal_type,
          itemStyle: { color: colors[idx % colors.length] }
        }
      })
    }]
  }
})

const fetchData = async () => {
  overview.value = await statsApi.overview()
  recentHelps.value = (await helpApi.list()).slice(0, 6)
  timeline.value = await statsApi.timeline()
  practiceStats.value = await statsApi.practice()
  deviceStats.value = await statsApi.device()
  familyEfficiency.value = await statsApi.familyEfficiency()
  try { riskStats.value = await statsApi.risk() } catch (e) { console.error(e) }
}

const formatTime = (t?: string) => {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(fetchData)
</script>

<template>
  <div>
    <div class="grid grid-4 mb-6">
      <div class="card stat-card stat-blue">
        <div class="stat-icon">📞</div>
        <div class="stat-info">
          <div class="stat-label">累计求助</div>
          <div class="stat-value">{{ overview?.total_requests || 0 }}</div>
          <div class="stat-sub">
            待处理 <strong class="text-orange">{{ overview?.pending_count || 0 }}</strong>
            · 已解决 <strong class="text-green">{{ overview?.resolved_count || 0 }}</strong>
          </div>
        </div>
      </div>

      <div class="card stat-card stat-purple">
        <div class="stat-icon">📋</div>
        <div class="stat-info">
          <div class="stat-label">步骤卡数量</div>
          <div class="stat-value">{{ overview?.total_stepcards || 0 }}</div>
          <div class="stat-sub">沉淀的可复用操作指南</div>
        </div>
      </div>

      <div class="card stat-card stat-green">
        <div class="stat-icon">⏱️</div>
        <div class="stat-info">
          <div class="stat-label">平均解决时长</div>
          <div class="stat-value">{{ overview?.average_duration_minutes || 0 }} 分钟</div>
          <div class="stat-sub">从发起到解决的平均时间</div>
        </div>
      </div>

      <div class="card stat-card stat-orange">
        <div class="stat-icon">🔄</div>
        <div class="stat-info">
          <div class="stat-label">重复求助率</div>
          <div class="stat-value">{{ overview?.repeat_rate_percent || 0 }}%</div>
          <div class="stat-sub">同类问题再次求助的比例</div>
        </div>
      </div>
    </div>

    <div class="grid grid-3 mb-6">
      <div class="card">
        <h3 class="section-title mb-4">📊 问题类型分布</h3>
        <VChart :option="problemTypeOption" style="height: 320px" autoresize />
      </div>

      <div class="card">
        <h3 class="section-title mb-4">📈 求助量趋势</h3>
        <VChart :option="timelineOption" style="height: 320px" autoresize />
      </div>

      <div class="card">
        <h3 class="section-title mb-4">✅ 独立完成比例</h3>
        <VChart :option="independentRateOption" style="height: 260px" autoresize />
        <div class="gauge-desc">
          老人通过步骤卡独立完成解决的问题占比
        </div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h3 class="section-title mb-4">🔴 重复求助率分析</h3>
        <VChart :option="repeatRateOption" style="height: 260px" autoresize />
        <div class="gauge-desc">
          相同问题类型重复出现的比例，越低越好
        </div>
        <div class="rate-comments">
          <div class="comment-item">
            <span class="comment-dot good"></span>
            <span>重复率低于 20%：步骤卡效果很好</span>
          </div>
          <div class="comment-item">
            <span class="comment-dot warn"></span>
            <span>重复率 20%-40%：部分步骤需要优化</span>
          </div>
          <div class="comment-item">
            <span class="comment-dot bad"></span>
            <span>重复率高于 40%：需要重新梳理步骤卡</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title mb-4">🕒 最近求助记录</h3>
        <div class="recent-list">
          <div v-for="h in recentHelps" :key="h.id" class="recent-item">
            <div class="recent-left">
              <div class="recent-avatar">
                {{ h.problem_type === '看不清字' ? '🔍' : h.problem_type === '误触广告' ? '🚫' : h.problem_type === '不会切换网络' ? '📶' : '❓' }}
              </div>
              <div>
                <div class="recent-title">{{ h.title }}</div>
                <div class="recent-meta">
                  <span class="tag">{{ h.problem_type }}</span>
                  <span class="text-sm text-muted">{{ h.requester?.name || '老人' }}</span>
                </div>
              </div>
            </div>
            <div class="recent-right">
              <span :class="['badge', 'badge-' + h.status]">
                {{ h.status === 'pending' ? '待处理' : '已解决' }}
              </span>
              <span class="text-sm text-muted">{{ formatTime(h.created_at) }}</span>
            </div>
          </div>
          <div v-if="recentHelps.length === 0" class="empty-state" style="padding: 40px;">
            <div class="empty-state-icon">📭</div>
            <div>暂无求助记录</div>
          </div>
        </div>
      </div>
    </div>

    <div class="practice-stats-section">
      <h3 class="section-title mb-4">📝 练习数据统计</h3>
      <div class="grid grid-3">
        <div class="card">
          <h3 class="section-title mb-4">✅ 练习完成率</h3>
          <VChart :option="practiceCompletionRateOption" style="height: 260px" autoresize />
          <div class="gauge-desc">
            老人通过自主练习完成的比例
          </div>
          <div class="practice-numbers">
            <div class="practice-num-item">
              <span class="practice-num-value">{{ practiceStats?.total_practices || 0 }}</span>
              <span class="practice-num-label">总练习次数</span>
            </div>
            <div class="practice-num-item">
              <span class="practice-num-value text-green">{{ practiceStats?.completed_practices || 0 }}</span>
              <span class="practice-num-label">已完成</span>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title mb-4">⚠️ 卡住步骤 Top 5</h3>
          <div class="stuck-steps-list">
            <div
              v-for="(item, index) in practiceStats?.top_stuck_steps || []"
              :key="index"
              class="stuck-step-item"
            >
              <div class="stuck-step-rank">{{ index + 1 }}</div>
              <div class="stuck-step-info">
                <div class="stuck-step-title">{{ item.card_title }}</div>
                <div class="stuck-step-detail">第 {{ item.step_number }} 步</div>
              </div>
              <div class="stuck-step-count">
                <span class="count-num">{{ item.stuck_count }}</span>
                <span class="count-label">次</span>
              </div>
            </div>
            <div v-if="!practiceStats?.top_stuck_steps?.length" class="empty-state" style="padding: 40px;">
              <div class="empty-state-icon">📊</div>
              <div>暂无卡住步骤数据</div>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title mb-4">🔄 练习转求助</h3>
          <div class="convert-stats">
            <div class="convert-main">
              <div class="convert-icon">📞</div>
              <div class="convert-number">{{ practiceStats?.converted_to_help_count || 0 }}</div>
              <div class="convert-label">从练习转求助次数</div>
            </div>
            <div class="convert-desc">
              <p>当老人在练习中遇到困难时，可以一键发起求助，家人能看到详细的练习记录和卡住的步骤。</p>
            </div>
            <div class="convert-rate">
              <div class="rate-label">转求助比例</div>
              <div class="rate-bar">
                <div
                  class="rate-fill"
                  :style="{ width: practiceStats && practiceStats.total_practices > 0
                    ? (practiceStats.converted_to_help_count / practiceStats.total_practices * 100) + '%'
                    : '0%' }"
                ></div>
              </div>
              <div class="rate-value">
                {{ practiceStats && practiceStats.total_practices > 0
                  ? (practiceStats.converted_to_help_count / practiceStats.total_practices * 100).toFixed(1)
                  : 0 }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card mt-6">
      <h3 class="section-title mb-4">🏆 练习最多的步骤卡</h3>
      <div class="top-practiced-list">
        <div
          v-for="(item, index) in practiceStats?.top_practiced_cards || []"
          :key="item.id"
          class="top-practiced-item"
        >
          <div :class="['top-practiced-rank', { 'rank-1': index === 0, 'rank-2': index === 1, 'rank-3': index === 2 }]">
            {{ index + 1 }}
          </div>
          <div class="top-practiced-info">
            <div class="top-practiced-title">{{ item.title }}</div>
          </div>
          <div class="top-practiced-count">
            <span class="count-num">{{ item.practice_count }}</span>
            <span class="count-label">次练习</span>
          </div>
        </div>
        <div v-if="!practiceStats?.top_practiced_cards?.length" class="empty-state" style="padding: 30px;">
          <div class="empty-state-icon">🏆</div>
          <div>暂无练习数据</div>
        </div>
      </div>
    </div>

    <div class="device-stats-section mt-6">
      <h3 class="section-title mb-4">📱 设备维度分析</h3>
      <div class="grid grid-3">
        <div class="card">
          <h3 class="section-title mb-4">📊 品牌求助分布</h3>
          <VChart v-if="deviceStats?.brand_distribution?.length" :option="brandDistributionOption" style="height: 320px" autoresize />
          <div v-else class="empty-state" style="padding: 40px;">
            <div class="empty-state-icon">📊</div>
            <div>暂无品牌数据</div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title mb-4">⏱️ 品牌平均解决时长</h3>
          <VChart v-if="deviceStats?.brand_avg_duration?.length" :option="brandDurationOption" style="height: 320px" autoresize />
          <div v-else class="empty-state" style="padding: 40px;">
            <div class="empty-state-icon">⏱️</div>
            <div>暂无解决时长数据</div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title mb-4">🏷️ 高频困难标签</h3>
          <div class="difficulty-tags-list">
            <div
              v-for="(item, index) in deviceStats?.top_difficulty_tags || []"
              :key="index"
              class="difficulty-tag-item"
            >
              <div :class="['difficulty-tag-rank', { 'rank-1': index === 0, 'rank-2': index === 1, 'rank-3': index === 2 }]">
                {{ index + 1 }}
              </div>
              <div class="difficulty-tag-name">{{ item.tag }}</div>
              <div class="difficulty-tag-count">
                <span class="count-num">{{ item.count }}</span>
                <span class="count-label">人</span>
              </div>
            </div>
            <div v-if="!deviceStats?.top_difficulty_tags?.length" class="empty-state" style="padding: 40px;">
              <div class="empty-state-icon">🏷️</div>
              <div>暂无困难标签数据</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card mt-6">
        <h3 class="section-title mb-4">📱 品牌问题类型分布</h3>
        <VChart v-if="deviceStats?.brand_problem_distribution?.length" :option="brandProblemOption" style="height: 380px" autoresize />
        <div v-else class="empty-state" style="padding: 40px;">
          <div class="empty-state-icon">📱</div>
          <div>暂无品牌问题分布数据</div>
        </div>
      </div>

      <div class="grid grid-2 mt-6">
        <div class="card">
          <h3 class="section-title mb-4">💻 系统版本分布</h3>
          <div class="system-list">
            <div
              v-for="item in deviceStats?.system_distribution || []"
              :key="item.system"
              class="system-item"
            >
              <div class="system-name">{{ item.system || '未知' }}</div>
              <div class="system-bar-wrap">
                <div
                  class="system-bar"
                  :style="{ width: deviceStats && deviceStats.system_distribution.length > 0
                    ? (item.count / Math.max(...deviceStats.system_distribution.map(s => s.count)) * 100) + '%'
                    : '0%' }"
                ></div>
              </div>
              <div class="system-count">{{ item.count }} 次</div>
            </div>
            <div v-if="!deviceStats?.system_distribution?.length" class="empty-state" style="padding: 30px;">
              <div class="empty-state-icon">💻</div>
              <div>暂无系统版本数据</div>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title mb-4">📋 品牌解决时长对比</h3>
          <div class="brand-duration-list">
            <div
              v-for="item in deviceStats?.brand_avg_duration || []"
              :key="item.brand"
              class="brand-duration-item"
            >
              <div class="brand-duration-name">{{ item.brand }}</div>
              <div class="brand-duration-bar-wrap">
                <div
                  class="brand-duration-bar"
                  :style="{ width: deviceStats && deviceStats.brand_avg_duration.length > 0
                    ? (item.avg_duration / Math.max(...deviceStats.brand_avg_duration.map(b => b.avg_duration)) * 100) + '%'
                    : '0%' }"
                ></div>
              </div>
              <div class="brand-duration-value">{{ item.avg_duration }} 分钟</div>
            </div>
            <div v-if="!deviceStats?.brand_avg_duration?.length" class="empty-state" style="padding: 30px;">
              <div class="empty-state-icon">📋</div>
              <div>暂无解决时长数据</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="family-efficiency-section mt-6">
      <h3 class="section-title mb-4">👨‍👩‍👧‍👦 家属响应效率分析</h3>

      <div v-if="familyEfficiency.length > 0">
        <div class="grid grid-3 mb-6">
          <div class="card">
            <h3 class="section-title mb-4">📊 处理数量分布</h3>
            <VChart :option="familyVolumeOption" style="height: 320px" autoresize />
          </div>

          <div class="card">
            <h3 class="section-title mb-4">⏱️ 平均响应时长</h3>
            <VChart :option="familyResponseTimeOption" style="height: 320px" autoresize />
          </div>

          <div class="card">
            <h3 class="section-title mb-4">✅ 平均解决时长</h3>
            <VChart :option="familyResolutionTimeOption" style="height: 320px" autoresize />
          </div>
        </div>

        <div class="card">
        <h3 class="section-title mb-4">📋 家属效率明细</h3>
        <div class="family-table">
          <div class="family-table-header">
            <div class="col-name">家属姓名</div>
            <div class="col-stat">处理总数</div>
            <div class="col-stat">已解决</div>
            <div class="col-stat">待处理</div>
            <div class="col-stat">平均响应</div>
            <div class="col-stat">平均解决</div>
            <div class="col-stat">转派次数</div>
            <div class="col-stat">超时次数</div>
            <div class="col-status">在线状态</div>
            <div class="col-status">值班状态</div>
          </div>
          <div class="family-table-body">
            <div
              v-for="(fe, idx) in familyEfficiency"
              :key="fe.family_member.id"
              class="family-table-row"
            >
              <div class="col-name">
                <span :class="['rank-badge', { 'rank-1': idx === 0, 'rank-2': idx === 1, 'rank-3': idx === 2 }]">
                  {{ idx + 1 }}
                </span>
                {{ fe.family_member.name }}
              </div>
              <div class="col-stat">
                <span class="stat-number">{{ fe.total_count }}</span>
              </div>
              <div class="col-stat">
                <span class="stat-number text-green">{{ fe.resolved_count }}</span>
              </div>
              <div class="col-stat">
                <span class="stat-number text-orange">{{ fe.pending_count }}</span>
              </div>
              <div class="col-stat">
                <span class="stat-number">{{ fe.avg_response_minutes }} 分</span>
              </div>
              <div class="col-stat">
                <span class="stat-number">{{ fe.avg_resolution_minutes }} 分</span>
              </div>
              <div class="col-stat">
                <span :class="['stat-badge', fe.transfer_count > 0 ? 'badge-warning' : 'badge-success']">
                  {{ fe.transfer_count }} 次
                </span>
              </div>
              <div class="col-stat">
                <span :class="['stat-badge', fe.timeout_count > 0 ? 'badge-danger' : 'badge-success']">
                  {{ fe.timeout_count }} 次
                </span>
              </div>
              <div class="col-status">
                <span v-if="fe.family_member.is_online" class="status-online">在线</span>
                <span v-else class="status-offline">离线</span>
              </div>
              <div class="col-status">
                <span v-if="fe.family_member.is_on_duty" class="duty-active">值班中</span>
                <span v-else class="duty-inactive">休息</span>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card">
        <div class="empty-state" style="padding: 60px;">
          <div class="empty-state-icon">📊</div>
          <div>暂无家属效率数据</div>
        </div>
      </div>
    </div>

    <div class="risk-stats-section mt-6">
      <h3 class="section-title mb-4">🛡️ 风险求助分析</h3>

      <div v-if="riskStats && riskStats.total_risk_requests > 0">
        <div class="grid grid-4 mb-6">
          <div class="card stat-card stat-red">
            <div class="stat-icon">🛡️</div>
            <div class="stat-info">
              <div class="stat-label">风险求助总数</div>
              <div class="stat-value">{{ riskStats.total_risk_requests }}</div>
              <div class="stat-sub">标记为诈骗风险的求助</div>
            </div>
          </div>

          <div class="card stat-card stat-green">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <div class="stat-label">成功拦截次数</div>
              <div class="stat-value text-green">{{ riskStats.blocked_count }}</div>
              <div class="stat-sub">已阻止的风险求助</div>
            </div>
          </div>

          <div class="card stat-card stat-orange">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <div class="stat-label">涉及金额汇总</div>
              <div class="stat-value">¥{{ riskStats.total_involved_amount }}</div>
              <div class="stat-sub">所有风险求助涉及的总金额</div>
            </div>
          </div>

          <div class="card stat-card stat-purple">
            <div class="stat-icon">⏱️</div>
            <div class="stat-info">
              <div class="stat-label">平均响应时长</div>
              <div class="stat-value">{{ riskStats.avg_response_minutes }} 分钟</div>
              <div class="stat-sub">风险求助从发到响应的时间</div>
            </div>
          </div>
        </div>

        <div class="grid grid-2 mb-6">
          <div class="card">
            <h3 class="section-title mb-4">📊 诈骗类型分布</h3>
            <VChart v-if="riskStats.scam_type_distribution.length" :option="scamTypeDistributionOption" style="height: 320px" autoresize />
            <div v-else class="empty-state" style="padding: 40px;">
              <div class="empty-state-icon">📊</div>
              <div>暂无诈骗类型数据</div>
            </div>
          </div>

          <div class="card">
            <h3 class="section-title mb-4">📋 处置方式分布</h3>
            <VChart v-if="riskStats.disposal_distribution.length" :option="disposalDistributionOption" style="height: 320px" autoresize />
            <div v-else class="empty-state" style="padding: 40px;">
              <div class="empty-state-icon">📋</div>
              <div>暂无处置数据</div>
            </div>
          </div>
        </div>

        <div class="grid grid-3">
          <div class="card">
            <h3 class="section-title mb-4">🔑 高频风险关键词</h3>
            <div class="keyword-list">
              <div
                v-for="(item, index) in riskStats.top_risk_keywords"
                :key="index"
                class="keyword-item"
              >
                <div :class="['keyword-rank', { 'rank-1': index === 0, 'rank-2': index === 1, 'rank-3': index === 2 }]">
                  {{ index + 1 }}
                </div>
                <div class="keyword-name">{{ item.keyword }}</div>
                <div class="keyword-count">
                  <span class="count-num">{{ item.count }}</span>
                  <span class="count-label">次</span>
                </div>
              </div>
              <div v-if="!riskStats.top_risk_keywords.length" class="empty-state" style="padding: 30px;">
                <div class="empty-state-icon">🔑</div>
                <div>暂无关键词数据</div>
              </div>
            </div>
          </div>

          <div class="card">
            <h3 class="section-title mb-4">⚠️ 风险泄露情况</h3>
            <div class="leak-stats">
              <div class="leak-item">
                <div class="leak-icon">🔑</div>
                <div class="leak-info">
                  <div class="leak-label">泄露验证码</div>
                  <div class="leak-value text-danger">{{ riskStats.leaked_verification_code_count }} 次</div>
                </div>
              </div>
              <div class="leak-item">
                <div class="leak-icon">🔐</div>
                <div class="leak-info">
                  <div class="leak-label">泄露支付密码</div>
                  <div class="leak-value text-danger">{{ riskStats.leaked_payment_password_count }} 次</div>
                </div>
              </div>
              <div class="leak-item">
                <div class="leak-icon">🔗</div>
                <div class="leak-info">
                  <div class="leak-label">点击可疑链接</div>
                  <div class="leak-value text-warning">{{ riskStats.clicked_link_count }} 次</div>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <h3 class="section-title mb-4">📈 拦截率分析</h3>
            <div class="interception-stats">
              <div class="interception-main">
                <div class="interception-icon">🛡️</div>
                <div class="interception-rate">
                  {{ riskStats.total_risk_requests > 0 ? (riskStats.blocked_count / riskStats.total_risk_requests * 100).toFixed(1) : 0 }}%
                </div>
                <div class="interception-label">风险拦截率</div>
              </div>
              <div class="interception-detail">
                <div class="interception-bar">
                  <div class="interception-fill" :style="{ width: (riskStats.total_risk_requests > 0 ? riskStats.blocked_count / riskStats.total_risk_requests * 100 : 0) + '%' }"></div>
                </div>
                <div class="interception-numbers">
                  <span>已拦截 {{ riskStats.blocked_count }} 次</span>
                  <span>共 {{ riskStats.total_risk_requests }} 次风险求助</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card">
        <div class="empty-state" style="padding: 60px;">
          <div class="empty-state-icon">🛡️</div>
          <div>暂无风险求助数据</div>
          <p class="text-sm text-muted mt-2">当老人发起风险求助后，这里将展示防诈骗分析数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  display: flex;
  gap: 16px;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.stat-blue::before { background: linear-gradient(180deg, #667eea, #764ba2); }
.stat-purple::before { background: linear-gradient(180deg, #8b5cf6, #ec4899); }
.stat-green::before { background: linear-gradient(180deg, #11998e, #38ef7d); }
.stat-orange::before { background: linear-gradient(180deg, #f59e0b, #ef4444); }

.stat-icon {
  font-size: 44px;
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 30px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-sub {
  font-size: 12px;
  color: #94a3b8;
}

.text-green { color: #15803d; }
.text-orange { color: #c2410c; }

.gauge-desc {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  margin-top: -10px;
  padding-bottom: 8px;
}

.rate-comments {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #475569;
}

.comment-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.comment-dot.good { background: #11998e; }
.comment-dot.warn { background: #f59e0b; }
.comment-dot.bad { background: #ef4444; }

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 12px;
  border-radius: 12px;
  transition: background 0.2s;
}

.recent-item:hover {
  background: #f8fafc;
}

.recent-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recent-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.recent-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 4px;
}

.recent-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recent-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.practice-stats-section {
  margin-top: 20px;
}

.practice-numbers {
  display: flex;
  justify-content: space-around;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
  margin-top: 8px;
}

.practice-num-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.practice-num-value {
  font-size: 22px;
  font-weight: 800;
  color: #1e293b;
}

.practice-num-label {
  font-size: 12px;
  color: #64748b;
}

.stuck-steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stuck-step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.2s;
}

.stuck-step-item:hover {
  background: #f1f5f9;
}

.stuck-step-rank {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.stuck-step-info {
  flex: 1;
  min-width: 0;
}

.stuck-step-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stuck-step-detail {
  font-size: 12px;
  color: #ef4444;
}

.stuck-step-count {
  flex-shrink: 0;
  text-align: right;
}

.stuck-step-count .count-num {
  font-size: 20px;
  font-weight: 800;
  color: #ef4444;
}

.stuck-step-count .count-label {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 2px;
}

.convert-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.convert-main {
  text-align: center;
  padding: 20px 0;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16px;
}

.convert-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.convert-number {
  font-size: 42px;
  font-weight: 800;
  color: #92400e;
  line-height: 1;
  margin-bottom: 4px;
}

.convert-label {
  font-size: 14px;
  color: #b45309;
  font-weight: 600;
}

.convert-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.convert-rate {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rate-label {
  font-size: 13px;
  color: #475569;
  font-weight: 600;
}

.rate-bar {
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  overflow: hidden;
}

.rate-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);
  border-radius: 5px;
  transition: width 0.3s;
}

.rate-value {
  font-size: 13px;
  color: #64748b;
  text-align: right;
}

.top-practiced-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-practiced-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 14px;
  transition: all 0.2s;
}

.top-practiced-item:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.top-practiced-rank {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
}

.top-practiced-rank.rank-1 {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.top-practiced-rank.rank-2 {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #4338ca;
}

.top-practiced-rank.rank-3 {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #be185d;
}

.top-practiced-info {
  flex: 1;
  min-width: 0;
}

.top-practiced-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-practiced-count {
  flex-shrink: 0;
  text-align: right;
}

.top-practiced-count .count-num {
  font-size: 22px;
  font-weight: 800;
  color: #8b5cf6;
}

.top-practiced-count .count-label {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 4px;
}

.mt-6 {
  margin-top: 24px;
}

.text-green {
  color: #16a34a;
}

.device-stats-section {
  margin-top: 24px;
}

.difficulty-tags-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.difficulty-tag-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.2s;
}

.difficulty-tag-item:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.difficulty-tag-rank {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
}

.difficulty-tag-rank.rank-1 {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.difficulty-tag-rank.rank-2 {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #4338ca;
}

.difficulty-tag-rank.rank-3 {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #be185d;
}

.difficulty-tag-name {
  flex: 1;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.difficulty-tag-count {
  flex-shrink: 0;
  text-align: right;
}

.difficulty-tag-count .count-num {
  font-size: 20px;
  font-weight: 800;
  color: #f59e0b;
}

.difficulty-tag-count .count-label {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 2px;
}

.system-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.system-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-name {
  width: 120px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  flex-shrink: 0;
}

.system-bar-wrap {
  flex: 1;
  height: 24px;
  background: #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

.system-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  transition: width 0.3s;
  min-width: 4px;
}

.system-count {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 700;
  color: #475569;
  flex-shrink: 0;
}

.brand-duration-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.brand-duration-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-duration-name {
  width: 60px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  flex-shrink: 0;
}

.brand-duration-bar-wrap {
  flex: 1;
  height: 24px;
  background: #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

.brand-duration-bar {
  height: 100%;
  background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
  border-radius: 12px;
  transition: width 0.3s;
  min-width: 4px;
}

.brand-duration-value {
  width: 80px;
  text-align: right;
  font-size: 14px;
  font-weight: 700;
  color: #475569;
  flex-shrink: 0;
}

.family-efficiency-section {
  background: #f8fafc;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.family-table {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.family-table-header {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr 0.8fr 0.8fr 0.9fr 0.9fr 0.8fr 0.8fr 0.8fr 0.8fr;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 13px;
}

.family-table-header > div {
  padding: 14px 12px;
  text-align: center;
}

.family-table-header .col-name {
  text-align: left;
  padding-left: 20px;
}

.family-table-body {
  background: white;
}

.family-table-row {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr 0.8fr 0.8fr 0.9fr 0.9fr 0.8fr 0.8fr 0.8fr 0.8fr;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.2s;
}

.family-table-row:hover {
  background: #f8fafc;
}

.family-table-row:last-child {
  border-bottom: none;
}

.family-table-row > div {
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}

.family-table-row .col-name {
  justify-content: flex-start;
  padding-left: 20px;
  font-weight: 500;
  color: #1e293b;
}

.stat-number {
  font-weight: 600;
  color: #1e293b;
}

.stat-number.text-green {
  color: #10b981;
}

.stat-number.text-orange {
  color: #f59e0b;
}

.stat-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: #dcfce7;
  color: #166534;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-danger {
  background: #fee2e2;
  color: #dc2626;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 12px;
  background: #e2e8f0;
  color: #64748b;
  margin-right: 10px;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  color: white;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #b8860b 100%);
  color: white;
}

.status-online {
  padding: 4px 10px;
  border-radius: 12px;
  background: #dcfce7;
  color: #166534;
  font-size: 12px;
  font-weight: 500;
}

.status-offline {
  padding: 4px 10px;
  border-radius: 12px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
  font-weight: 500;
}

.duty-active {
  padding: 4px 10px;
  border-radius: 12px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 12px;
  font-weight: 500;
}

.duty-inactive {
  padding: 4px 10px;
  border-radius: 12px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  color: #94a3b8;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.risk-stats-section {
  background: #fef2f2;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #fecaca;
}

.stat-red::before { background: linear-gradient(180deg, #ef4444, #dc2626); }

.keyword-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyword-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 12px;
}

.keyword-item:hover {
  background: #fef2f2;
  transform: translateX(4px);
}

.keyword-rank {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
}

.keyword-rank.rank-1 { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); color: #92400e; }
.keyword-rank.rank-2 { background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); color: #4338ca; }
.keyword-rank.rank-3 { background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%); color: #be185d; }

.keyword-name {
  flex: 1;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.keyword-count .count-num {
  font-size: 20px;
  font-weight: 800;
  color: #ef4444;
}

.keyword-count .count-label {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 2px;
}

.leak-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.leak-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #fef2f2;
  border-radius: 12px;
}

.leak-icon {
  font-size: 28px;
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.leak-info {
  flex: 1;
}

.leak-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 2px;
}

.leak-value {
  font-size: 20px;
  font-weight: 800;
}

.text-danger { color: #dc2626 !important; }
.text-warning { color: #f59e0b !important; }
.text-safe { color: #16a34a !important; }

.interception-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.interception-main {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-radius: 16px;
}

.interception-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.interception-rate {
  font-size: 42px;
  font-weight: 800;
  color: #166534;
  line-height: 1;
  margin-bottom: 4px;
}

.interception-label {
  font-size: 14px;
  color: #15803d;
  font-weight: 600;
}

.interception-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.interception-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  border-radius: 6px;
  transition: width 0.3s;
}

.interception-numbers {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #64748b;
  margin-top: 8px;
}
</style>
