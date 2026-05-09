import { getPublicApiKey } from '@/lib/config/publicEnv';

export function apiHeaders(): HeadersInit {
  return {
    'X-API-Key': getPublicApiKey(),
  };
}
