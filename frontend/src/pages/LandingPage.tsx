import { LandingNav } from '@/components/landing/LandingNav'
import { Hero } from '@/components/landing/Hero'
import { SignoffStrip } from '@/components/landing/SignoffStrip'
import { ChapterProblem } from '@/components/landing/ChapterProblem'
import { ChapterHowItWorks } from '@/components/landing/ChapterHowItWorks'
import { ChapterFeatures } from '@/components/landing/ChapterFeatures'
import { PartnersSection } from '@/components/landing/PartnersSection'
import { Testimonial } from '@/components/landing/Testimonial'
import { Pricing } from '@/components/landing/Pricing'
import { FinalCTA } from '@/components/landing/FinalCTA'
import { LandingFooter } from '@/components/landing/LandingFooter'

export function LandingPage({
  onLogin,
  onOrder,
}: {
  onLogin?: () => void
  onOrder?: () => void
}) {
  return (
    <div className="bg-paper text-ink-900">
      <LandingNav onLogin={onLogin} onOrder={onOrder} />
      <Hero onOrder={onOrder} />
      <SignoffStrip />
      <ChapterProblem />
      <ChapterHowItWorks />
      <ChapterFeatures />
      <PartnersSection />
      <Testimonial />
      <Pricing onOrder={onOrder} />
      <FinalCTA onOrder={onOrder} />
      <LandingFooter />
    </div>
  )
}
