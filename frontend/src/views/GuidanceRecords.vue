<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { helpApi, stepcardApi, practiceApi, deviceApi } from '@/api'
import type { HelpRequest, PracticeRecord, StepCardStep, DeviceProfile } from '@/types'
import { useRouter } from 'vue-router'

const router = useRouter()
const helps = ref<HelpRequest[]>([])
const filterStatus = ref<string>('all')
const selectedHelp = ref<HelpRequest | null>(null)
const newStep = ref('')
const newTip = ref('')
const isIndependent = ref(false)

const activeTab = ref<'help' | 'practice'>('help')
const practices = ref<PracticeRecord[]>([])
const selectedPractice = ref<PracticeRecord | null>(null)
const showTipModal = ref(false)
const tipStepNumber = ref(0)
const tipContent = ref('')
const tipStepId = ref(0)

const showDeviceSupplementModal = ref(false)
const supplementProfileId = ref<number | null>(null)
const supplementData = ref({
  device_brand: '',
  system_version: '',
  difficulty_tags: '',
  common_apps: '',
  network_environment: ''
})

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

const fetchPractices = async () => {
  practices.value = await practiceApi.list()
}

const selectPractice = (p: PracticeRecord) => {
  selectedPractice.value = p
}

const openAddTip = (stepNumber: number, stepId: number) => {
  tipStepNumber.value = stepNumber
  tipStepId.value = stepId
  tipContent.value = ''
  showTipModal.value = true
}

const submitTip = async () => {
  if (!selectedPractice.value || !tipStepNumber.value || !tipContent.value.trim()) {
    alert('请填写提示内容')
    return
  }
  try {
    await stepcardApi.addTip(selectedPractice.value.step_card_id, {
      step_number: tipStepNumber.value,
      tip: tipContent.value.trim()
    })
    alert('提示已添加到步骤卡')
    showTipModal.value = false
    if (selectedPractice.value.step_card_id) {
      const updated = await practiceApi.get(selectedPractice.value.id)
      selectedPractice.value = updated
    }
  } catch (e) {
    console.error(e)
    alert('添加提示失败')
  }
}

const practiceStatusLabel = (status: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'in_progress': return '进行中'
    case 'converted': return '已转求助'
    default: return status
  }
}

const stepStatusLabel = (status: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'cannot_understand': return '看不懂'
    case 'cannot_find': return '找不到入口'
    default: return status
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const formatTime = (t?: string) => {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const openDeviceSupplement = (profileId: number | undefined, helpRequest: HelpRequest) => {
  if (!profileId) return
  supplementProfileId.value = profileId
  supplementData.value = {
    device_brand: helpRequest.device_brand || '',
    system_version: helpRequest.system_version || '',
    difficulty_tags: helpRequest.problem_type || '',
    common_apps: '',
    network_environment: ''
  }
  showDeviceSupplementModal.value = true
}

const submitSupplement = async () => {
  if (!supplementProfileId.value) return
  try {
    await deviceApi.supplementProfile(supplementProfileId.value, supplementData.value)
    alert('设备档案已更新')
    showDeviceSupplementModal.value = false
    if (selectedHelp.value) {
      const updated = await helpApi.get(selectedHelp.value.id)
      selectedHelp.value = updated
    }
  } catch (e) {
    console.error(e)
    alert('更新设备档案失败')
  }
}

const fetchAll = () => {
  fetchHelps()
  fetchPractices()
}

onMounted(fetchAll)
</script>

<template>
  <div class="guidance-layout">
    <div class="guidance-list card">
      <div class="list-header">
        <h3 class="section-title mb-3">记录列表</h3>
        <div class="main-tabs">
          <button :class="['main-tab-btn', { active: activeTab === 'help' }]" @click="activeTab = 'help'">
            📞 求助记录 ({{ helps.length }})
          </button>
          <button :class="['main-tab-btn', { active: activeTab === 'practice' }]" @click="activeTab = 'practice'">
            📝 练习记录 ({{ practices.length }})
          </button>
        </div>
      </div>

      <div v-if="activeTab === 'help'" class="list-sub-header">
        <div class="filter-tabs">
          <button :class="['tab-btn', { active: filterStatus === 'all' }]" @click="filterStatus = 'all'">
            全部
          </button>
          <button :class="['tab-btn', { active: filterStatus === 'pending' }]" @click="filterStatus = 'pending'">
            待处理 ({{ pendingCount }})
          </button>
          <button :class="['tab-btn', { active: filterStatus === 'resolved' }]" @click="filterStatus = 'resolved'">
            已解决
          </button>
        </div>
      </div>

      <div v-if="activeTab === 'help'" class="help-items">
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

      <div v-else class="help-items">
        <div
          v-for="p in practices"
          :key="p.id"
          class="help-item practice-item"
          :class="{ active: selectedPractice?.id === p.id }"
          @click="selectPractice(p)"
        >
          <div class="help-item-header">
            <span :class="['badge', 'badge-' + (p.status === 'completed' ? 'resolved' : p.status === 'converted' ? 'pending' : 'normal')]">
              {{ practiceStatusLabel(p.status) }}
            </span>
            <span v-if="p.is_independent" class="badge badge-resolved">独立完成</span>
            <span v-if="p.converted_to_help" class="badge badge-pending">已转求助</span>
          </div>
          <div class="help-title">{{ p.step_card?.title || '练习' }}</div>
          <div class="help-meta">
            <span class="tag">练习</span>
            <span class="text-sm text-muted">{{ p.step_card?.problem_type }}</span>
          </div>
          <div class="help-footer">
            <span class="text-sm text-muted">{{ p.practitioner?.name || '老人' }}</span>
            <span class="text-sm text-muted">{{ formatDate(p.created_at) }}</span>
          </div>
          <div v-if="p.stuck_step_number" class="practice-stuck-info">
            ⚠️ 卡在第 {{ p.stuck_step_number }} 步
          </div>
        </div>

        <div v-if="practices.length === 0" class="empty-state">
          <div class="empty-state-icon">📝</div>
          <div>暂无练习记录</div>
        </div>
      </div>
    </div>

    <div class="guidance-detail card">
      <div v-if="activeTab === 'help' && selectedHelp" class="detail-content">
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

          <div v-if="selectedHelp.device_profile" class="device-profile-section">
            <div class="device-profile-header">
              <h4 class="detail-subtitle">📱 关联设备档案</h4>
              <button class="btn btn-secondary btn-sm" @click="openDeviceSupplement(selectedHelp.device_profile_id, selectedHelp)">
                ✏️ 补充档案
              </button>
            </div>
            <div class="device-profile-grid">
              <div class="device-profile-item">
                <span class="dp-label">设备品牌</span>
                <span class="dp-value">{{ selectedHelp.device_profile.device_brand || '未设置' }}</span>
              </div>
              <div class="device-profile-item">
                <span class="dp-label">系统版本</span>
                <span class="dp-value">{{ selectedHelp.device_profile.system_version || '未设置' }}</span>
              </div>
              <div class="device-profile-item">
                <span class="dp-label">字体偏好</span>
                <span class="dp-value">{{ selectedHelp.device_profile.font_size_preference || '未设置' }}</span>
              </div>
              <div class="device-profile-item">
                <span class="dp-label">简易模式</span>
                <span class="dp-value">{{ selectedHelp.device_profile.simple_mode_enabled ? '已开启' : '未开启' }}</span>
              </div>
              <div class="device-profile-item">
                <span class="dp-label">常用App</span>
                <span class="dp-value">{{ selectedHelp.device_profile.common_apps || '未设置' }}</span>
              </div>
              <div class="device-profile-item">
                <span class="dp-label">网络环境</span>
                <span class="dp-value">{{ selectedHelp.device_profile.network_environment || '未设置' }}</span>
              </div>
            </div>
            <div v-if="selectedHelp.device_profile.difficulty_tags" class="device-profile-tags">
              <span class="dp-label">高频困难：</span>
              <span v-for="tag in selectedHelp.device_profile.difficulty_tags.split(',')" :key="tag" class="tag">{{ tag.trim() }}</span>
            </div>
          </div>
          <div v-else-if="selectedHelp.device_brand" class="device-profile-section">
            <div class="device-profile-header">
              <h4 class="detail-subtitle">📱 设备信息</h4>
            </div>
            <div class="device-profile-grid">
              <div class="device-profile-item">
                <span class="dp-label">设备品牌</span>
                <span class="dp-value">{{ selectedHelp.device_brand }}</span>
              </div>
              <div class="device-profile-item">
                <span class="dp-label">系统版本</span>
                <span class="dp-value">{{ selectedHelp.system_version || '未设置' }}</span>
              </div>
            </div>
          </div>

          <div v-if="selectedHelp.image_url" class="screenshot-preview">
            <img :src="selectedHelp.image_url" alt="问题截图" />
          </div>
          <div v-if="selectedHelp.audio_url" class="audio-preview">
            <div class="audio-info">
              <span class="audio-icon">🎙️</span>
              <span class="audio-label">语音描述</span>
            </div>
            <audio :src="selectedHelp.audio_url" controls class="audio-player"></audio>
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

      <div v-else-if="activeTab === 'practice' && selectedPractice" class="detail-content">
        <div class="detail-header">
          <h3 class="section-title mb-2">{{ selectedPractice.step_card?.title || '练习记录' }}</h3>
          <div class="detail-tags">
            <span class="tag">{{ selectedPractice.step_card?.problem_type || '练习' }}</span>
            <span :class="['badge', 'badge-' + (selectedPractice.status === 'completed' ? 'resolved' : selectedPractice.status === 'converted' ? 'pending' : 'normal')]">
              {{ practiceStatusLabel(selectedPractice.status) }}
            </span>
            <span v-if="selectedPractice.is_independent" class="badge badge-resolved">独立完成</span>
          </div>
        </div>

        <div class="detail-section">
          <div class="practice-meta-grid">
            <div class="practice-meta-item">
              <div class="practice-meta-label">练习人</div>
              <div class="practice-meta-value">{{ selectedPractice.practitioner?.name || '老人' }}</div>
            </div>
            <div class="practice-meta-item">
              <div class="practice-meta-label">来源</div>
              <div class="practice-meta-value">
                {{ selectedPractice.source === 'library' ? '高频问题库' : '求助成功页' }}
              </div>
            </div>
            <div class="practice-meta-item">
              <div class="practice-meta-label">练习时间</div>
              <div class="practice-meta-value">{{ formatDate(selectedPractice.created_at) }}</div>
            </div>
            <div class="practice-meta-item">
              <div class="practice-meta-label">卡住步骤</div>
              <div class="practice-meta-value text-orange">
                {{ selectedPractice.stuck_step_number ? '第 ' + selectedPractice.stuck_step_number + ' 步' : '无' }}
              </div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="detail-subtitle">
            📋 各步骤完成情况
            <span class="text-sm text-muted">（共 {{ selectedPractice.step_feedbacks.length }} 个步骤有反馈）</span>
          </h4>

          <div v-if="selectedPractice.step_feedbacks.length === 0" class="empty-state" style="padding: 30px;">
            <div class="empty-state-icon" style="font-size: 40px;">📝</div>
            <div class="text-sm">该练习暂无步骤反馈</div>
          </div>

          <div v-else class="practice-steps-detail">
            <div
              v-for="fb in [...selectedPractice.step_feedbacks].sort((a, b) => a.step_number - b.step_number)"
              :key="fb.id"
              :class="['practice-step-detail', {
                'step-completed': fb.status === 'completed',
                'step-stuck': fb.status !== 'completed'
              }]"
            >
              <div class="practice-step-detail-header">
                <div class="step-number">{{ fb.step_number }}</div>
                <div class="step-content">
                  <div class="step-text">{{ fb.step_content }}</div>
                  <div :class="['step-status-badge', 'status-' + fb.status]">
                    {{ stepStatusLabel(fb.status) }}
                  </div>
                </div>
              </div>
              <div v-if="fb.feedback" class="step-feedback-text">
                💬 老人反馈：{{ fb.feedback }}
              </div>
              <div v-if="fb.status !== 'completed'" class="step-tip-action">
                <button class="btn btn-secondary btn-sm" @click="openAddTip(fb.step_number, fb.step_card_step_id)">
                  💡 补充为步骤提示
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedPractice.feedback" class="detail-section">
          <h4 class="detail-subtitle">📝 总体反馈</h4>
          <div class="feedback-box">
            {{ selectedPractice.feedback }}
          </div>
        </div>

        <div v-if="selectedPractice.converted_to_help && selectedPractice.help_request_id" class="detail-section">
          <div class="converted-info">
            <span>📞 已转为求助</span>
            <button class="btn btn-link" @click="activeTab = 'help'">查看求助记录 →</button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-state-icon">👈</div>
        <div>请从左侧选择一条记录查看详情</div>
      </div>
    </div>

    <div v-if="showTipModal" class="modal-overlay" @click.self="showTipModal = false">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h3>💡 补充步骤提示</h3>
          <button class="modal-close" @click="showTipModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">第 {{ tipStepNumber }} 步 - 补充提示内容</label>
            <textarea
              v-model="tipContent"
              class="form-textarea"
              rows="4"
              placeholder="例如：这个按钮一般在屏幕右上角，是一个齿轮形状的图标..."
            ></textarea>
          </div>
          <p class="text-sm text-muted mt-3">
            这条提示会被添加到对应的步骤卡中，帮助老人下次更容易理解。
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showTipModal = false">取消</button>
          <button class="btn btn-primary" @click="submitTip">确认添加</button>
        </div>
      </div>
    </div>

    <div v-if="showDeviceSupplementModal" class="modal-overlay" @click.self="showDeviceSupplementModal = false">
      <div class="modal-content" style="max-width: 560px;">
        <div class="modal-header">
          <h3>📱 补充设备档案</h3>
          <button class="modal-close" @click="showDeviceSupplementModal = false">×</button>
        </div>
        <div class="modal-body">
          <p class="text-sm text-muted mb-4">
            将本次指导中发现的设备差异补充回设备档案，帮助下次更精准匹配步骤卡。
          </p>
          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">设备品牌</label>
              <input v-model="supplementData.device_brand" class="form-input" placeholder="例如：华为" />
            </div>
            <div class="form-group">
              <label class="form-label">系统版本</label>
              <input v-model="supplementData.system_version" class="form-input" placeholder="例如：HarmonyOS 4" />
            </div>
            <div class="form-group">
              <label class="form-label">新增困难标签（逗号分隔）</label>
              <input v-model="supplementData.difficulty_tags" class="form-input" placeholder="例如：找不到入口,看不清字" />
            </div>
            <div class="form-group">
              <label class="form-label">新增常用App（逗号分隔）</label>
              <input v-model="supplementData.common_apps" class="form-input" placeholder="例如：微信,抖音" />
            </div>
            <div class="form-group" style="grid-column: span 2">
              <label class="form-label">网络环境</label>
              <input v-model="supplementData.network_environment" class="form-input" placeholder="例如：WiFi" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDeviceSupplementModal = false">取消</button>
          <button class="btn btn-primary" @click="submitSupplement">确认补充</button>
        </div>
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

.audio-preview {
  margin-top: 16px;
  padding: 16px;
  background: #f0fdf4;
  border-radius: 12px;
  border-left: 4px solid #10b981;
}

.audio-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.audio-icon {
  font-size: 20px;
}

.audio-label {
  font-weight: 600;
  color: #065f46;
}

.audio-player {
  width: 100%;
  max-width: 360px;
}

.main-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.main-tab-btn {
  flex: 1;
  min-width: 120px;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #475569;
}

.main-tab-btn:hover {
  background: #f8fafc;
}

.main-tab-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.list-sub-header {
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.practice-item {
  border-left: 4px solid #f59e0b;
}

.practice-stuck-info {
  margin-top: 8px;
  padding: 6px 10px;
  background: #fef2f2;
  color: #dc2626;
  border-radius: 8px;
  font-size: 13px;
}

.practice-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.practice-meta-item {
  padding: 14px;
  background: #f8fafc;
  border-radius: 12px;
}

.practice-meta-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.practice-meta-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.practice-steps-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.practice-step-detail {
  padding: 16px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  background: #f8fafc;
}

.practice-step-detail.step-completed {
  background: #f0fdf4;
  border-color: #86efac;
}

.practice-step-detail.step-stuck {
  background: #fef2f2;
  border-color: #fca5a5;
}

.practice-step-detail-header {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-status-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.step-status-badge.status-completed {
  background: #dcfce7;
  color: #166534;
}

.step-status-badge.status-cannot_understand,
.step-status-badge.status-cannot_find {
  background: #fee2e2;
  color: #dc2626;
}

.step-feedback-text {
  margin-top: 10px;
  margin-left: 48px;
  padding: 10px 12px;
  background: #fef9c3;
  border-radius: 8px;
  font-size: 14px;
  color: #854d0e;
}

.step-tip-action {
  margin-top: 10px;
  margin-left: 48px;
}

.feedback-box {
  padding: 16px;
  background: #fef9c3;
  border-radius: 12px;
  color: #854d0e;
  line-height: 1.6;
}

.converted-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #fef3c7;
  border-radius: 12px;
  font-weight: 600;
  color: #92400e;
}

.btn-link {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
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
  max-width: 480px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
}

.modal-close {
  background: #f1f5f9;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.text-orange {
  color: #ea580c;
}

.device-profile-section {
  margin-top: 16px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 12px;
  border: 1px solid #bae6fd;
}

.device-profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.device-profile-header .detail-subtitle {
  margin-bottom: 0;
}

.device-profile-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.device-profile-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
}

.dp-label {
  font-size: 12px;
  color: #64748b;
}

.dp-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.device-profile-tags {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
