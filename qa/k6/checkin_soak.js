import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.K6_BASE_URL || 'https://api.example.com';
const DRY_RUN = __ENV.K6_DRY_RUN === "1";
const TOKEN = __ENV.K6_TOKEN || 'test-token';

export const options = {
  vus: 50,
  duration: '30m',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{endpoint:/checkout}': ['p(95)<300'],
  },
};

export default function () {
  if (DRY_RUN) {
    sleep(0.1);
    return;
  }
  const payload = JSON.stringify({
    toolId: 'TL-100',
    userId: 'u-tech',
    workOrder: `WO-${__ITER % 10000}`,
  });
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${TOKEN}`,
  };
  const res = http.post(`${BASE_URL}/checkout`, payload, { headers, tags: { endpoint: '/checkout' } });
  check(res, {
    'status ok': (r) => [200, 400, 409].includes(r.status),
  });
  sleep(1);
}

export function handleSummary(data) {
  return {
    'artifacts/k6/checkin_soak_summary.json': JSON.stringify(data, null, 2),
  };
}
