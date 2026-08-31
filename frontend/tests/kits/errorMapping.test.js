import { describe, expect, it } from 'vitest';

import { determineErrorType, ERROR_TYPES, getErrorInfo } from '../../src/utils/errorMapping';

describe('errorMapping', () => {
  it('handles missing and malformed errors without throwing', () => {
    expect(determineErrorType(null)).toBe(ERROR_TYPES.UNKNOWN_ERROR);
    expect(determineErrorType({ response: { status: '503' } })).toBe(ERROR_TYPES.SERVER_ERROR);
  });

  it('classifies actionable transport failures', () => {
    expect(determineErrorType({ code: 'ETIMEDOUT' })).toBe(ERROR_TYPES.TIMEOUT_ERROR);
    expect(determineErrorType({ code: 'ERR_NETWORK' })).toBe(ERROR_TYPES.NETWORK_ERROR);
    expect(determineErrorType(new Error('cors policy blocked the request'))).toBe(ERROR_TYPES.CORS_ERROR);
  });

  it('carries the safe API contract and support reference into display data', () => {
    const info = getErrorInfo({
      response: {
        status: 409,
        data: {
          error: 'This record changed while you were editing it.',
          hint: 'Refresh and review the latest values.',
          reference: 'ABC123'
        }
      }
    });

    expect(info.user).toBe('This record changed while you were editing it.');
    expect(info.action).toBe('Refresh and review the latest values.');
    expect(info.reference).toBe('ABC123');
  });

  it('rejects unbounded server messages from the UI', () => {
    const info = getErrorInfo({
      response: { status: 500, data: { error: 'x'.repeat(501) } }
    });

    expect(info.user).toBe("Something went wrong on our end. We're working to fix it.");
  });
});
