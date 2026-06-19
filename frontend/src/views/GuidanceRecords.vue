<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { helpApi, stepcardApi, practiceApi, deviceApi, familyApi, riskApi } from '@/api'
import type { HelpRequest, PracticeRecord, StepCardStep, DeviceProfile, User, HelpStatusLog } from '@/types'
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

const familyMembers = ref<User[]>([])
const showTransferModal = ref(false)
const transferToId = ref<number>(0)
const transferReason = ref('')
const showNoteModal = ref(false)
const noteContent = ref('')
const showAssignModal = ref(false)
const assignToId = ref<number>(0)
const assignReason = ref('')
const recommendCandidates = ref<any[]>([])

const showRiskDisposalModal = ref(false)
const riskDisposalType = ref('')
const riskDisposalNote = ref('')
const shouldCreateStepCard = ref(true)

const currentUserId = 2

const processingStatusOptions = [
  { value: 'phone_guidance', label: '📞 电话指导中', color: '#667eea' },
  { value: 'waiting_operation', label: '⏳ 等待老人操作', color: '#f59e0b' },
  { value: 'need_confirm', label: '❓ 需二次确认', color: '#ef4444' },
  { value: 'resolved', label: '✅ 已解决', color: '#10b981' }
]

const getProcessingStatusInfo = (status?: string) => {
  return processingStatusOptions.find(o => o.value === status) || { label: '未知状态', color: '#94a3b8' }
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'pending': '待分派',
    'assigned': '已分派',
    'processing': '处理中',
    'resolved': '已解决'
  }
  return map[status] || status
}

const filteredHelps = computed(() => {
  if (filterStatus.value === 'all') return helps.value
  return helps.value.filter((h) => h.status === filterStatus.value)
})

const pendingCount = computed(() => helps.value.filter((h) => h.status === 'pending').length)
const assignedCount = computed(() => helps.value.filter((h) => h.status === 'assigned').length)
const processingCount = computed(() => helps.value.filter((h) => h.status === 'processing').length)

const fetchHelps = async () => {
  helps.value = await helpApi.list()
  for (const h of helps.value) {
    if (h.status === 'assigned' || h.status === 'processing') {
      helpApi.checkTimeout(h.id)
    }
  }
}

const fetchFamilyMembers = async () => {
  familyMembers.value = await familyApi.listMembers()
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
  fetchFamilyMembers()
}

const autoAssign = async (helpId: number) => {
  try {
    const result = await helpApi.autoAssign(helpId)
    alert(`已自动分派给 ${result.assigned_to.name}，匹配度 ${result.match_score} 分`)
    await fetchHelps()
    if (selectedHelp.value?.id === helpId) {
      selectedHelp.value = result.help_request
    }
  } catch (e: any) {
    alert(e.response?.data?.error || '分派失败')
  }
}

const openManualAssign = async () => {
  if (!selectedHelp.value) return
  try {
    recommendCandidates.value = await familyApi.recommendForHelp(selectedHelp.value.id)
  } catch (e) {
    console.error(e)
  }
  assignToId.value = 0
  assignReason.value = ''
  showAssignModal.value = true
}

const manualAssign = async () => {
  if (!selectedHelp.value || !assignToId.value) {
    alert('请选择分派对象')
    return
  }
  try {
    const result = await helpApi.manualAssign(selectedHelp.value.id, {
      to_helper_id: assignToId.value,
      reason: assignReason.value
    })
    alert('分派成功')
    showAssignModal.value = false
    await fetchHelps()
    selectedHelp.value = result
  } catch (e: any) {
    alert(e.response?.data?.error || '分派失败')
  }
}

const claimHelp = async () => {
  if (!selectedHelp.value) return
  try {
    const result = await helpApi.claim(selectedHelp.value.id, { helper_id: currentUserId })
    alert('领取成功，开始处理')
    await fetchHelps()
    selectedHelp.value = result
  } catch (e: any) {
    alert(e.response?.data?.error || '领取失败')
  }
}

const openTransfer = () => {
  if (!selectedHelp.value) return
  transferToId.value = 0
  transferReason.value = ''
  showTransferModal.value = true
}

const transferHelp = async () => {
  if (!selectedHelp.value || !transferToId.value) {
    alert('请选择转派对象')
    return
  }
  try {
    const result = await helpApi.transfer(selectedHelp.value.id, {
      to_helper_id: transferToId.value,
      from_helper_id: currentUserId,
      reason: transferReason.value
    })
    alert('转派成功')
    showTransferModal.value = false
    await fetchHelps()
    selectedHelp.value = result
  } catch (e: any) {
    alert(e.response?.data?.error || '转派失败')
  }
}

const updateProcessingStatus = async (status: string) => {
  if (!selectedHelp.value) return
  try {
    const result = await helpApi.updateProcessing(selectedHelp.value.id, {
      processing_status: status
    })
    alert('状态已更新')
    await fetchHelps()
    selectedHelp.value = result
  } catch (e: any) {
    alert(e.response?.data?.error || '更新失败')
  }
}

const openNoteModal = () => {
  noteContent.value = ''
  showNoteModal.value = true
}

const submitNote = async () => {
  if (!selectedHelp.value || !noteContent.value.trim()) {
    alert('请填写备注内容')
    return
  }
  try {
    const result = await helpApi.addNote(selectedHelp.value.id, {
      note: noteContent.value.trim(),
      operator_id: currentUserId
    })
    alert('备注已添加')
    showNoteModal.value = false
    selectedHelp.value = result
  } catch (e: any) {
    alert(e.response?.data?.error || '添加备注失败')
  }
}

const openRiskDisposal = () => {
  if (!selectedHelp.value) return
  riskDisposalType.value = ''
  riskDisposalNote.value = ''
  shouldCreateStepCard.value = true
  showRiskDisposalModal.value = true
}

const submitRiskDisposal = async () => {
  if (!selectedHelp.value || !riskDisposalType.value) {
    alert('请选择处置类型')
    return
  }
  try {
    const result = await riskApi.addDisposal(selectedHelp.value.id, {
      disposal_type: riskDisposalType.value,
      note: riskDisposalNote.value,
      operator_id: currentUserId,
      create_step_card: shouldCreateStepCard.value
    })
    alert('风险处置已记录')
    showRiskDisposalModal.value = false
    await fetchHelps()
    selectedHelp.value = result
  } catch (e: any) {
    alert(e.response?.data?.error || '处置失败')
  }
}

const canClaim = computed(() => {
  if (!selectedHelp.value) return false
  return selectedHelp.value.status === 'pending' ||
    (selectedHelp.value.status === 'assigned' && selectedHelp.value.helper_id !== currentUserId)
})

const isMyTask = computed(() => {
  if (!selectedHelp.value) return false
  return selectedHelp.value.helper_id === currentUserId
})

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
            待分派 ({{ pendingCount }})
          </button>
          <button :class="['tab-btn', { active: filterStatus === 'assigned' }]" @click="filterStatus = 'assigned'">
            已分派 ({{ assignedCount }})
          </button>
          <button :class="['tab-btn', { active: filterStatus === 'processing' }]" @click="filterStatus = 'processing'">
            处理中 ({{ processingCount }})
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
          :class="{ active: selectedHelp?.id === h.id, resolved: h.status === 'resolved', timeout: h.is_timeout }"
          @click="selectHelp(h)"
        >
          <div class="help-item-header">
            <span :class="['badge', 'badge-' + h.status]">
              {{ getStatusLabel(h.status) }}
            </span>
            <span v-if="h.processing_status && h.status === 'processing'" 
                  :style="{ background: getProcessingStatusInfo(h.processing_status).color + '20', color: getProcessingStatusInfo(h.processing_status).color }"
                  class="badge">
              {{ getProcessingStatusInfo(h.processing_status).label }}
            </span>
            <span v-if="h.is_repeat" class="badge badge-normal">重复问题</span>
            <span v-if="h.is_timeout" class="badge badge-danger">⚠️ 超时</span>
            <span v-if="h.is_risk" class="badge badge-risk">🛡️ {{ h.risk_level === 'high' ? '高风险' : '风险' }}</span>
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
          <div v-if="h.helper" class="help-helper">
            <span class="text-sm">👤 {{ h.helper.name }}</span>
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
              {{ getStatusLabel(selectedHelp.status) }}
            </span>
            <span v-if="selectedHelp.is_timeout" class="badge badge-danger">⚠️ 响应超时</span>
            <span v-if="selectedHelp.is_risk" class="badge badge-risk">🛡️ {{ selectedHelp.risk_level === 'high' ? '高风险' : '中风险' }}</span>
          </div>
        </div>

        <div v-if="selectedHelp.status !== 'resolved'" class="action-toolbar">
          <button v-if="selectedHelp.status === 'pending'" class="btn btn-primary btn-sm" @click="autoAssign(selectedHelp.id)">
            🤖 智能分派
          </button>
          <button v-if="selectedHelp.status === 'pending'" class="btn btn-secondary btn-sm" @click="openManualAssign">
            👋 手动分派
          </button>
          <button v-if="canClaim" class="btn btn-success btn-sm" @click="claimHelp">
            ✋ 我来处理
          </button>
          <button v-if="isMyTask && selectedHelp.status === 'processing'" class="btn btn-warning btn-sm" @click="openTransfer">
            🔄 转派他人
          </button>
          <button v-if="isMyTask && selectedHelp.status === 'processing'" class="btn btn-info btn-sm" @click="openNoteModal">
            📝 添加备注
          </button>
          <button v-if="selectedHelp.is_risk && isMyTask" class="btn btn-danger btn-sm" @click="openRiskDisposal">
            🛡️ 风险处置
          </button>
        </div>

        <div v-if="isMyTask && selectedHelp.status === 'processing'" class="processing-status-bar">
          <span class="status-label">当前状态：</span>
          <div class="status-buttons">
            <button
              v-for="opt in processingStatusOptions"
              :key="opt.value"
              :class="['status-btn', { active: selectedHelp.processing_status === opt.value }]"
              :style="selectedHelp.processing_status === opt.value ? { background: opt.color, color: 'white' } : {}"
              @click="updateProcessingStatus(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div v-if="selectedHelp.helper" class="helper-info-section">
          <div class="helper-info-card">
            <div class="helper-avatar">👤</div>
            <div class="helper-info">
              <div class="helper-name">{{ selectedHelp.helper.name }}</div>
              <div class="helper-meta">
                <span v-if="selectedHelp.helper.is_online" class="online-dot"></span>
                <span v-if="selectedHelp.helper.is_online">在线</span>
                <span v-else>离线</span>
                <span v-if="selectedHelp.helper.is_on_duty" class="badge badge-success ml-2">值班中</span>
              </div>
              <div v-if="selectedHelp.assigned_at" class="helper-time">
                分派时间：{{ formatTime(selectedHelp.assigned_at) }}
                <span v-if="selectedHelp.response_duration" class="ml-4">响应时长：{{ selectedHelp.response_duration }} 分钟</span>
              </div>
              <div v-if="selectedHelp.expected_response_minutes" class="expected-time">
                预计响应：{{ selectedHelp.expected_response_minutes }} 分钟内
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedHelp.is_risk && selectedHelp.risk_info" class="risk-info-section">
          <h4 class="detail-subtitle">🛡️ 风险求助详情</h4>
          <div class="risk-info-grid">
            <div class="risk-info-item">
              <span class="ri-label">风险等级</span>
              <span :class="['ri-value', selectedHelp.risk_level === 'high' ? 'text-danger' : 'text-warning']">
                {{ selectedHelp.risk_level === 'high' ? '🔴 高风险' : '🟡 中风险' }}
              </span>
            </div>
            <div class="risk-info-item">
              <span class="ri-label">诈骗类型</span>
              <span class="ri-value">{{ selectedHelp.risk_info.scam_type }}</span>
            </div>
            <div class="risk-info-item">
              <span class="ri-label">可疑来源</span>
              <span class="ri-value">{{ selectedHelp.risk_info.suspicious_source || '未提供' }}</span>
            </div>
            <div class="risk-info-item">
              <span class="ri-label">涉及金额</span>
              <span class="ri-value text-danger">{{ selectedHelp.risk_info.involved_amount ? '¥' + selectedHelp.risk_info.involved_amount : '未涉及' }}</span>
            </div>
            <div class="risk-info-item">
              <span class="ri-label">泄露验证码</span>
              <span :class="['ri-value', selectedHelp.risk_info.leaked_verification_code ? 'text-danger' : 'text-safe']">
                {{ selectedHelp.risk_info.leaked_verification_code ? '⚠️ 是' : '✅ 否' }}
              </span>
            </div>
            <div class="risk-info-item">
              <span class="ri-label">泄露支付密码</span>
              <span :class="['ri-value', selectedHelp.risk_info.leaked_payment_password ? 'text-danger' : 'text-safe']">
                {{ selectedHelp.risk_info.leaked_payment_password ? '⚠️ 是' : '✅ 否' }}
              </span>
            </div>
            <div class="risk-info-item">
              <span class="ri-label">点击可疑链接</span>
              <span :class="['ri-value', selectedHelp.risk_info.clicked_link ? 'text-danger' : 'text-safe']">
                {{ selectedHelp.risk_info.clicked_link ? '⚠️ 是' : '✅ 否' }}
              </span>
            </div>
          </div>
          <div v-if="selectedHelp.risk_info.custom_description" class="risk-custom-desc">
            <span class="ri-label">补充描述：</span>{{ selectedHelp.risk_info.custom_description }}
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

        <div v-if="selectedHelp.processing_note" class="detail-section">
          <h4 class="detail-subtitle">📝 处理备注</h4>
          <div class="processing-notes">
            <pre class="note-content">{{ selectedHelp.processing_note }}</pre>
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

          <div v-if="selectedHelp.status === 'processing' && isMyTask" class="add-step-form">
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

        <div v-if="selectedHelp.status_logs && selectedHelp.status_logs.length > 0" class="detail-section">
          <h4 class="detail-subtitle">📋 状态变更记录</h4>
          <div class="status-log-list">
            <div
              v-for="log in [...selectedHelp.status_logs].sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime())"
              :key="log.id"
              class="status-log-item"
            >
              <div class="log-time">{{ formatTime(log.created_at) }}</div>
              <div class="log-content">
                <span v-if="log.operator" class="log-operator">{{ log.operator.name }}</span>
                <span v-else class="log-operator">系统</span>
                <span class="log-action">
                  {{ log.note || (log.new_processing_status ? getProcessingStatusInfo(log.new_processing_status).label : getStatusLabel(log.new_status || '')) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedHelp.status === 'processing' && isMyTask" class="detail-actions">
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

        <div v-else-if="selectedHelp.status === 'pending'" class="detail-actions">
          <button class="btn btn-primary" @click="autoAssign(selectedHelp.id)">
            🤖 智能分派给最合适的家属
          </button>
          <button class="btn btn-secondary" @click="openManualAssign">
            👋 手动选择处理人
          </button>
          <button class="btn btn-success" @click="claimHelp">
            ✋ 我来处理这个求助
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
            <div v-if="selectedHelp.transfer_count > 0">
              <span class="text-muted">转派次数：</span>
              <span class="font-bold">{{ selectedHelp.transfer_count }} 次</span>
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

    <div v-if="showRiskDisposalModal" class="modal-overlay" @click.self="showRiskDisposalModal = false">
      <div class="modal-content" style="max-width: 520px;">
        <div class="modal-header">
          <h3>🛡️ 风险求助处置</h3>
          <button class="modal-close" @click="showRiskDisposalModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedHelp?.risk_info" class="disposal-risk-summary">
            <div class="drs-item"><strong>诈骗类型：</strong>{{ selectedHelp.risk_info.scam_type }}</div>
            <div class="drs-item"><strong>涉及金额：</strong>{{ selectedHelp.risk_info.involved_amount ? '¥' + selectedHelp.risk_info.involved_amount : '无' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">处置方式 *</label>
            <div class="disposal-options">
              <button v-for="dt in ['已阻止', '需报警', '需冻结支付', '误报', '继续观察']" :key="dt"
                :class="['disposal-btn', { active: riskDisposalType === dt }, 'disposal-' + dt]"
                @click="riskDisposalType = dt">
                {{ dt }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">处置备注</label>
            <textarea v-model="riskDisposalNote" class="form-textarea" rows="3" placeholder="记录处置详情..."></textarea>
          </div>
          <label class="risk-check" style="margin-top: 12px;">
            <input type="checkbox" v-model="shouldCreateStepCard" />
            <span>同时生成防诈骗步骤卡</span>
          </label>
          <div v-if="selectedHelp?.risk_disposals && selectedHelp.risk_disposals.length > 0" class="existing-disposals">
            <h4 class="detail-subtitle" style="margin-top: 16px;">📋 已有处置记录</h4>
            <div v-for="d in selectedHelp.risk_disposals" :key="d.id" class="disposal-record">
              <span :class="['disposal-type-badge', 'disposal-' + d.disposal_type]">{{ d.disposal_type }}</span>
              <span class="text-sm text-muted">{{ d.operator?.name || '家属' }} · {{ formatTime(d.created_at) }}</span>
              <span v-if="d.note" class="text-sm">{{ d.note }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRiskDisposalModal = false">取消</button>
          <button class="btn btn-danger" :disabled="!riskDisposalType" @click="submitRiskDisposal">确认处置</button>
        </div>
      </div>
    </div>

    <div v-if="showTransferModal" class="modal-overlay" @click.self="showTransferModal = false">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h3>🔄 转派求助</h3>
          <button class="modal-close" @click="showTransferModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">选择转派对象 *</label>
            <select v-model="transferToId" class="form-select">
              <option :value="0">请选择家属</option>
              <option
                v-for="m in familyMembers.filter(f => f.id !== currentUserId)"
                :key="m.id"
                :value="m.id"
              >
                {{ m.name }}
                <span v-if="m.is_online"> (在线)</span>
                <span v-if="m.is_on_duty"> [值班]</span>
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">转派原因（可选）</label>
            <textarea
              v-model="transferReason"
              class="form-textarea"
              rows="3"
              placeholder="例如：该问题涉及苹果设备，我不太熟悉..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showTransferModal = false">取消</button>
          <button class="btn btn-primary" @click="transferHelp">确认转派</button>
        </div>
      </div>
    </div>

    <div v-if="showNoteModal" class="modal-overlay" @click.self="showNoteModal = false">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h3>📝 添加处理备注</h3>
          <button class="modal-close" @click="showNoteModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">备注内容 *</label>
            <textarea
              v-model="noteContent"
              class="form-textarea"
              rows="4"
              placeholder="记录处理进展、老人反馈等信息..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showNoteModal = false">取消</button>
          <button class="btn btn-primary" @click="submitNote">确认添加</button>
        </div>
      </div>
    </div>

    <div v-if="showAssignModal" class="modal-overlay" @click.self="showAssignModal = false">
      <div class="modal-content" style="max-width: 560px;">
        <div class="modal-header">
          <h3>👋 手动分派求助</h3>
          <button class="modal-close" @click="showAssignModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="recommendCandidates.length > 0" class="recommend-section mb-4">
            <h4 class="detail-subtitle">🤖 系统推荐</h4>
            <div class="candidate-list">
              <div
                v-for="(c, idx) in recommendCandidates.slice(0, 3)"
                :key="c.user.id"
                class="candidate-item"
                :class="{ selected: assignToId === c.user.id }"
                @click="assignToId = c.user.id"
              >
                <div class="candidate-rank">{{ idx + 1 }}</div>
                <div class="candidate-info">
                  <div class="candidate-name">{{ c.user.name }}</div>
                  <div class="candidate-reason text-sm text-muted">{{ c.reason }}</div>
                </div>
                <div class="candidate-score">
                  <div class="score-value">{{ c.score }}</div>
                  <div class="score-label">匹配度</div>
                </div>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">选择处理人 *</label>
            <select v-model="assignToId" class="form-select">
              <option :value="0">请选择家属</option>
              <option v-for="m in familyMembers" :key="m.id" :value="m.id">
                {{ m.name }}
                <span v-if="m.is_online"> (在线)</span>
                <span v-if="m.is_on_duty"> [值班]</span>
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">分派原因（可选）</label>
            <textarea
              v-model="assignReason"
              class="form-textarea"
              rows="2"
              placeholder="例如：根据问题类型和设备品牌匹配..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAssignModal = false">取消</button>
          <button class="btn btn-primary" @click="manualAssign">确认分派</button>
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

.help-item.timeout {
  border-left: 4px solid #ef4444;
}

.help-item-header {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
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

.help-helper {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
  color: #6366f1;
  font-weight: 500;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.action-toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.processing-status-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f1f5f9;
  border-radius: 12px;
  flex-wrap: wrap;
}

.status-label {
  font-weight: 600;
  color: #475569;
  flex-shrink: 0;
}

.status-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
}

.status-btn {
  padding: 8px 14px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.status-btn:hover {
  border-color: #667eea;
}

.status-btn.active {
  border-color: transparent;
  color: white;
}

.helper-info-section {
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  border-left: 4px solid #0284c7;
}

.helper-info-card {
  display: flex;
  gap: 16px;
  align-items: center;
}

.helper-avatar {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.helper-info {
  flex: 1;
}

.helper-name {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.helper-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  display: inline-block;
}

.helper-time {
  font-size: 13px;
  color: #475569;
  margin-bottom: 2px;
}

.expected-time {
  font-size: 13px;
  color: #0284c7;
  font-weight: 500;
}

.ml-2 {
  margin-left: 8px;
}

.ml-4 {
  margin-left: 16px;
}

.text-green {
  color: #16a34a;
}

.processing-notes {
  padding: 16px;
  background: #fefce8;
  border-radius: 12px;
  border-left: 4px solid #f59e0b;
}

.note-content {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
  color: #854d0e;
}

.status-log-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-log-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border-left: 3px solid #667eea;
}

.log-time {
  flex-shrink: 0;
  font-size: 12px;
  color: #64748b;
  min-width: 100px;
}

.log-content {
  flex: 1;
  font-size: 14px;
  color: #334155;
}

.log-operator {
  font-weight: 600;
  color: #1e293b;
  margin-right: 8px;
}

.log-action {
  color: #475569;
}

.recommend-section {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.candidate-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.candidate-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.candidate-item:hover {
  border-color: #667eea;
}

.candidate-item.selected {
  border-color: #667eea;
  background: #eef2ff;
}

.candidate-rank {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.candidate-info {
  flex: 1;
}

.candidate-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.candidate-score {
  text-align: center;
  flex-shrink: 0;
}

.score-value {
  font-size: 24px;
  font-weight: 800;
  color: #667eea;
  line-height: 1;
}

.score-label {
  font-size: 11px;
  color: #64748b;
}

.badge-danger {
  background: #fee2e2 !important;
  color: #dc2626 !important;
}

.badge-success {
  background: #dcfce7 !important;
  color: #166534 !important;
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(245, 158, 11, 0.4);
}

.btn-info {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: white;
  border: none;
}

.btn-info:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(6, 182, 212, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(239, 68, 68, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%);
  color: white;
  border: none;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(100, 116, 139, 0.3);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.4);
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-lg {
  padding: 12px 28px;
  font-size: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.grid {
  display: grid;
  gap: 12px;
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}

.mb-3 {
  margin-bottom: 12px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mb-6 {
  margin-bottom: 24px;
}

.mt-2 {
  margin-top: 8px;
}

.mt-3 {
  margin-top: 12px;
}

.mt-4 {
  margin-top: 16px;
}

.text-sm {
  font-size: 13px;
}

.text-muted {
  color: #64748b;
}

.text-green {
  color: #16a34a;
}

.text-orange {
  color: #ea580c;
}

.font-bold {
  font-weight: 700;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-pending {
  background: #fef3c7;
  color: #92400e;
}

.badge-assigned {
  background: #dbeafe;
  color: #1e40af;
}

.badge-processing {
  background: #ddd6fe;
  color: #5b21b6;
}

.badge-resolved {
  background: #dcfce7;
  color: #166534;
}

.badge-normal {
  background: #f1f5f9;
  color: #475569;
}

.tag {
  display: inline-block;
  padding: 3px 10px;
  background: #eef2ff;
  color: #4f46e5;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}

.step-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 10px;
  margin-bottom: 8px;
}

.step-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.step-content {
  flex: 1;
}

.step-text {
  font-size: 14px;
  color: #1e293b;
  line-height: 1.6;
}

.tip-box {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 8px;
  font-size: 13px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.badge-risk {
  background: #fef2f2 !important;
  color: #dc2626 !important;
}

.risk-info-section {
  padding: 16px;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 12px;
  border: 2px solid #fca5a5;
}

.risk-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 12px;
}

.risk-info-item {
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ri-label {
  font-size: 12px;
  color: #64748b;
}

.ri-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.text-danger {
  color: #dc2626 !important;
}

.text-warning {
  color: #f59e0b !important;
}

.text-safe {
  color: #16a34a !important;
}

.risk-custom-desc {
  margin-top: 12px;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  color: #334155;
  line-height: 1.6;
}

.disposal-risk-summary {
  padding: 12px 16px;
  background: #fef2f2;
  border-radius: 10px;
  margin-bottom: 16px;
  display: flex;
  gap: 20px;
}

.drs-item {
  font-size: 14px;
  color: #334155;
}

.disposal-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.disposal-btn {
  padding: 10px 18px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #475569;
}

.disposal-btn:hover {
  border-color: #ef4444;
}

.disposal-btn.active {
  color: white;
  border-color: transparent;
}

.disposal-btn.disposal-已阻止.active { background: #10b981; }
.disposal-btn.disposal-需报警.active { background: #ef4444; }
.disposal-btn.disposal-需冻结支付.active { background: #f59e0b; }
.disposal-btn.disposal-误报.active { background: #64748b; }
.disposal-btn.disposal-继续观察.active { background: #667eea; }

.existing-disposals {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.disposal-record {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.disposal-type-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.disposal-type-badge.disposal-已阻止 { background: #dcfce7; color: #166534; }
.disposal-type-badge.disposal-需报警 { background: #fee2e2; color: #dc2626; }
.disposal-type-badge.disposal-需冻结支付 { background: #fef3c7; color: #92400e; }
.disposal-type-badge.disposal-误报 { background: #f1f5f9; color: #64748b; }
.disposal-type-badge.disposal-继续观察 { background: #dbeafe; color: #1e40af; }

.risk-check {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
}

.risk-check input {
  width: 18px;
  height: 18px;
}
</style>
