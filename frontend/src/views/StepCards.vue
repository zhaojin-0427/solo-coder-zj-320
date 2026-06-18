<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { stepcardApi } from '@/api'
import { PROBLEM_TYPES, DEVICE_BRANDS, SYSTEM_VERSIONS, type StepCard, type StepCardStep, type CardPracticeStats, type StepCardDeviceTip } from '@/types'

const cards = ref<StepCard[]>([])
const filterType = ref<string>('all')
const showCreateModal = ref(false)
const cardStatsMap = ref<Map<number, CardPracticeStats>>(new Map())

const showDeviceTipModal = ref(false)
const selectedCardForTips = ref<StepCard | null>(null)
const newDeviceTip = ref({
  step_number: 1,
  device_brand: '',
  system_version: '',
  adaptation_tip: '',
  entry_name: ''
})

const newCard = ref({
  title: '',
  problem_type: '',
  difficulty: 'normal' as 'easy' | 'normal' | 'hard',
  device_brand: '',
  system_version: '',
  description: '',
  steps: [
    { step_number: 1, content: '', tip: '' }
  ] as Partial<StepCardStep>[]
})

const filteredCards = computed(() => {
  if (filterType.value === 'all') return cards.value
  return cards.value.filter((c) => c.problem_type === filterType.value)
})

const typeStats = computed(() => {
  const stats: Record<string, number> = { all: cards.value.length }
  cards.value.forEach((c) => {
    stats[c.problem_type] = (stats[c.problem_type] || 0) + 1
  })
  return stats
})

const fetchCardStats = async (cardId: number) => {
  try {
    const stats = await stepcardApi.getPracticeStats(cardId)
    cardStatsMap.value.set(cardId, stats)
  } catch (e) {
    console.error('Failed to fetch card stats:', e)
  }
}

const fetchCards = async () => {
  cards.value = await stepcardApi.list()
  cards.value.forEach((card) => {
    fetchCardStats(card.id)
  })
}

const getCardStats = (cardId: number): CardPracticeStats | null => {
  return cardStatsMap.value.get(cardId) || null
}

const addStep = () => {
  newCard.value.steps.push({
    step_number: newCard.value.steps.length + 1,
    content: '',
    tip: ''
  })
}

const removeStep = (idx: number) => {
  newCard.value.steps.splice(idx, 1)
  newCard.value.steps.forEach((s, i) => (s.step_number = i + 1))
}

const resetNewCard = () => {
  newCard.value = {
    title: '',
    problem_type: '',
    difficulty: 'normal',
    device_brand: '',
    system_version: '',
    description: '',
    steps: [{ step_number: 1, content: '', tip: '' }]
  }
}

const submitCard = async () => {
  if (!newCard.value.title || !newCard.value.problem_type) {
    alert('请填写标题并选择问题类型')
    return
  }
  const validSteps = newCard.value.steps.filter((s) => s.content?.trim())
  if (validSteps.length === 0) {
    alert('请至少填写一个操作步骤')
    return
  }
  try {
    await stepcardApi.create({
      ...newCard.value,
      steps: validSteps
    })
    showCreateModal.value = false
    resetNewCard()
    await fetchCards()
  } catch (e) {
    console.error(e)
  }
}

const openDeviceTipModal = (card: StepCard) => {
  selectedCardForTips.value = card
  newDeviceTip.value = {
    step_number: 1,
    device_brand: '',
    system_version: '',
    adaptation_tip: '',
    entry_name: ''
  }
  showDeviceTipModal.value = true
}

const submitDeviceTip = async () => {
  if (!selectedCardForTips.value) return
  if (!newDeviceTip.value.device_brand || !newDeviceTip.value.adaptation_tip) {
    alert('请填写设备品牌和适配提示')
    return
  }
  try {
    await stepcardApi.addDeviceTip(selectedCardForTips.value.id, newDeviceTip.value)
    showDeviceTipModal.value = false
    await fetchCards()
  } catch (e) {
    console.error(e)
    alert('添加适配提示失败')
  }
}

const deleteDeviceTip = async (cardId: number, tipId: number) => {
  try {
    await stepcardApi.deleteDeviceTip(cardId, tipId)
    await fetchCards()
  } catch (e) {
    console.error(e)
    alert('删除适配提示失败')
  }
}

const getDeviceTipsGrouped = (card: StepCard): Map<string, StepCardDeviceTip[]> => {
  const grouped = new Map<string, StepCardDeviceTip[]>()
  if (!card.device_tips) return grouped
  for (const tip of card.device_tips) {
    const key = tip.device_brand
    const existing = grouped.get(key) || []
    existing.push(tip)
    grouped.set(key, existing)
  }
  return grouped
}

const difficultyLabel = (d: string) => {
  return d === 'easy' ? '简单' : d === 'normal' ? '一般' : '较难'
}

onMounted(fetchCards)
</script>

<template>
  <div>
    <div class="card mb-6">
      <div class="flex justify-between items-center mb-4">
        <div>
          <h3 class="section-title mb-1">步骤卡分类</h3>
          <p class="text-muted text-sm">共 {{ cards.length }} 张操作步骤卡</p>
        </div>
        <button class="btn btn-primary" @click="showCreateModal = true">
          ➕ 新建步骤卡
        </button>
      </div>
      <div class="type-filters">
        <button
          :class="['filter-chip', { active: filterType === 'all' }]"
          @click="filterType = 'all'"
        >
          全部 <span class="chip-count">{{ typeStats.all || 0 }}</span>
        </button>
        <button
          v-for="t in PROBLEM_TYPES"
          :key="t"
          :class="['filter-chip', { active: filterType === t }]"
          @click="filterType = t"
        >
          {{ t }}
          <span class="chip-count" v-if="typeStats[t]">{{ typeStats[t] }}</span>
        </button>
      </div>
    </div>

    <div class="grid grid-3">
      <div v-for="card in filteredCards" :key="card.id" class="card card-hover stepcard-card">
        <div class="stepcard-header">
          <h4 class="stepcard-title">{{ card.title }}</h4>
          <span :class="['badge', 'badge-' + card.difficulty]">{{ difficultyLabel(card.difficulty) }}</span>
        </div>
        <div class="stepcard-meta">
          <span class="tag">{{ card.problem_type }}</span>
          <span v-if="card.device_brand" class="text-sm text-muted">{{ card.device_brand }}</span>
        </div>
        <p class="stepcard-desc">{{ card.description || '暂无描述' }}</p>
        <div class="stepcard-footer">
          <div class="stepcard-steps-count">📋 {{ card.steps.length }} 个操作步骤</div>
          <div class="stepcard-usage">👆 使用 {{ card.usage_count }} 次</div>
        </div>
        <div class="stepcard-preview">
          <div
            v-for="(step, idx) in card.steps.slice(0, 3)"
            :key="step.id"
            class="preview-step"
          >
            <span class="preview-num">{{ step.step_number }}</span>
            <span class="preview-content">{{ step.content }}</span>
          </div>
          <div v-if="card.steps.length > 3" class="preview-more">
            还有 {{ card.steps.length - 3 }} 个步骤...
          </div>
          <div v-if="card.steps.length === 0" class="text-sm text-muted">暂无步骤</div>
        </div>

        <div class="practice-stats-row" v-if="getCardStats(card.id)">
          <div class="practice-stat-item">
            <span class="practice-stat-label">练习次数</span>
            <span class="practice-stat-value">{{ getCardStats(card.id)?.recent_practice_count || 0 }}</span>
          </div>
          <div class="practice-stat-item" v-if="getCardStats(card.id)?.most_stuck_step">
            <span class="practice-stat-label">卡住最多</span>
            <span class="practice-stat-value text-orange">
              第 {{ getCardStats(card.id)?.most_stuck_step?.step_number }} 步
            </span>
          </div>
          <div class="practice-stat-item" v-if="getCardStats(card.id)?.needs_optimization">
            <span class="practice-stat-label">状态</span>
            <span class="practice-stat-badge badge-warning">需优化</span>
          </div>
          <div class="practice-stat-item" v-else-if="getCardStats(card.id)?.total_practice_count > 0">
            <span class="practice-stat-label">完成率</span>
            <span class="practice-stat-value text-green">
              {{ getCardStats(card.id)?.completion_rate_percent }}%
            </span>
          </div>
        </div>

        <div v-if="card.device_tips && card.device_tips.length > 0" class="device-tips-section">
          <div class="device-tips-header">
            <span class="device-tips-title">📱 多设备适配说明</span>
            <button class="btn btn-secondary btn-sm" @click="openDeviceTipModal(card)">+ 添加</button>
          </div>
          <div v-for="[brand, tips] in getDeviceTipsGrouped(card)" :key="brand" class="device-tip-brand-group">
            <div class="device-tip-brand-label">{{ brand }}</div>
            <div v-for="tip in tips" :key="tip.id" class="device-tip-item">
              <span class="device-tip-step">第{{ tip.step_number }}步：</span>
              <span class="device-tip-text">{{ tip.adaptation_tip }}</span>
              <span v-if="tip.entry_name" class="device-tip-entry">入口：{{ tip.entry_name }}</span>
              <button class="device-tip-delete" @click="deleteDeviceTip(card.id, tip.id)">×</button>
            </div>
          </div>
        </div>

        <div v-else class="device-tips-add">
          <button class="btn btn-secondary btn-sm" @click="openDeviceTipModal(card)">📱 添加多设备适配说明</button>
        </div>
      </div>

      <div v-if="filteredCards.length === 0" class="card empty-col">
        <div class="empty-state">
          <div class="empty-state-icon">📋</div>
          <div>该分类下暂无步骤卡</div>
          <button class="btn btn-primary mt-4" @click="showCreateModal = true">
            创建第一张步骤卡
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📋 新建操作步骤卡</h3>
          <button class="modal-close" @click="showCreateModal = false">×</button>
        </div>

        <div class="modal-body">
          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">步骤卡标题 *</label>
              <input v-model="newCard.title" class="form-input" placeholder="例如：调大手机字体" />
            </div>
            <div class="form-group">
              <label class="form-label">问题类型 *</label>
              <select v-model="newCard.problem_type" class="form-select">
                <option value="">请选择类型</option>
                <option v-for="t in PROBLEM_TYPES" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">难度等级</label>
              <select v-model="newCard.difficulty" class="form-select">
                <option value="easy">简单</option>
                <option value="normal">一般</option>
                <option value="hard">较难</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">适用设备品牌</label>
              <select v-model="newCard.device_brand" class="form-select">
                <option value="">通用</option>
                <option v-for="b in DEVICE_BRANDS" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div class="form-group" style="grid-column: span 2">
              <label class="form-label">适用系统版本</label>
              <select v-model="newCard.system_version" class="form-select">
                <option value="">通用</option>
                <option v-for="s in SYSTEM_VERSIONS" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group" style="grid-column: span 2">
              <label class="form-label">场景描述</label>
              <textarea
                v-model="newCard.description"
                class="form-textarea"
                placeholder="描述在什么情况下需要使用这个步骤卡"
              ></textarea>
            </div>
          </div>

          <div class="form-group">
            <div class="flex justify-between items-center mb-2">
              <label class="form-label mb-0">操作步骤</label>
              <button class="btn btn-secondary" @click="addStep">+ 添加步骤</button>
            </div>

            <div
              v-for="(step, idx) in newCard.steps"
              :key="idx"
              class="step-editor"
            >
              <div class="step-editor-num">{{ step.step_number }}</div>
              <div class="step-editor-fields">
                <input
                  v-model="step.content"
                  class="form-input"
                  placeholder="步骤描述，例如：点击桌面上的「设置」图标"
                />
                <input
                  v-model="step.tip"
                  class="form-input mt-2"
                  placeholder="小提示（可选），例如：图标是齿轮的样子"
                />
              </div>
              <button
                v-if="newCard.steps.length > 1"
                class="step-editor-remove"
                @click="removeStep(idx)"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" @click="submitCard">保存步骤卡</button>
        </div>
      </div>
    </div>

    <div v-if="showDeviceTipModal" class="modal-overlay" @click.self="showDeviceTipModal = false">
      <div class="modal-content" style="max-width: 560px;">
        <div class="modal-header">
          <h3>📱 添加设备适配说明</h3>
          <button class="modal-close" @click="showDeviceTipModal = false">×</button>
        </div>
        <div class="modal-body">
          <p class="text-sm text-muted mb-4">
            为步骤卡「{{ selectedCardForTips?.title }}」添加不同品牌/系统的操作差异说明。
          </p>
          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">步骤编号 *</label>
              <input v-model.number="newDeviceTip.step_number" class="form-input" type="number" min="1" />
            </div>
            <div class="form-group">
              <label class="form-label">设备品牌 *</label>
              <select v-model="newDeviceTip.device_brand" class="form-select">
                <option value="">请选择</option>
                <option v-for="b in DEVICE_BRANDS" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">系统版本</label>
              <select v-model="newDeviceTip.system_version" class="form-select">
                <option value="">通用</option>
                <option v-for="s in SYSTEM_VERSIONS" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">入口名称</label>
              <input v-model="newDeviceTip.entry_name" class="form-input" placeholder="例如：设置、图库" />
            </div>
            <div class="form-group" style="grid-column: span 2">
              <label class="form-label">适配说明 *</label>
              <textarea
                v-model="newDeviceTip.adaptation_tip"
                class="form-textarea"
                rows="3"
                placeholder="描述该设备上的操作差异，例如：华为手机叫「图库」而不是「相册」..."
              ></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeviceTipModal = false">取消</button>
          <button class="btn btn-primary" @click="submitDeviceTip">添加适配说明</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.type-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  background: #f1f5f9;
  border: 2px solid transparent;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.filter-chip:hover {
  background: #e2e8f0;
}

.filter-chip.active {
  background: #667eea;
  color: white;
}

.chip-count {
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.filter-chip.active .chip-count {
  background: rgba(255, 255, 255, 0.25);
}

.stepcard-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stepcard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.stepcard-title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
}

.stepcard-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stepcard-desc {
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
}

.stepcard-footer {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #475569;
  padding: 10px 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
}

.stepcard-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-step {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  font-size: 13px;
  color: #475569;
}

.preview-num {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.preview-content {
  line-height: 1.5;
  flex: 1;
}

.preview-more {
  font-size: 12px;
  color: #94a3b8;
  padding-left: 32px;
}

.empty-col {
  grid-column: span 3;
}

@media (max-width: 768px) {
  .empty-col {
    grid-column: span 1;
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 700;
}

.modal-close {
  background: #f1f5f9;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.step-editor {
  display: flex;
  gap: 12px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 10px;
}

.step-editor-num {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.step-editor-fields {
  flex: 1;
}

.step-editor-remove {
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  align-self: flex-start;
}

.practice-stats-row {
  display: flex;
  gap: 12px;
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

.practice-stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.practice-stat-label {
  font-size: 11px;
  color: #94a3b8;
}

.practice-stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

.practice-stat-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.badge-warning {
  background: #fef3c7;
  color: #b45309;
}

.text-green {
  color: #16a34a;
}

.text-orange {
  color: #ea580c;
}

.device-tips-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0f2fe;
}

.device-tips-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.device-tips-title {
  font-size: 14px;
  font-weight: 600;
  color: #0369a1;
}

.device-tip-brand-group {
  margin-bottom: 8px;
}

.device-tip-brand-label {
  font-size: 13px;
  font-weight: 700;
  color: #0284c7;
  margin-bottom: 4px;
  padding-left: 4px;
}

.device-tip-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 6px 10px;
  background: #f0f9ff;
  border-radius: 8px;
  margin-bottom: 4px;
  font-size: 13px;
  color: #334155;
  line-height: 1.5;
}

.device-tip-step {
  font-weight: 600;
  color: #0c4a6e;
  flex-shrink: 0;
}

.device-tip-text {
  flex: 1;
}

.device-tip-entry {
  background: #bae6fd;
  padding: 1px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #0c4a6e;
  flex-shrink: 0;
}

.device-tip-delete {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  flex-shrink: 0;
  line-height: 1;
}

.device-tip-delete:hover {
  color: #dc2626;
}

.device-tips-add {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}
</style>
