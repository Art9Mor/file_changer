import { getPublicApiBaseUrl } from '@/lib/config/publicEnv';
import { apiHeaders } from '@/lib/api/http';
import type { AlertItem, PaginatedResponse } from '@/lib/api/types';

const base = () => getPublicApiBaseUrl();

export async function fetchAlerts(
  skip: number = 0,
  limit: number = 20,
): Promise<PaginatedResponse<AlertItem>> {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  const response = await fetch(`${base()}/alerts?${params}`, {
    cache: 'no-store',
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json();
}
