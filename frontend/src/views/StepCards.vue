<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { stepcardApi } from '@/api'
import { PROBLEM_TYPES, DEVICE_BRANDS, SYSTEM_VERSIONS, type StepCard, type StepCardStep } from '@/types'

const cards = ref<StepCard[]>([])
const filterType = ref<string>('all')
const showCreateModal = ref(false)

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

const fetchCards = async () => {
  cards.value = await stepcardApi.list()
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
</style>
