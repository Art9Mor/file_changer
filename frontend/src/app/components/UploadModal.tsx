'use client';

import { FormEvent, useState } from 'react';
import { Button, Form, Modal } from 'react-bootstrap';
import { uploadFile } from '@/lib/api/filesClient';

interface UploadModalProps {
  show: boolean;
  onHide: () => void;
  onUpload: () => void;
}

export default function UploadModal({ show, onHide, onUpload }: UploadModalProps) {
  const [title, setTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      setErrorMessage('Укажите название и выберите файл');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await uploadFile(title.trim(), selectedFile);
      onHide();
      setTitle('');
      setSelectedFile(null);
      onUpload();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Произошла ошибка');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal show={show} onHide={onHide} centered>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например, Договор с подрядчиком"
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(event) =>
                setSelectedFile((event.target as HTMLInputElement).files?.[0] ?? null)
              }
            />
          </Form.Group>
          {errorMessage && (
            <div className="mt-3 text-danger">{errorMessage}</div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? 'Загрузка...' : 'Сохранить'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}