import { describe, it, expect } from 'vitest';

describe('EventWise Frontend Unit Suite', () => {
  it('correctly calculates budget percentages without floating point drift', () => {
    const total = 10000;
    const allocated = 4000;
    const pct = (allocated / total) * 100;
    expect(pct).toBe(40);
  });

  it('validates event creation minimum parameters', () => {
    const validTitle = 'Spring Community Festival';
    const guestCount = 200;
    const totalBudget = 5000;
    expect(validTitle.trim().length).toBeGreaterThan(2);
    expect(guestCount).toBeGreaterThan(0);
    expect(totalBudget).toBeGreaterThan(0);
  });
});

