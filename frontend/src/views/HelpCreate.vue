<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { helpApi, stepcardApi } from '@/api'
import { PROBLEM_TYPES, DEVICE_BRANDS, SYSTEM_VERSIONS, type StepCard } from '@/types'

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
    suggestedCards.value = await stepcardApi.list(type)
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

const submitHelp = async () => {
  if (!problemType.value || !title.value) {
    alert('请选择问题类型并填写简要描述')
    return
  }
  submitting.value = true
  try {
    await helpApi.create({
      title: title.value,
      problem_type: problemType.value,
      description: description.value,
      device_brand: deviceBrand.value,
      system_version: systemVersion.value,
      image_url: imageUrl.value,
      audio_url: audioUrl.value || undefined
    })
    submitted.value = true
  } catch (e) {
    console.error(e)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

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
  deviceBrand.value = ''
  systemVersion.value = ''
  submitted.value = false
  suggestedCards.value = []
  isLoadingSuggestions.value = false
}
</script>

<template>
  <div v-if="submitted" class="card success-card">
    <div class="success-icon">✅</div>
    <h2 class="success-title">求助已成功发出！</h2>
    <p class="success-desc">您的家人已收到通知，会尽快通过电话或远程指导帮助您解决问题。</p>
    <div class="success-actions">
      <button class="btn btn-primary btn-lg" @click="resetForm">继续发起新求助</button>
      <button class="btn btn-secondary btn-lg" @click="$router.push('/guidance')">查看求助记录</button>
    </div>
  </div>

  <div v-else>
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
</style>
