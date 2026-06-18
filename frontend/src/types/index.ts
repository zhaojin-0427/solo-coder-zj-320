export interface User {
  id: number
  name: string
  role: string
  avatar?: string
  phone?: string
}

export interface GuidanceRecord {
  id: number
  help_request_id: number
  step_number: number
  content: string
  tip?: string
  image_url?: string
  created_at?: string
}

export interface HelpRequest {
  id: number
  title: string
  problem_type: string
  description?: string
  image_url?: string
  audio_url?: string
  device_brand?: string
  system_version?: string
  status: 'pending' | 'resolved'
  requester_id?: number
  helper_id?: number
  step_card_id?: number
  requester?: User
  helper?: User
  created_at?: string
  resolved_at?: string
  resolution_duration?: number
  is_independent: boolean
  is_repeat: boolean
  guidance_records: GuidanceRecord[]
}

export interface StepCardStep {
  id: number
  step_card_id: number
  step_number: number
  content: string
  tip?: string
  image_url?: string
}

export interface StepCard {
  id: number
  title: string
  problem_type: string
  difficulty: 'easy' | 'normal' | 'hard'
  device_brand?: string
  system_version?: string
  description?: string
  usage_count: number
  created_by?: number
  created_at?: string
  updated_at?: string
  steps: StepCardStep[]
}

export interface StatsOverview {
  total_requests: number
  resolved_count: number
  pending_count: number
  total_stepcards: number
  problem_types: { type: string; count: number }[]
  average_duration_minutes: number
  repeat_rate_percent: number
  independent_rate_percent: number
}

export const PROBLEM_TYPES = [
  '看不清字',
  '找不到入口',
  '误触广告',
  '不会切换网络',
  '支付设置',
  '声音太小',
  '不会拍照',
  '其他问题'
] as const

export const DEVICE_BRANDS = ['华为', '苹果', '小米', 'OPPO', 'vivo', '三星', '其他']

export const SYSTEM_VERSIONS = [
  'HarmonyOS 3',
  'HarmonyOS 4',
  'iOS 15',
  'iOS 16',
  'iOS 17',
  'MIUI 14',
  'ColorOS 13',
  'OriginOS 4',
  '其他'
]
