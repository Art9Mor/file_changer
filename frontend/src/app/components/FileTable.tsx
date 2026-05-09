'use client';

import { useState } from 'react';
import { Badge, Button, Table } from 'react-bootstrap';
import { downloadFile } from '@/lib/api/filesClient';
import type { FileItem } from '@/lib/api/types';

interface FileTableProps {
  files: FileItem[];
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatSize(size: number) {
  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function getProcessingVariant(status: string) {
  if (status === 'failed') {
    return 'danger';
  }

  if (status === 'processing') {
    return 'warning';
  }

  if (status === 'processed') {
    return 'success';
  }

  return 'secondary';
}

export default function FileTable({ files }: FileTableProps) {
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  async function handleDownload(file: FileItem) {
    setDownloadingId(file.id);
    try {
      await downloadFile(file.id, file.original_name);
    } catch {
      window.alert('Не удалось скачать файл. Проверьте API и ключ.');
    } finally {
      setDownloadingId(null);
    }
  }

  return (
    <div className="table-responsive">
      <Table hover bordered className="align-middle mb-0">
        <thead className="table-light">
          <tr>
            <th>Название</th>
            <th>Файл</th>
            <th>MIME</th>
            <th>Размер</th>
            <th>Статус</th>
            <th>Проверка</th>
            <th>Создан</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {files.length === 0 ? (
            <tr>
              <td colSpan={8} className="text-center py-4 text-secondary">
                Файлы пока не загружены
              </td>
            </tr>
          ) : (
            files.map((file) => (
              <tr key={file.id}>
                <td>
                  <div className="fw-semibold">{file.title}</div>
                  <div className="small text-secondary">{file.id}</div>
                </td>
                <td>{file.original_name}</td>
                <td>{file.mime_type}</td>
                <td>{formatSize(file.size)}</td>
                <td>
                  <Badge bg={getProcessingVariant(file.processing_status)}>
                    {file.processing_status}
                  </Badge>
                </td>
                <td>
                  <div className="d-flex flex-column gap-1">
                    <Badge bg={file.requires_attention ? 'warning' : 'success'}>
                      {file.scan_status ?? 'pending'}
                    </Badge>
                    <span className="small text-secondary">
                      {file.scan_details ?? 'Ожидает обработки'}
                    </span>
                  </div>
                </td>
                <td>{formatDate(file.created_at)}</td>
                <td className="text-nowrap">
                  <Button
                    type="button"
                    variant="outline-primary"
                    size="sm"
                    disabled={downloadingId === file.id}
                    onClick={() => void handleDownload(file)}
                  >
                    {downloadingId === file.id ? '…' : 'Скачать'}
                  </Button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}
