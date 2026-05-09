/**
 * Публичные переменные окружения (префикс NEXT_PUBLIC_ для браузера).
 */

export function getPublicApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
}

export function getPublicApiKey(): string {
  return process.env.NEXT_PUBLIC_API_KEY ?? 'test-key-dev';
}
