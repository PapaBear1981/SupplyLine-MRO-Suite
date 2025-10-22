import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.K6_BASE_URL || 'https://api.example.com';
const DRY_RUN = __ENV.K6_DRY_RUN === "1";
const TOKEN = __ENV.K6_TOKEN || 'test-token';

export const options = {
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{endpoint:/checkout}': ['p(95)<300'],
  },
  stages: [
    { duration: '2m', target: 20 },
    { duration: '2m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '1m', target: 0 },
  ],
  gracefulStop: '30s',
};

export default function () {
  if (DRY_RUN) {
    sleep(0.1);
    return;
  }
  const payload = JSON.stringify({
    toolId: 'TL-100',
    userId: 'u-tech',
    workOrder: `WO-${__ITER % 1000}`,
  });
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${TOKEN}`,
  };
  const res = http.post(`${BASE_URL}/checkout`, payload, { headers, tags: { endpoint: '/checkout' } });
  check(res, {
    'status is acceptable': (r) => [200, 400, 409].includes(r.status),
  });
  sleep(0.5);
}
