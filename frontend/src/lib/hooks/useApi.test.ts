/* Testy pomocnika useApi (WP-1) — czysta logika isEmptyResult (bez DOM). */
import { describe, it, expect } from 'vitest'
import { isEmptyResult } from './useApi'

describe('isEmptyResult', () => {
  it('traktuje null / undefined jako puste', () => {
    expect(isEmptyResult(null)).toBe(true)
    expect(isEmptyResult(undefined)).toBe(true)
  })

  it('pusta tablica jest pusta, niepusta nie', () => {
    expect(isEmptyResult([])).toBe(true)
    expect(isEmptyResult([1])).toBe(false)
  })

  it('pusty obiekt jest pusty, z kluczami nie', () => {
    expect(isEmptyResult({})).toBe(true)
    expect(isEmptyResult({ a: 1 })).toBe(false)
  })

  it('wartości prymitywne nie są puste', () => {
    expect(isEmptyResult(0)).toBe(false)
    expect(isEmptyResult('')).toBe(false)
    expect(isEmptyResult(false)).toBe(false)
  })
})
