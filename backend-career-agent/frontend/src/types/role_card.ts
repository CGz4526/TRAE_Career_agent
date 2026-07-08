/**
 * 角色卡类型定义
 */
export interface RoleCard {
  id: string
  card_type: 'preset' | 'custom'
  role_name: string
  icon: string
  description: string
  company?: string
  tech_stack: string[]
  core_skills: string[]
  soft_skills: string[]
  experience_years: string
  education: string
  interview_directions: string[]
  question_categories: { name: string; weight: number }[]
  difficulty_profile: string
  jd_summary?: string
  source_jd_id?: string
  source_company?: string
  is_active?: boolean
  created_at?: string
}

/**
 * 角色卡图标映射
 */
export const ROLE_ICONS: Record<string, string> = {
  java: '☕',
  python: '🐍',
  go: '🔷',
  fullstack: '🔄',
  bigdata: '📊',
  algorithm: '🧮',
  devops: '⚙️',
  frontend: '🎨',
  agent: '🤖',
  default: '💼'
}

/**
 * 获取角色卡图标
 */
export function getRoleIcon(icon: string): string {
  return ROLE_ICONS[icon] || ROLE_ICONS.default
}

/**
 * 角色卡分类颜色 - 黑白灰系列
 */
export const ROLE_COLORS: Record<string, string> = {
  java: '#52525b',
  python: '#71717a',
  go: '#a1a1aa',
  fullstack: '#3f3f46',
  bigdata: '#52525b',
  algorithm: '#71717a',
  devops: '#a1a1aa',
  frontend: '#3f3f46',
  agent: '#52525b',
  default: '#52525b'
}

/**
 * 获取角色卡颜色
 */
export function getRoleColor(icon: string): string {
  return ROLE_COLORS[icon] || ROLE_COLORS.default
}
