<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { stepcardApi } from '@/api'
import { PROBLEM_TYPES, type StepCard } from '@/types'

const cards = ref<StepCard[]>([])
const searchQuery = ref('')
const selectedType = ref<string>('')
const viewingCard = ref<StepCard | null>(null)

const filteredCards = computed(() => {
  let list = cards.value
  if (selectedType.value) {
    list = list.filter((c) => c.problem_type === selectedType.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.description?.toLowerCase().includes(q) ||
        c.steps.some((s) => s.content.toLowerCase().includes(q))
    )
  }
  return list.sort((a, b) => b.usage_count - a.usage_count)
})

const typeIcons: Record<string, string> = {
  '看不清字': '🔍',
  '找不到入口': '🧭',
  '误触广告': '🚫',
  '不会切换网络': '📶',
  '支付设置': '💰',
  '声音太小': '🔊',
  '不会拍照': '📷',
  '其他问题': '❓'
}

const fetchCards = async () => {
  cards.value = await stepcardApi.list()
}

const openCard = async (card: StepCard) => {
  const detail = await stepcardApi.get(card.id)
  viewingCard.value = detail
  stepcardApi.use(card.id)
  card.usage_count++
}

const closeCard = () => {
  viewingCard.value = null
}

const difficultyLabel = (d: string) => {
  return d === 'easy' ? '简单' : d === 'normal' ? '一般' : '较难'
}

onMounted(fetchCards)
</script>

<template>
  <div>
    <div class="card mb-6 library-hero">
      <div class="hero-content">
        <div class="hero-icon">📚</div>
        <div>
          <h2 class="hero-title">高频问题智能库</h2>
          <p class="hero-desc">
            收录了 {{ cards.length }} 张操作步骤卡，遇到同类问题可直接调出历史方案
          </p>
        </div>
      </div>
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          class="search-input"
          placeholder="搜索问题关键词，如：字体、WiFi、相册..."
        />
      </div>
    </div>

    <div class="card mb-6">
      <h3 class="section-title mb-3">常见问题分类</h3>
      <div class="type-grid">
        <button
          :class="['type-card', { active: !selectedType }]"
          @click="selectedType = ''"
        >
          <div class="type-card-icon">📂</div>
          <div class="type-card-name">全部</div>
          <div class="type-card-count">{{ cards.length }} 个方案</div>
        </button>
        <button
          v-for="t in PROBLEM_TYPES"
          :key="t"
          :class="['type-card', { active: selectedType === t }]"
          @click="selectedType = t"
        >
          <div class="type-card-icon">{{ typeIcons[t] || '❓' }}</div>
          <div class="type-card-name">{{ t }}</div>
          <div class="type-card-count">
            {{ cards.filter((c) => c.problem_type === t).length }} 个方案
          </div>
        </button>
      </div>
    </div>

    <h3 class="section-title mb-4">
      {{ selectedType || '全部' }} · 共 {{ filteredCards.length }} 个方案
    </h3>

    <div class="grid grid-2">
      <div
        v-for="card in filteredCards"
        :key="card.id"
        class="card card-hover library-card"
        @click="openCard(card)"
      >
        <div class="library-card-header">
          <div class="library-card-icon">{{ typeIcons[card.problem_type] || '❓' }}</div>
          <div class="library-card-info">
            <h4 class="library-card-title">{{ card.title }}</h4>
            <div class="library-card-tags">
              <span class="tag">{{ card.problem_type }}</span>
              <span v-if="card.device_brand" class="tag">{{ card.device_brand }}</span>
              <span :class="['badge', 'badge-' + card.difficulty]">
                {{ difficultyLabel(card.difficulty) }}
              </span>
            </div>
          </div>
        </div>
        <p class="library-card-desc">{{ card.description || '暂无描述' }}</p>
        <div class="library-card-footer">
          <span>📋 {{ card.steps.length }} 个步骤</span>
          <span>🔥 使用 {{ card.usage_count }} 次</span>
        </div>
      </div>

      <div v-if="filteredCards.length === 0" class="card" style="grid-column: span 2">
        <div class="empty-state">
          <div class="empty-state-icon">🔍</div>
          <div>没有找到匹配的方案</div>
          <p class="text-sm text-muted mt-2">换个关键词试试，或者去「步骤卡整理」新建一张</p>
        </div>
      </div>
    </div>

    <div v-if="viewingCard" class="modal-overlay" @click.self="closeCard">
      <div class="modal-content detail-modal">
        <div class="modal-header">
          <div class="detail-modal-title">
            <span class="detail-icon">{{ typeIcons[viewingCard.problem_type] || '❓' }}</span>
            <div>
              <h3>{{ viewingCard.title }}</h3>
              <div class="detail-sub">
                <span class="tag">{{ viewingCard.problem_type }}</span>
                <span v-if="viewingCard.device_brand" class="tag">{{ viewingCard.device_brand }}</span>
                <span v-if="viewingCard.system_version" class="tag">{{ viewingCard.system_version }}</span>
                <span :class="['badge', 'badge-' + viewingCard.difficulty]">
                  {{ difficultyLabel(viewingCard.difficulty) }}
                </span>
              </div>
            </div>
          </div>
          <button class="modal-close" @click="closeCard">×</button>
        </div>

        <div class="modal-body">
          <div class="detail-desc">
            <h4>场景描述</h4>
            <p>{{ viewingCard.description || '暂无详细描述' }}</p>
          </div>

          <div class="detail-steps">
            <h4>📋 操作步骤（共 {{ viewingCard.steps.length }} 步）</h4>
            <div
              v-for="step in [...viewingCard.steps].sort((a, b) => a.step_number - b.step_number)"
              :key="step.id"
              class="step-item large-step"
            >
              <div class="step-number">{{ step.step_number }}</div>
              <div class="step-content">
                <div class="step-text">{{ step.content }}</div>
                <div v-if="step.tip" class="tip-box">💡 小提示：{{ step.tip }}</div>
              </div>
            </div>
          </div>

          <div class="detail-usage">
            👆 该方案已被使用 <strong>{{ viewingCard.usage_count }}</strong> 次
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-primary btn-lg" @click="closeCard">我明白了，问题已解决</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.library-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero-content {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.hero-icon {
  font-size: 56px;
}

.hero-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.hero-desc {
  opacity: 0.9;
  font-size: 14px;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 14px;
  padding: 4px 16px;
  gap: 10px;
}

.search-icon {
  font-size: 18px;
  color: #94a3b8;
}

.search-input {
  flex: 1;
  padding: 12px;
  border: none;
  outline: none;
  font-size: 15px;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.type-card {
  background: #f8fafc;
  border: 2px solid transparent;
  border-radius: 14px;
  padding: 18px 14px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.type-card:hover {
  background: #eef2ff;
  transform: translateY(-2px);
}

.type-card.active {
  border-color: #667eea;
  background: #eef2ff;
}

.type-card-icon {
  font-size: 32px;
  margin-bottom: 6px;
}

.type-card-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.type-card-count {
  font-size: 12px;
  color: #64748b;
}

.library-card {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.library-card-header {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.library-card-icon {
  font-size: 36px;
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.library-card-info {
  flex: 1;
}

.library-card-title {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1e293b;
}

.library-card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.library-card-desc {
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
}

.library-card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #475569;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
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
  max-width: 640px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.detail-modal {
  max-width: 680px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
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

.detail-modal-title {
  display: flex;
  align-items: center;
  gap: 14px;
}

.detail-icon {
  font-size: 40px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-modal-title h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 6px;
}

.detail-sub {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.detail-desc {
  margin-bottom: 24px;
}

.detail-desc h4,
.detail-steps h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1e293b;
}

.detail-desc p {
  color: #475569;
  line-height: 1.8;
  background: #f8fafc;
  padding: 14px 16px;
  border-radius: 10px;
}

.large-step {
  padding: 18px;
}

.large-step .step-number {
  width: 42px;
  height: 42px;
  font-size: 18px;
}

.large-step .step-text {
  font-size: 16px;
  line-height: 1.7;
}

.detail-usage {
  margin-top: 20px;
  padding: 14px;
  background: #f0fdf4;
  border-radius: 10px;
  color: #166534;
  text-align: center;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
}
</style>
