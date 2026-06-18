import axios from 'axios'
import type { HelpRequest, StepCard, User, StatsOverview, GuidanceRecord, PracticeRecord, PracticeStepFeedback, CardPracticeStats, PracticeStats, StepCardStep, DeviceProfile, DeviceStats, StepCardDeviceTip } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const userApi = {
  list: () => api.get<User[]>('/user/').then(r => r.data)
}

export const helpApi = {
  list: (status?: string) =>
    api.get<HelpRequest[]>('/help/', { params: status ? { status } : {} }).then(r => r.data),
  get: (id: number) => api.get<HelpRequest>(`/help/${id}`).then(r => r.data),
  create: (data: Partial<HelpRequest>) =>
    api.post<HelpRequest>('/help/', data).then(r => r.data),
  addGuidance: (id: number, data: Partial<GuidanceRecord>) =>
    api.post<GuidanceRecord>(`/help/${id}/guidance`, data).then(r => r.data),
  resolve: (id: number, data: { helper_id?: number; is_independent?: boolean } = {}) =>
    api.post<HelpRequest>(`/help/${id}/resolve`, data).then(r => r.data)
}

export const stepcardApi = {
  list: (params?: { problem_type?: string; device_brand?: string }) =>
    api.get<StepCard[]>('/stepcard/', { params: params || {} }).then(r => r.data),
  get: (id: number) => api.get<StepCard>(`/stepcard/${id}`).then(r => r.data),
  create: (data: Partial<StepCard> & { steps?: any[] }) =>
    api.post<StepCard>('/stepcard/', data).then(r => r.data),
  createFromHelp: (help_id: number, data?: Partial<StepCard>) =>
    api.post<StepCard>(`/stepcard/from_help/${help_id}`, data || {}).then(r => r.data),
  use: (id: number) => api.post<StepCard>(`/stepcard/${id}/use`).then(r => r.data),
  addTip: (id: number, data: { step_number: number; tip: string }) =>
    api.post<StepCardStep>(`/stepcard/${id}/add_tip`, data).then(r => r.data),
  getPracticeStats: (id: number) =>
    api.get<CardPracticeStats>(`/practice/card_stats/${id}`).then(r => r.data),
  getDeviceTips: (id: number) =>
    api.get<StepCardDeviceTip[]>(`/stepcard/${id}/device_tips`).then(r => r.data),
  addDeviceTip: (id: number, data: Partial<StepCardDeviceTip>) =>
    api.post<StepCardDeviceTip>(`/stepcard/${id}/device_tips`, data).then(r => r.data),
  updateDeviceTip: (id: number, tipId: number, data: Partial<StepCardDeviceTip>) =>
    api.put<StepCardDeviceTip>(`/stepcard/${id}/device_tips/${tipId}`, data).then(r => r.data),
  deleteDeviceTip: (id: number, tipId: number) =>
    api.delete(`/stepcard/${id}/device_tips/${tipId}`).then(r => r.data),
  getAdaptation: (id: number, params?: { device_brand?: string; system_version?: string }) =>
    api.get(`/stepcard/${id}/adaptation`, { params: params || {} }).then(r => r.data)
}

export const practiceApi = {
  list: (params?: { step_card_id?: number; practitioner_id?: number; status?: string }) =>
    api.get<PracticeRecord[]>('/practice/', { params }).then(r => r.data),
  get: (id: number) => api.get<PracticeRecord>(`/practice/${id}`).then(r => r.data),
  create: (data: { step_card_id: number; practitioner_id?: number; source?: string }) =>
    api.post<PracticeRecord>('/practice/', data).then(r => r.data),
  addStepFeedback: (id: number, data: {
    step_card_step_id: number
    step_number: number
    status: 'completed' | 'cannot_understand' | 'cannot_find'
    feedback?: string
  }) =>
    api.post<PracticeStepFeedback>(`/practice/${id}/step_feedback`, data).then(r => r.data),
  complete: (id: number, data: {
    feedback?: string
    is_independent?: boolean
    stuck_step_number?: number
  }) =>
    api.post<PracticeRecord>(`/practice/${id}/complete`, data).then(r => r.data),
  convertToHelp: (id: number, data?: { description?: string }) =>
    api.post<PracticeRecord>(`/practice/${id}/convert_to_help`, data || {}).then(r => r.data)
}

export const statsApi = {
  overview: () => api.get<StatsOverview>('/stats/overview').then(r => r.data),
  timeline: () => api.get<{ date: string; count: number }[]>('/stats/timeline').then(r => r.data),
  practice: () => api.get<PracticeStats>('/stats/practice').then(r => r.data),
  device: () => api.get<DeviceStats>('/stats/device').then(r => r.data)
}

export const deviceApi = {
  listProfiles: () => api.get<DeviceProfile[]>('/device/profiles').then(r => r.data),
  getProfile: (id: number) => api.get<DeviceProfile>(`/device/profiles/${id}`).then(r => r.data),
  getProfileByUser: (userId: number) => api.get<DeviceProfile | null>(`/device/profiles/user/${userId}`).then(r => r.data),
  createProfile: (data: Partial<DeviceProfile>) =>
    api.post<DeviceProfile>('/device/profiles', data).then(r => r.data),
  updateProfile: (id: number, data: Partial<DeviceProfile>) =>
    api.put<DeviceProfile>(`/device/profiles/${id}`, data).then(r => r.data),
  supplementProfile: (id: number, data: Partial<DeviceProfile>) =>
    api.post<DeviceProfile>(`/device/profiles/${id}/supplement`, data).then(r => r.data)
}
