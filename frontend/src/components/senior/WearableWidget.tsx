import { Heart, Droplet, Footprints, Moon, BatteryMedium, Watch, Lock } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { WearableInfo } from '@/types/domain'
import { Badge } from '@/components/ui/Badge'

export interface WearableWidgetProps {
  device: WearableInfo
  showLive?: boolean
  /** Panel Opiekuna: thresholds READ ONLY. */
  readOnlyThresholds?: boolean
  className?: string
}

const BRAND_LABEL: Record<WearableInfo['brand'], string> = {
  xiaomi: 'Xiaomi',
  apple: 'Apple',
  garmin: 'Garmin',
  fitbit: 'Fitbit',
}

const SYNC_TONE = {
  ok: 'green',
  delayed: 'gold',
  offline: 'red',
} as const

const SYNC_LABEL = {
  ok: 'Zsynchronizowany',
  delayed: 'Opóźniony',
  offline: 'Offline',
} as const

function Vital({ icon, label, value, unit }: { icon: React.ReactNode; label: string; value: number; unit: string }) {
  return (
    <div className="flex flex-col items-center gap-1 py-3">
      <span className="text-ink-400">{icon}</span>
      <span className="kpi text-h4 text-granat-800">{value}</span>
      <span className="text-caption text-ink-500 uppercase tracking-wide">{label}</span>
      <span className="text-caption text-ink-400">{unit}</span>
    </div>
  )
}

export function WearableWidget({ device, showLive = false, readOnlyThresholds = true, className }: WearableWidgetProps) {
  const { vitals, thresholds, calibration } = device

  return (
    <div className={cn('adam-card overflow-hidden', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 bg-granat-50 border-b border-line">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-white flex items-center justify-center text-granat-700 border border-line">
            <Watch size={18} />
          </div>
          <div>
            <h3 className="text-body font-medium text-granat-900">
              {BRAND_LABEL[device.brand]} {device.model}
            </h3>
            <p className="text-caption text-ink-500">
              Sparowano {new Date(device.pairedAt).toLocaleDateString('pl-PL')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {showLive && (
            <span className="inline-flex items-center gap-1 text-caption text-sem-green">
              <span className="w-1.5 h-1.5 rounded-full bg-sem-green animate-sem-dot-pulse" /> LIVE
            </span>
          )}
          <Badge tone={SYNC_TONE[device.syncStatus]}>{SYNC_LABEL[device.syncStatus]}</Badge>
        </div>
      </div>

      {/* Vitals grid */}
      <div className="grid grid-cols-4 divide-x divide-line">
        <Vital icon={<Heart size={18} />} label="Tętno" value={vitals.heartRate} unit="bpm" />
        <Vital icon={<Droplet size={18} />} label="SpO₂" value={vitals.spo2} unit="%" />
        <Vital icon={<Footprints size={18} />} label="Kroki" value={vitals.stepsToday} unit="dziś" />
        <Vital icon={<Moon size={18} />} label="Sen" value={vitals.sleepLastNight.score} unit="pkt" />
      </div>

      {/* Footer: battery + thresholds */}
      <div className="px-5 py-3 border-t border-line flex items-center justify-between text-label text-ink-500">
        <span className="inline-flex items-center gap-1.5">
          <BatteryMedium size={14} /> {device.batteryPct}%
        </span>
        {calibration.status === 'calibrating' ? (
          <Badge tone="gold">Kalibracja {calibration.day}/{calibration.totalDays ?? 14} dni</Badge>
        ) : (
          <Badge tone="green">Kalibracja stabilna</Badge>
        )}
      </div>

      {/* Thresholds — READ ONLY in Panel Opiekuna */}
      <div className="px-5 py-3 border-t border-line bg-paper-2">
        <div className="flex items-center justify-between mb-2">
          <span className="eyebrow">Progi alarmowe</span>
          {readOnlyThresholds && (
            <span className="inline-flex items-center gap-1 text-caption text-ink-400">
              <Lock size={11} /> tylko odczyt
            </span>
          )}
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-label text-ink-700">
          <span>Tętno: {thresholds.hrLow}–{thresholds.hrHigh} bpm</span>
          <span>SpO₂ min: {thresholds.spo2Low}%</span>
          <span className="text-ink-400">
            {thresholds.mode === 'auto' ? 'tryb auto' : `override: ${thresholds.overriddenBy?.userName ?? '—'}`}
          </span>
        </div>
      </div>
    </div>
  )
}
