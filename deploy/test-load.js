import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 }, // Sobe rápido para 100 VUs
    { duration: '2m', target: 200 },  // Mantém 200 VUs por 2 minutos
    { duration: '1m', target: 0 },    // Reduz gradualmente
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'], // Máximo de 1% de falhas permitidas
    http_req_duration: ['p(95)<500'], // 95% das requisições devem ser < 500ms
  },
};

export default function () {
  http.get('http://127.0.0.1:64240/api/health_check'); // Ajuste para a URL correta do serviço
  sleep(0.5); // Reduz tempo de espera para aumentar carga
}
