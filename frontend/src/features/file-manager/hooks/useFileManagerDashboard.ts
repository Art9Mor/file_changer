"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchAlerts } from "@/lib/api/alertsClient";
import { fetchFiles } from "@/lib/api/filesClient";
import type { AlertItem, FileItem } from "@/lib/api/types";

export function useFileManagerDashboard() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [filesTotal, setFilesTotal] = useState(0);
  const [alertsTotal, setAlertsTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesData, alertsData] = await Promise.all([
        fetchFiles(),
        fetchAlerts(),
      ]);

      setFiles(filesData.items);
      setFilesTotal(filesData.total);
      setAlerts(alertsData.items);
      setAlertsTotal(alertsData.total);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return {
    files,
    alerts,
    filesTotal,
    alertsTotal,
    isLoading,
    showModal,
    setShowModal,
    errorMessage,
    loadData,
  };
}
