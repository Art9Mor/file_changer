import { getPublicApiBaseUrl } from '@/lib/config/publicEnv';
import { apiHeaders } from '@/lib/api/http';
import type { FileItem, PaginatedResponse } from '@/lib/api/types';

const base = () => getPublicApiBaseUrl();

export async function fetchFiles(
  skip: number = 0,
  limit: number = 20,
): Promise<PaginatedResponse<FileItem>> {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  const response = await fetch(`${base()}/files?${params}`, {
    cache: 'no-store',
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch files');
  return response.json();
}

export async function uploadFile(title: string, file: File): Promise<FileItem> {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('file', file);

  const response = await fetch(`${base()}/files`, {
    method: 'POST',
    headers: apiHeaders(),
    body: formData,
  });

  if (!response.ok) throw new Error('Failed to upload file');
  return response.json();
}

export async function downloadFile(fileId: string, originalName: string): Promise<void> {
  const response = await fetch(`${base()}/files/${fileId}/download`, {
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Failed to download file');
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = originalName;
  anchor.click();
  URL.revokeObjectURL(url);
}
