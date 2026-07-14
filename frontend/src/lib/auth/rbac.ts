/* ============================================================
   ADAM · RBAC
   Role → permission map. Panel Admina requires 'admin';
   Panel Opiekuna is available to caregiver + family_member.
   ============================================================ */

import type { Role } from '@/types/domain'

export type Permission =
  | 'panel:caregiver'
  | 'panel:admin'
  | 'senior:view'
  | 'senior:call'
  | 'order:create'
  | 'order:cancel'
  | 'wearable:threshold:edit' // coordinator/doctor only — NOT caregiver
  | 'family:invite' // caregiver/admin — NOT family_member
  | 'admin:users:manage'
  | 'admin:marketplace:manage'
  | 'admin:reports:view'
  | 'admin:fleet:manage'

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  admin: [
    'panel:caregiver',
    'panel:admin',
    'senior:view',
    'senior:call',
    'order:create',
    'order:cancel',
    'wearable:threshold:edit',
    'family:invite',
    'admin:users:manage',
    'admin:marketplace:manage',
    'admin:reports:view',
    'admin:fleet:manage',
  ],
  caregiver: ['panel:caregiver', 'senior:view', 'senior:call', 'order:create', 'order:cancel', 'family:invite'],
  family_member: ['panel:caregiver', 'senior:view', 'senior:call', 'order:create'],
}

export function can(role: Role | undefined, permission: Permission): boolean {
  if (!role) return false
  return ROLE_PERMISSIONS[role].includes(permission)
}

export const ROLE_LABEL: Record<Role, string> = {
  admin: 'Administrator',
  caregiver: 'Opiekun',
  family_member: 'Członek rodziny',
}
