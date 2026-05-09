const API_BASE = 'http://localhost:8000';

export interface FileItem {
  id: string;
  title: string;
  original_name: string;
  mime_type: string;
  size: number;
  processing_status: string;
  scan_status: string | null;
  scan_details: string | null;
  metadata_json: Record<string, unknown> | null;
  requires_attention: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertItem {
  id: number;
  file_id: string;
  level: string;
  message: string;
  created_at: string;
}

export async function fetchFiles(): Promise<FileItem[]> {
  const response = await fetch(`${API_BASE}/files`, { cache: 'no-store' });
  if (!response.ok) throw new Error('Failed to fetch files');
  return response.json();
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  const response = await fetch(`${API_BASE}/alerts`, { cache: 'no-store' });
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json();
}

export async function uploadFile(title: string, file: File): Promise<FileItem> {
  const formData = new FormData();
  formData.append('title', title);
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/files`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) throw new Error('Failed to upload file');
  return response.json();
}