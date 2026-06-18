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

export interface PracticeStepFeedback {
  id: number
  practice_record_id: number
  step_card_step_id: number
  step_number: number
  status: 'completed' | 'cannot_understand' | 'cannot_find'
  feedback?: string
  step_content?: string
  created_at?: string
}

export interface PracticeRecord {
  id: number
  step_card_id: number
  practitioner_id: number
  practitioner?: User
  source: 'library' | 'help_success'
  status: 'in_progress' | 'completed' | 'converted'
  is_independent: boolean
  stuck_step_number?: number
  feedback?: string
  converted_to_help: boolean
  help_request_id?: number
  step_card?: StepCard
  step_feedbacks: PracticeStepFeedback[]
  created_at?: string
  completed_at?: string
}

export interface CardPracticeStats {
  step_card_id: number
  total_practice_count: number
  recent_practice_count: number
  completion_count: number
  completion_rate_percent: number
  most_stuck_step?: { step_number: number; stuck_count: number }
  stuck_steps_detail: { step_number: number; stuck_count: number }[]
  needs_optimization: boolean
  independent_count: number
  converted_to_help_count: number
}

export interface PracticeStats {
  total_practices: number
  completed_practices: number
  completion_rate_percent: number
  converted_to_help_count: number
  top_stuck_steps: { step_number: number; card_title: string; stuck_count: number }[]
  top_practiced_cards: { id: number; title: string; practice_count: number }[]
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
