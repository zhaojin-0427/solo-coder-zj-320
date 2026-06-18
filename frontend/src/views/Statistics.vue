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
import type { StatsOverview, HelpRequest } from '@/types'

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

const fetchData = async () => {
  overview.value = await statsApi.overview()
  recentHelps.value = (await helpApi.list()).slice(0, 6)
  timeline.value = await statsApi.timeline()
  practiceStats.value = await statsApi.practice()
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
</style>
