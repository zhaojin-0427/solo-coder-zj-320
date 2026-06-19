<script setup lang="ts">
import { ref, watch, onBeforeUnmount, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { helpApi, stepcardApi, deviceApi } from '@/api'
import { PROBLEM_TYPES, DEVICE_BRANDS, SYSTEM_VERSIONS, SCAM_TYPES, type StepCard, type DeviceProfile, type HelpRequest } from '@/types'

const router = useRouter()

const problemType = ref('')
const title = ref('')
const description = ref('')
const deviceBrand = ref('')
const systemVersion = ref('')
const imageUrl = ref('')
const imageFile = ref<File | null>(null)
const submitting = ref(false)
const submitted = ref(false)
const suggestedCards = ref<StepCard[]>([])
const isLoadingSuggestions = ref(false)
const deviceProfile = ref<DeviceProfile | null>(null)
const currentHelp = ref<HelpRequest | null>(null)
let statusPollingTimer: number | null = null

const isRiskMode = ref(false)
const riskInfo = ref({
  scam_type: '',
  suspicious_source: '',
  involved_amount: 0,
  leaked_verification_code: false,
  leaked_payment_password: false,
  clicked_link: false,
  risk_keywords: '',
  custom_description: ''
})

const riskScenarios: { type: string; icon: string; desc: string }[] = [
  { type: '陌生来电', icon: '📱', desc: '接到可疑电话，对方要求操作' },
  { type: '短信链接', icon: '📩', desc: '收到不明短信，含可疑链接' },
  { type: '中奖弹窗', icon: '🎁', desc: '手机弹出中奖提示' },
  { type: '要求转账', icon: '💸', desc: '对方要求转账汇款' },
  { type: '索要验证码', icon: '🔑', desc: '对方索要手机验证码' },
  { type: '远程控制', icon: '🖥️', desc: '对方要求远程操控手机' }
]

const selectRiskScenario = (type: string) => {
  isRiskMode.value = true
  riskInfo.value.scam_type = type
  problemType.value = '防诈骗'
  if (!title.value) {
    title.value = type + '风险求助'
  }
}

const loadDeviceProfile = async () => {
  try {
    const profile = await deviceApi.getProfileByUser(1)
    if (profile) {
      deviceProfile.value = profile
      deviceBrand.value = profile.device_brand || ''
      systemVersion.value = profile.system_version || ''
    }
  } catch (e) {
    console.error(e)
  }
}

const quickOptions: { type: string; icon: string; desc: string }[] = [
  { type: '看不清字', icon: '🔍', desc: '字体太小，看不清屏幕' },
  { type: '找不到入口', icon: '🧭', desc: '找不到某个功能在哪' },
  { type: '误触广告', icon: '🚫', desc: '手机总是弹出广告' },
  { type: '不会切换网络', icon: '📶', desc: 'WiFi或流量不会切换' },
  { type: '支付设置', icon: '💰', desc: '支付相关的问题' },
  { type: '声音太小', icon: '🔊', desc: '听不清手机声音' }
]

const selectQuick = (type: string) => {
  problemType.value = type
  if (!title.value) {
    title.value = type + '问题求助'
  }
}

watch(problemType, (val) => {
  if (val) {
    fetchSuggestions(val)
  } else {
    suggestedCards.value = []
  }
})

const fetchSuggestions = async (type: string) => {
  isLoadingSuggestions.value = true
  try {
    const params: { problem_type: string; device_brand?: string } = { problem_type: type }
    if (deviceBrand.value) {
      params.device_brand = deviceBrand.value
    }
    suggestedCards.value = await stepcardApi.list(params)
  } catch (e) {
    console.error(e)
    suggestedCards.value = []
  } finally {
    isLoadingSuggestions.value = false
  }
}

const handleImageFile = (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    imageFile.value = file
    if (imageUrl.value) URL.revokeObjectURL(imageUrl.value)
    imageUrl.value = URL.createObjectURL(file)
  }
}

const removeImage = () => {
  if (imageUrl.value) URL.revokeObjectURL(imageUrl.value)
  imageUrl.value = ''
  imageFile.value = null
}

const audioUrl = ref('')
const isRecording = ref(false)
const recordingSeconds = ref(0)
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let timerId: number | null = null
let stream: MediaStream | null = null

const startRecording = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioChunks = []
    mediaRecorder = new MediaRecorder(stream)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
      audioUrl.value = URL.createObjectURL(blob)
    }
    mediaRecorder.start()
    isRecording.value = true
    recordingSeconds.value = 0
    timerId = window.setInterval(() => {
      recordingSeconds.value += 1
      if (recordingSeconds.value >= 60) {
        stopRecording()
      }
    }, 1000)
  } catch (e) {
    console.error(e)
    alert('无法访问麦克风，请检查浏览器权限设置或使用文字描述')
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  if (stream) {
    stream.getTracks().forEach((t) => t.stop())
    stream = null
  }
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
  isRecording.value = false
}

const removeAudio = () => {
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
  audioUrl.value = ''
  recordingSeconds.value = 0
}

const formatDuration = (s: number) => {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

onBeforeUnmount(() => {
  if (isRecording.value) stopRecording()
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
})

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'pending': '待分派',
    'assigned': '已分派',
    'processing': '处理中',
    'resolved': '已解决'
  }
  return map[status] || status
}

const getProcessingStatusLabel = (status?: string) => {
  const map: Record<string, string> = {
    'phone_guidance': '📞 电话指导中',
    'waiting_operation': '⏳ 等待老人操作',
    'need_confirm': '❓ 需二次确认',
    'resolved': '✅ 已解决'
  }
  return status ? (map[status] || status) : ''
}

const pollHelpStatus = async () => {
  if (!currentHelp.value) return
  try {
    const updated = await helpApi.get(currentHelp.value.id)
    currentHelp.value = updated
    if (updated.status === 'resolved') {
      if (statusPollingTimer) {
        clearInterval(statusPollingTimer)
        statusPollingTimer = null
      }
    }
  } catch (e) {
    console.error('Failed to poll status:', e)
  }
}

const submitHelp = async () => {
  if (!problemType.value || !title.value) {
    alert('请选择问题类型并填写简要描述')
    return
  }
  submitting.value = true
  try {
    const help = await helpApi.create({
      title: title.value,
      problem_type: problemType.value,
      description: description.value,
      device_brand: deviceBrand.value,
      system_version: systemVersion.value,
      image_url: imageUrl.value,
      audio_url: audioUrl.value || undefined,
      device_profile_id: deviceProfile.value?.id,
      risk_info: isRiskMode.value && riskInfo.value.scam_type ? riskInfo.value : undefined
    })
    currentHelp.value = help
    
    try {
      const assignResult = await helpApi.autoAssign(help.id)
      currentHelp.value = assignResult.help_request
    } catch (e) {
      console.warn('Auto assign failed:', e)
    }
    
    submitted.value = true
    statusPollingTimer = window.setInterval(pollHelpStatus, 5000)
  } catch (e) {
    console.error(e)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onUnmounted(() => {
  if (statusPollingTimer) {
    clearInterval(statusPollingTimer)
  }
})

const openCard = (id: number) => {
  stepcardApi.use(id)
  router.push(`/library/${id}`)
}

const resetForm = () => {
  removeAudio()
  removeImage()
  problemType.value = ''
  title.value = ''
  description.value = ''
  isRiskMode.value = false
  riskInfo.value = {
    scam_type: '',
    suspicious_source: '',
    involved_amount: 0,
    leaked_verification_code: false,
    leaked_payment_password: false,
    clicked_link: false,
    risk_keywords: '',
    custom_description: ''
  }
  if (deviceProfile.value) {
    deviceBrand.value = deviceProfile.value.device_brand || ''
    systemVersion.value = deviceProfile.value.system_version || ''
  } else {
    deviceBrand.value = ''
    systemVersion.value = ''
  }
  submitted.value = false
  suggestedCards.value = []
  isLoadingSuggestions.value = false
  currentHelp.value = null
  if (statusPollingTimer) {
    clearInterval(statusPollingTimer)
    statusPollingTimer = null
  }
}

watch(deviceBrand, () => {
  if (problemType.value) {
    fetchSuggestions(problemType.value)
  }
})

const formatTime = (dateStr?: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(loadDeviceProfile)
</script>

<template>
  <div v-if="submitted" class="card success-card">
    <div v-if="currentHelp?.status === 'resolved'" class="success-icon">✅</div>
    <div v-else-if="currentHelp?.status === 'processing'" class="success-icon">📞</div>
    <div v-else-if="currentHelp?.status === 'assigned'" class="success-icon">👋</div>
    <div v-else class="success-icon">⏳</div>
    
    <h2 class="success-title">
      {{ currentHelp?.status === 'resolved' ? '问题已解决！' : '求助已成功发出！' }}
    </h2>
    <p class="success-desc">
      {{ currentHelp?.status === 'resolved' 
        ? '您的问题已经得到解决，感谢您使用我们的服务。' 
        : '您的家人已收到通知，会尽快通过电话或远程指导帮助您解决问题。' }}
    </p>

    <div v-if="currentHelp" class="help-status-card">
      <div class="status-header">
        <span :class="['status-badge', 'badge-' + currentHelp.status]">
          {{ getStatusLabel(currentHelp.status) }}
        </span>
        <span v-if="currentHelp.processing_status && currentHelp.status === 'processing'" class="processing-badge">
          {{ getProcessingStatusLabel(currentHelp.processing_status) }}
        </span>
        <span v-if="currentHelp.is_timeout" class="badge badge-danger">⚠️ 响应超时</span>
      </div>

      <div v-if="currentHelp.helper" class="helper-info">
        <div class="helper-avatar">👤</div>
        <div class="helper-details">
          <div class="helper-name">{{ currentHelp.helper.name }}</div>
          <div class="helper-meta">
            <span v-if="currentHelp.helper.is_online" class="online-indicator"></span>
            <span>{{ currentHelp.helper.is_online ? '在线' : '离线' }}</span>
            <span v-if="currentHelp.helper.is_on_duty" class="duty-badge">值班中</span>
          </div>
          <div v-if="currentHelp.expected_response_minutes" class="expected-time">
            ⏱️ 预计 {{ currentHelp.expected_response_minutes }} 分钟内响应
          </div>
          <div v-if="currentHelp.assigned_at" class="assign-time">
            📅 分派时间：{{ formatTime(currentHelp.assigned_at) }}
          </div>
          <div v-if="currentHelp.response_duration" class="response-time">
            ⚡ 实际响应：{{ currentHelp.response_duration }} 分钟
          </div>
        </div>
      </div>

      <div v-else class="no-helper">
        <div class="no-helper-icon">🔍</div>
        <div>正在为您匹配最合适的家属...</div>
      </div>

      <div v-if="currentHelp.processing_note" class="processing-notes">
        <div class="notes-title">📝 处理备注</div>
        <pre class="notes-content">{{ currentHelp.processing_note }}</pre>
      </div>

      <div v-if="currentHelp.status_logs && currentHelp.status_logs.length > 0" class="status-timeline">
        <div class="timeline-title">📋 处理进度</div>
        <div class="timeline-list">
          <div
            v-for="log in [...currentHelp.status_logs].sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()).slice(0, 5)"
            :key="log.id"
            class="timeline-item"
          >
            <div class="timeline-time">{{ formatTime(log.created_at) }}</div>
            <div class="timeline-content">
              <span class="timeline-operator">{{ log.operator?.name || '系统' }}</span>
              <span class="timeline-action">
                {{ log.note || (log.new_processing_status ? getProcessingStatusLabel(log.new_processing_status) : getStatusLabel(log.new_status || '')) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="success-actions">
      <button class="btn btn-primary btn-lg" @click="resetForm">继续发起新求助</button>
      <button class="btn btn-secondary btn-lg" @click="$router.push('/guidance')">查看求助记录</button>
    </div>
  </div>

  <div v-else>
    <div v-if="deviceProfile" class="card mb-6 device-profile-banner">
      <div class="profile-banner-content">
        <div class="profile-banner-icon">📱</div>
        <div class="profile-banner-info">
          <div class="profile-banner-title">设备档案已自动加载</div>
          <div class="profile-banner-detail">
            {{ deviceProfile.device_brand || '未设置' }} · {{ deviceProfile.system_version || '未设置' }}
            <span v-if="deviceProfile.font_size_preference"> · 字体{{ deviceProfile.font_size_preference }}</span>
            <span v-if="deviceProfile.simple_mode_enabled"> · 简易模式</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-6">
      <h3 class="section-title">🎯 常见问题快速选择</h3>
      <p class="text-muted mb-4">请点击最接近您遇到的问题，系统会自动匹配历史解决方案</p>
      <div class="grid grid-3">
        <button
          v-for="opt in quickOptions"
          :key="opt.type"
          class="quick-card"
          :class="{ active: problemType === opt.type }"
          @click="selectQuick(opt.type)"
        >
          <div class="quick-icon">{{ opt.icon }}</div>
          <div class="quick-type">{{ opt.type }}</div>
          <div class="quick-desc">{{ opt.desc }}</div>
        </button>
      </div>
    </div>

    <div class="card mb-6 risk-alert-section">
      <h3 class="section-title">🛡️ 防诈骗风险求助</h3>
      <p class="text-muted mb-4">如果您遇到可疑情况，请选择对应的风险场景，系统将优先通知家属</p>
      <div class="grid grid-3">
        <button
          v-for="rs in riskScenarios"
          :key="rs.type"
          class="risk-card"
          :class="{ active: isRiskMode && riskInfo.scam_type === rs.type }"
          @click="selectRiskScenario(rs.type)"
        >
          <div class="risk-icon">{{ rs.icon }}</div>
          <div class="risk-type">{{ rs.type }}</div>
          <div class="risk-desc">{{ rs.desc }}</div>
        </button>
      </div>
    </div>

    <div v-if="isRiskMode" class="card mb-6 risk-detail-section">
      <h3 class="section-title">⚠️ 风险详情补充</h3>
      <p class="text-muted mb-4">补充以下信息有助于家属更快速判断风险程度</p>
      <div class="grid grid-2">
        <div class="form-group">
          <label class="form-label">可疑信息来源</label>
          <input v-model="riskInfo.suspicious_source" class="form-input" placeholder="例如：+86 138****5678" />
        </div>
        <div class="form-group">
          <label class="form-label">涉及金额（元）</label>
          <input v-model.number="riskInfo.involved_amount" class="form-input" type="number" min="0" placeholder="0" />
        </div>
      </div>
      <div class="risk-check-group">
        <label class="risk-check">
          <input type="checkbox" v-model="riskInfo.leaked_verification_code" />
          <span>是否已泄露验证码</span>
        </label>
        <label class="risk-check">
          <input type="checkbox" v-model="riskInfo.leaked_payment_password" />
          <span>是否已泄露支付密码</span>
        </label>
        <label class="risk-check">
          <input type="checkbox" v-model="riskInfo.clicked_link" />
          <span>是否已点击可疑链接</span>
        </label>
      </div>
      <div class="form-group">
        <label class="form-label">其他描述（可选）</label>
        <textarea v-model="riskInfo.custom_description" class="form-textarea" rows="2" placeholder="描述具体情况，如对方说了什么、要求做什么..."></textarea>
      </div>
    </div>

    <div v-if="isLoadingSuggestions" class="card mb-6 suggestion-card loading-card">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在为您匹配历史方案...</p>
    </div>

    <div v-else-if="suggestedCards.length > 0" class="card mb-6 suggestion-card">
      <div class="suggestion-header">
        <h3 class="section-title mb-2">💡 为您找到 {{ suggestedCards.length }} 个历史方案</h3>
        <p class="text-muted">也许下面的方法可以帮您立即解决问题，无需等待家人回复</p>
      </div>
      <div class="grid grid-2">
        <div
          v-for="card in suggestedCards.slice(0, 4)"
          :key="card.id"
          class="suggestion-item"
          @click="openCard(card.id)"
        >
          <div class="suggestion-title">
            <span :class="['badge', 'badge-' + card.difficulty]">
              {{ card.difficulty === 'easy' ? '简单' : card.difficulty === 'normal' ? '一般' : '较难' }}
            </span>
            {{ card.title }}
          </div>
          <div class="suggestion-meta">
            <span v-if="card.device_brand">{{ card.device_brand }}</span>
            <span v-if="card.system_version"> · {{ card.system_version }}</span>
            <span> · 已使用 {{ card.usage_count }} 次</span>
          </div>
          <div v-if="card.device_tips && card.device_tips.length > 0 && deviceBrand" class="suggestion-adapt">
            📱 含{{ deviceBrand }}适配提示
          </div>
          <div class="suggestion-steps">共 {{ card.steps.length }} 个操作步骤</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="section-title">📝 详细描述问题</h3>
      <p class="text-muted mb-4">填写以下信息可以帮助家人更快了解情况</p>

      <div class="grid grid-2">
        <div class="form-group">
          <label class="form-label">问题类型</label>
          <select v-model="problemType" class="form-select">
            <option value="">请选择问题类型</option>
            <option v-for="t in PROBLEM_TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">简要标题</label>
          <input v-model="title" class="form-input" placeholder="例如：手机字体太小看不清" />
        </div>

        <div class="form-group">
          <label class="form-label">手机品牌</label>
          <select v-model="deviceBrand" class="form-select">
            <option value="">请选择品牌</option>
            <option v-for="b in DEVICE_BRANDS" :key="b" :value="b">{{ b }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">系统版本</label>
          <select v-model="systemVersion" class="form-select">
            <option value="">请选择版本</option>
            <option v-for="s in SYSTEM_VERSIONS" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">详细描述问题</label>
        <textarea
          v-model="description"
          class="form-textarea"
          placeholder="请尽量详细地描述您遇到的问题，例如：'打开微信后字体太小，想要调大一点，但不知道在哪里设置'"
        ></textarea>
      </div>

      <div class="form-group">
        <label class="form-label">上传截图（可选）</label>
        <div class="upload-area">
          <div v-if="imageUrl" class="image-preview">
            <img :src="imageUrl" alt="截图预览" />
            <button class="remove-btn" @click="removeImage">×</button>
          </div>
          <label v-else class="upload-btn">
            <div class="upload-icon">📷</div>
            <div>点击上传屏幕截图</div>
            <div class="text-sm text-muted">支持拍照或从相册选择</div>
            <input type="file" accept="image/*" class="file-input" @change="handleImageFile" />
          </label>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">语音描述（可选）</label>
        <div class="audio-area">
          <div v-if="!audioUrl && !isRecording" class="audio-idle">
            <button class="record-btn" @click="startRecording">
              <span class="record-icon">🎙️</span>
              <span>按住说话 / 点击录音</span>
            </button>
            <div class="text-sm text-muted mt-2">说不太清楚时，可以直接用语音描述问题</div>
          </div>

          <div v-else-if="isRecording" class="audio-recording">
            <div class="recording-indicator">
              <span class="rec-dot"></span>
              <span class="rec-time">{{ formatDuration(recordingSeconds) }}</span>
              <span class="text-sm text-muted">录音中...</span>
            </div>
            <button class="btn btn-danger" @click="stopRecording">⏹ 停止录音</button>
          </div>

          <div v-else class="audio-playback">
            <div class="playback-info">
              <span class="playback-icon">🔊</span>
              <span>录音已就绪</span>
              <span class="text-sm text-muted">（{{ formatDuration(recordingSeconds) }}）</span>
            </div>
            <audio :src="audioUrl" controls class="audio-player"></audio>
            <div class="audio-actions">
              <button class="btn btn-secondary" @click="startRecording">🎤 重新录制</button>
              <button class="btn btn-secondary" @click="removeAudio">🗑 删除录音</button>
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="resetForm">重置</button>
        <button class="btn btn-primary btn-lg" :disabled="submitting" @click="submitHelp">
          {{ submitting ? '提交中...' : '📞 一键呼叫家人帮助' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.device-profile-banner {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  border-left: 4px solid #0284c7;
}

.profile-banner-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-banner-icon {
  font-size: 40px;
}

.profile-banner-title {
  font-size: 16px;
  font-weight: 700;
  color: #0c4a6e;
  margin-bottom: 2px;
}

.profile-banner-detail {
  font-size: 14px;
  color: #0369a1;
}

.quick-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 3px solid transparent;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.quick-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
}

.quick-icon {
  font-size: 42px;
  margin-bottom: 8px;
}

.quick-type {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.quick-desc {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.suggestion-card {
  background: linear-gradient(135deg, #fefce8 0%, #fef9c3 100%);
  border-left: 4px solid #f59e0b;
}

.suggestion-item {
  background: white;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.suggestion-item:hover {
  border-color: #667eea;
  transform: translateX(4px);
}

.suggestion-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 6px;
}

.suggestion-meta {
  font-size: 13px;
  color: #64748b;
}

.suggestion-steps {
  margin-top: 8px;
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
}

.suggestion-adapt {
  margin-top: 6px;
  padding: 4px 10px;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  background: #fafbfc;
}

.upload-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.image-preview {
  position: relative;
  display: inline-block;
}

.image-preview img {
  max-width: 300px;
  border-radius: 8px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  border: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.audio-area {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  background: #fafbfc;
}

.audio-idle {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.record-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(245, 87, 108, 0.4);
}

.record-icon {
  font-size: 22px;
}

.audio-recording {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rec-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ef4444;
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.rec-time {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  font-variant-numeric: tabular-nums;
}

.audio-playback {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.playback-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #15803d;
}

.playback-icon {
  font-size: 22px;
}

.audio-player {
  width: 100%;
  max-width: 360px;
}

.audio-actions {
  display: flex;
  gap: 10px;
}

.success-card {
  text-align: center;
  padding: 60px 40px;
}

.success-icon {
  font-size: 80px;
  margin-bottom: 16px;
}

.success-title {
  font-size: 28px;
  color: #15803d;
  margin-bottom: 12px;
}

.success-desc {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 32px;
}

.success-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #fef3c7;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #92400e;
  font-size: 14px;
}

.help-status-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 24px;
  margin: 24px 0;
  text-align: left;
  border: 1px solid #e2e8f0;
}

.status-header {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.status-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
}

.status-badge.badge-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.badge-assigned {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.badge-processing {
  background: #ddd6fe;
  color: #5b21b6;
}

.status-badge.badge-resolved {
  background: #dcfce7;
  color: #166534;
}

.processing-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.helper-info {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  margin-bottom: 16px;
  border-left: 4px solid #0284c7;
}

.helper-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.helper-details {
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

.online-indicator {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  display: inline-block;
}

.duty-badge {
  background: #dcfce7;
  color: #166534;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.expected-time,
.assign-time,
.response-time {
  font-size: 13px;
  color: #475569;
  margin-top: 2px;
}

.expected-time {
  color: #0284c7;
  font-weight: 500;
}

.no-helper {
  text-align: center;
  padding: 24px;
  background: #fef3c7;
  border-radius: 12px;
  margin-bottom: 16px;
  color: #92400e;
}

.no-helper-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.processing-notes {
  margin-bottom: 16px;
  padding: 16px;
  background: #fefce8;
  border-radius: 12px;
  border-left: 4px solid #f59e0b;
}

.notes-title {
  font-weight: 600;
  color: #854d0e;
  margin-bottom: 8px;
  font-size: 14px;
}

.notes-content {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 13px;
  color: #854d0e;
  line-height: 1.8;
}

.status-timeline {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.timeline-title {
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
  font-size: 14px;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.timeline-time {
  flex-shrink: 0;
  font-size: 12px;
  color: #64748b;
  min-width: 90px;
}

.timeline-content {
  flex: 1;
  font-size: 13px;
  color: #334155;
}

.timeline-operator {
  font-weight: 600;
  color: #1e293b;
  margin-right: 8px;
}

.badge-danger {
  background: #fee2e2 !important;
  color: #dc2626 !important;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(100, 116, 139, 0.3);
}

.btn-lg {
  padding: 12px 28px;
  font-size: 16px;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.mb-6 {
  margin-bottom: 24px;
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

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 768px) {
  .grid-2, .grid-3 {
    grid-template-columns: 1fr;
  }
}

.text-muted {
  color: #64748b;
}

.text-sm {
  font-size: 13px;
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

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
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

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-easy {
  background: #dcfce7;
  color: #166534;
}

.badge-normal {
  background: #fef3c7;
  color: #92400e;
}

.badge-hard {
  background: #fee2e2;
  color: #dc2626;
}

.risk-alert-section {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-left: 4px solid #ef4444;
}

.risk-card {
  background: white;
  border: 3px solid transparent;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.risk-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.15);
}

.risk-card.active {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.risk-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.risk-type {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.risk-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.risk-detail-section {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border-left: 4px solid #f59e0b;
}

.risk-check-group {
  display: flex;
  gap: 24px;
  margin: 16px 0;
  flex-wrap: wrap;
}

.risk-check {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #dc2626;
  font-weight: 600;
  font-size: 14px;
}

.risk-check input {
  width: 18px;
  height: 18px;
}
</style>
