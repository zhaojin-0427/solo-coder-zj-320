export interface User {
  id: number
  name: string
  role: string
  avatar?: string
  phone?: string
  expertise?: string
  is_online?: boolean
  is_on_duty?: boolean
  last_online_at?: string
  expected_response_minutes?: number
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

export interface HelpStatusLog {
  id: number
  help_request_id: number
  old_status?: string
  new_status?: string
  old_processing_status?: string
  new_processing_status?: string
  operator?: User
  note?: string
  created_at?: string
}

export interface HelpAssignment {
  id: number
  help_request_id: number
  from_helper?: User
  to_helper?: User
  assignment_type: string
  reason?: string
  match_score?: number
  created_at?: string
}

export interface FraudRiskInfo {
  id: number
  help_request_id: number
  scam_type: string
  suspicious_source?: string
  involved_amount: number
  leaked_verification_code: boolean
  leaked_payment_password: boolean
  clicked_link: boolean
  risk_keywords?: string
  custom_description?: string
  created_at?: string
}

export interface RiskDisposal {
  id: number
  help_request_id: number
  disposal_type: '已阻止' | '需报警' | '需冻结支付' | '误报' | '继续观察'
  note?: string
  operator?: User
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
  status: 'pending' | 'assigned' | 'processing' | 'resolved'
  processing_status?: 'phone_guidance' | 'waiting_operation' | 'need_confirm' | 'resolved'
  requester_id?: number
  helper_id?: number
  step_card_id?: number
  device_profile_id?: number
  device_profile?: DeviceProfile
  requester?: User
  helper?: User
  created_at?: string
  assigned_at?: string
  responded_at?: string
  response_duration?: number
  resolved_at?: string
  resolution_duration?: number
  is_independent: boolean
  is_repeat: boolean
  transfer_count: number
  is_timeout: boolean
  is_risk: boolean
  risk_level?: 'high' | 'medium' | 'low'
  risk_info?: FraudRiskInfo
  risk_disposals: RiskDisposal[]
  processing_note?: string
  create_source: 'direct' | 'practice' | 'risk_disposal'
  guidance_records: GuidanceRecord[]
  status_logs: HelpStatusLog[]
  assignments: HelpAssignment[]
  expected_response_minutes?: number
}

export interface FamilyEfficiency {
  family_member: User
  total_count: number
  resolved_count: number
  pending_count: number
  avg_response_minutes: number
  avg_resolution_minutes: number
  transfer_count: number
  timeout_count: number
}

export interface StepCardStep {
  id: number
  step_card_id: number
  step_number: number
  content: string
  tip?: string
  image_url?: string
}

export interface StepCardDeviceTip {
  id: number
  step_card_id: number
  step_number: number
  device_brand: string
  system_version?: string
  adaptation_tip: string
  entry_name?: string
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
  responsible_family_id?: number
  responsible_family?: User
  create_source: 'manual' | 'help_request'
  source_help_request_id?: number
  created_at?: string
  updated_at?: string
  steps: StepCardStep[]
  device_tips: StepCardDeviceTip[]
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
  '防诈骗',
  '其他问题'
] as const

export const SCAM_TYPES = [
  '陌生来电',
  '短信链接',
  '中奖弹窗',
  '要求转账',
  '索要验证码',
  '远程控制'
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

export interface DeviceProfile {
  id: number
  user_id: number
  device_brand?: string
  system_version?: string
  font_size_preference?: string
  simple_mode_enabled: boolean
  common_apps?: string
  network_environment?: string
  difficulty_tags?: string
  updated_at?: string
  user?: User
}

export interface DeviceStats {
  brand_distribution: { brand: string; count: number }[]
  system_distribution: { system: string; count: number }[]
  brand_avg_duration: { brand: string; avg_duration: number }[]
  brand_problem_distribution: { brand: string; problem_type: string; count: number }[]
  top_difficulty_tags: { tag: string; count: number }[]
}

export const FONT_SIZE_OPTIONS = ['标准', '大', '超大'] as const
export const NETWORK_OPTIONS = ['WiFi', '4G', '5G', '不确定'] as const

export interface RiskStats {
  total_risk_requests: number
  scam_type_distribution: { scam_type: string; count: number }[]
  blocked_count: number
  total_involved_amount: number
  avg_response_minutes: number
  top_risk_keywords: { keyword: string; count: number }[]
  disposal_distribution: { disposal_type: string; count: number }[]
  leaked_verification_code_count: number
  leaked_payment_password_count: number
  clicked_link_count: number
}
