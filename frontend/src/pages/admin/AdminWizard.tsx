import { useState } from 'react'
import { Check, ArrowRight, ArrowLeft } from 'lucide-react'
import { AdminPageHead } from '@/components/admin'
import { Card, CardBody, Button } from '@/components/ui'
import { WIZARD_STEPS } from '@/data/mockAdmin'
import { cn } from '@/lib/cn'

export function AdminWizard() {
  const [step, setStep] = useState(0)
  const current = WIZARD_STEPS[step]

  return (
    <>
      <AdminPageHead eyebrow="Overview" title="Setup Wizard" subtitle="Konfiguracja instancji Adama w 5 krokach" />

      {/* Stepper */}
      <div className="flex items-center mb-8 overflow-x-auto">
        {WIZARD_STEPS.map((s, i) => {
          const done = i < step
          const active = i === step
          return (
            <div key={s.id} className="flex items-center shrink-0">
              <div className="flex flex-col items-center">
                <span
                  className={cn(
                    'w-9 h-9 rounded-full flex items-center justify-center text-body font-medium',
                    done ? 'bg-sem-green text-white' : active ? 'bg-granat-700 text-white' : 'bg-paper-3 text-ink-400',
                  )}
                >
                  {done ? <Check size={16} /> : s.id}
                </span>
                <span className={cn('text-caption mt-1 whitespace-nowrap', active ? 'text-granat-900 font-medium' : 'text-ink-400')}>{s.title}</span>
              </div>
              {i < WIZARD_STEPS.length - 1 && <div className={cn('w-16 h-0.5 mx-2 mb-4', done ? 'bg-sem-green' : 'bg-line')} />}
            </div>
          )
        })}
      </div>

      <Card>
        <CardBody>
          <span className="eyebrow">Krok {current.id} z {WIZARD_STEPS.length}</span>
          <h3 className="text-h3 font-serif text-granat-900 mt-1">{current.title}</h3>
          <p className="text-body text-ink-500 mt-2 max-w-2xl">{current.desc}</p>

          <div className="mt-6 rounded-lg border border-dashed border-line bg-paper-2 p-8 text-center text-ink-400 text-body">
            Formularz konfiguracji: <b>{current.title}</b>
          </div>

          <div className="flex justify-between mt-6">
            <Button variant="secondary" disabled={step === 0} onClick={() => setStep((s) => s - 1)}>
              <ArrowLeft size={16} /> Wstecz
            </Button>
            {step < WIZARD_STEPS.length - 1 ? (
              <Button variant="primary" onClick={() => setStep((s) => s + 1)}>
                Dalej <ArrowRight size={16} />
              </Button>
            ) : (
              <Button variant="gold"><Check size={16} /> Zakończ i uruchom</Button>
            )}
          </div>
        </CardBody>
      </Card>
    </>
  )
}
