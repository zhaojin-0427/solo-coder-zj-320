<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { helpApi, stepcardApi } from '@/api'
import type { HelpRequest } from '@/types'
import { useRouter } from 'vue-router'

const router = useRouter()
const helps = ref<HelpRequest[]>([])
const filterStatus = ref<string>('all')
const selectedHelp = ref<HelpRequest | null>(null)
const newStep = ref('')
const newTip = ref('')
const isIndependent = ref(false)

const filteredHelps = computed(() => {
  if (filterStatus.value === 'all') return helps.value
  return helps.value.filter((h) => h.status === filterStatus.value)
})

const pendingCount = computed(() => helps.value.filter((h) => h.status === 'pending').length)

const fetchHelps = async () => {
  helps.value = await helpApi.list()
}

const selectHelp = (h: HelpRequest) => {
  selectedHelp.value = h
}

const addGuidance = async () => {
  if (!selectedHelp.value || !newStep.value.trim()) return
  const stepNum = selectedHelp.value.guidance_records.length + 1
  await helpApi.addGuidance(selectedHelp.value.id, {
    step_number: stepNum,
    content: newStep.value,
    tip: newTip.value || undefined
  })
  newStep.value = ''
  newTip.value = ''
  const updated = await helpApi.get(selectedHelp.value.id)
  selectedHelp.value = updated
  const idx = helps.value.findIndex((h) => h.id === updated.id)
  if (idx !== -1) helps.value[idx] = updated
}

const resolveHelp = async () => {
  if (!selectedHelp.value) return
  await helpApi.resolve(selectedHelp.value.id, {
    is_independent: isIndependent.value
  })
  selectedHelp.value.status = 'resolved'
  await fetchHelps()
  isIndependent.value = false
}

const createStepCard = async () => {
  if (!selectedHelp.value) return
  await stepcardApi.createFromHelp(selectedHelp.value.id, {
    title: selectedHelp.value.title,
    description: selectedHelp.value.description
  })
  alert('步骤卡已创建成功！可在「步骤卡整理」和「高频问题库」中查看')
  router.push('/stepcards')
}

const formatTime = (t?: string) => {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(fetchHelps)
</script>

<template>
  <div class="guidance-layout">
    <div class="guidance-list card">
      <div class="list-header">
        <h3 class="section-title mb-2">求助列表</h3>
        <div class="filter-tabs">
          <button :class="['tab-btn', { active: filterStatus === 'all' }]" @click="filterStatus = 'all'">
            全部 ({{ helps.length }})
          </button>
          <button :class="['tab-btn', { active: filterStatus === 'pending' }]" @click="filterStatus = 'pending'">
            待处理 ({{ pendingCount }})
          </button>
          <button :class="['tab-btn', { active: filterStatus === 'resolved' }]" @click="filterStatus = 'resolved'">
            已解决
          </button>
        </div>
      </div>

      <div class="help-items">
        <div
          v-for="h in filteredHelps"
          :key="h.id"
          class="help-item"
          :class="{ active: selectedHelp?.id === h.id, resolved: h.status === 'resolved' }"
          @click="selectHelp(h)"
        >
          <div class="help-item-header">
            <span :class="['badge', 'badge-' + h.status]">
              {{ h.status === 'pending' ? '待处理' : '已解决' }}
            </span>
            <span v-if="h.is_repeat" class="badge badge-normal">重复问题</span>
          </div>
          <div class="help-title">{{ h.title }}</div>
          <div class="help-meta">
            <span class="tag">{{ h.problem_type }}</span>
            <span v-if="h.device_brand" class="text-sm text-muted">{{ h.device_brand }}</span>
          </div>
          <div class="help-footer">
            <span class="text-sm text-muted">{{ h.requester?.name || '老人' }}</span>
            <span class="text-sm text-muted">{{ formatTime(h.created_at) }}</span>
          </div>
        </div>

        <div v-if="filteredHelps.length === 0" class="empty-state">
          <div class="empty-state-icon">📭</div>
          <div>暂无求助记录</div>
        </div>
      </div>
    </div>

    <div class="guidance-detail card">
      <div v-if="selectedHelp" class="detail-content">
        <div class="detail-header">
          <h3 class="section-title mb-2">{{ selectedHelp.title }}</h3>
          <div class="detail-tags">
            <span class="tag">{{ selectedHelp.problem_type }}</span>
            <span v-if="selectedHelp.device_brand" class="tag">{{ selectedHelp.device_brand }}</span>
            <span v-if="selectedHelp.system_version" class="tag">{{ selectedHelp.system_version }}</span>
            <span :class="['badge', 'badge-' + selectedHelp.status]">
              {{ selectedHelp.status === 'pending' ? '待处理' : '已解决' }}
            </span>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="detail-subtitle">问题描述</h4>
          <p class="detail-description">{{ selectedHelp.description || '暂无详细描述' }}</p>
          <div v-if="selectedHelp.image_url" class="screenshot-preview">
            <img :src="selectedHelp.image_url" alt="问题截图" />
          </div>
        </div>

        <div class="detail-section">
          <h4 class="detail-subtitle">
            分步指导
            <span class="text-sm text-muted">（共 {{ selectedHelp.guidance_records.length }} 步）</span>
          </h4>

          <div v-if="selectedHelp.guidance_records.length === 0" class="empty-state" style="padding: 30px;">
            <div class="empty-state-icon" style="font-size: 40px;">📝</div>
            <div class="text-sm">还没有添加指导步骤，请在下方填写</div>
          </div>

          <div v-else>
            <div
              v-for="g in [...selectedHelp.guidance_records].sort((a, b) => a.step_number - b.step_number)"
              :key="g.id"
              class="step-item"
            >
              <div class="step-number">{{ g.step_number }}</div>
              <div class="step-content">
                <div class="step-text">{{ g.content }}</div>
                <div v-if="g.tip" class="tip-box">💡 小提示：{{ g.tip }}</div>
              </div>
            </div>
          </div>

          <div v-if="selectedHelp.status === 'pending'" class="add-step-form">
            <div class="form-group mb-3">
              <label class="form-label">添加第 {{ selectedHelp.guidance_records.length + 1 }} 步</label>
              <input
                v-model="newStep"
                class="form-input"
                placeholder="例如：点击手机桌面上的「设置」图标"
              />
            </div>
            <div class="form-group mb-3">
              <label class="form-label">小提示（可选）</label>
              <input
                v-model="newTip"
                class="form-input"
                placeholder="例如：图标是一个齿轮的样子"
              />
            </div>
            <button class="btn btn-secondary" @click="addGuidance">添加这一步</button>
          </div>
        </div>

        <div v-if="selectedHelp.status === 'pending'" class="detail-actions">
          <button class="btn btn-primary" :disabled="selectedHelp.guidance_records.length === 0" @click="resolveHelp">
            ✅ 标记为已解决
          </button>
          <label class="independent-check">
            <input type="checkbox" v-model="isIndependent" />
            <span>老人独立完成</span>
          </label>
          <button
            class="btn btn-success"
            :disabled="selectedHelp.guidance_records.length === 0"
            @click="createStepCard"
          >
            📋 保存为步骤卡
          </button>
        </div>

        <div v-else class="resolved-info">
          <div class="resolved-meta">
            <div>
              <span class="text-muted">解决用时：</span>
              <span class="font-bold">{{ selectedHelp.resolution_duration || 0 }} 分钟</span>
            </div>
            <div>
              <span class="text-muted">指导人：</span>
              <span class="font-bold">{{ selectedHelp.helper?.name || '家人' }}</span>
            </div>
            <div>
              <span class="text-muted">独立完成：</span>
              <span class="font-bold">{{ selectedHelp.is_independent ? '是' : '否' }}</span>
            </div>
          </div>
          <button v-if="!selectedHelp.step_card_id" class="btn btn-success" @click="createStepCard">
            📋 将本次指导保存为步骤卡
          </button>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-state-icon">👈</div>
        <div>请从左侧选择一条求助记录查看详情</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.guidance-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 20px;
  min-height: 70vh;
}

@media (max-width: 1024px) {
  .guidance-layout {
    grid-template-columns: 1fr;
  }
}

.list-header {
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 16px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 6px 14px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.help-items {
  max-height: 70vh;
  overflow-y: auto;
}

.help-item {
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  background: #f8fafc;
}

.help-item:hover {
  background: #eef2ff;
}

.help-item.active {
  border-color: #667eea;
  background: #eef2ff;
}

.help-item.resolved {
  opacity: 0.75;
}

.help-item-header {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.help-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
  margin-bottom: 6px;
}

.help-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.help-footer {
  display: flex;
  justify-content: space-between;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-subtitle {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}

.detail-description {
  color: #475569;
  line-height: 1.8;
}

.screenshot-preview img {
  max-width: 100%;
  max-height: 240px;
  border-radius: 12px;
  margin-top: 12px;
  border: 1px solid #e2e8f0;
}

.add-step-form {
  margin-top: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.detail-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.independent-check {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #475569;
  font-size: 14px;
}

.independent-check input {
  width: 18px;
  height: 18px;
}

.resolved-info {
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.resolved-meta {
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
</style>
