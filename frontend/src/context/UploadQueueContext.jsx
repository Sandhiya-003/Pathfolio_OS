import { createContext, useCallback, useContext, useState } from "react";
import { api } from "../lib/api";
import { useToast } from "./ToastContext";

const UploadQueueContext = createContext(null);

const ACCEPTED = [".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"];
let uid = 0;

export function UploadQueueProvider({ children }) {
  const toast = useToast();
  // { id, file, status: pending|uploading|done|error, progress, result, error }
  const [queue, setQueue] = useState([]);

  const updateItem = useCallback((id, patch) => {
    setQueue((prev) => prev.map((it) => (it.id === id ? { ...it, ...patch } : it)));
  }, []);

  const processItem = useCallback(
    async (item) => {
      updateItem(item.id, { status: "uploading", progress: 5 });
      try {
        const result = await api.uploadSingle(item.file, (pct) =>
          updateItem(item.id, { progress: pct })
        );
        if (result.success === false) {
          updateItem(item.id, { status: "error", error: result.message || "Could not process file" });
          return;
        }
        updateItem(item.id, { status: "done", progress: 100, result });
      } catch (e) {
        updateItem(item.id, { status: "error", error: e.message || "Upload failed" });
      }
    },
    [updateItem]
  );

  const addFiles = useCallback(
    (fileList) => {
      const files = Array.from(fileList);
      const valid = [];
      const rejected = [];

      files.forEach((file) => {
        const ext = "." + file.name.split(".").pop().toLowerCase();
        if (ACCEPTED.includes(ext)) {
          valid.push(file);
        } else {
          rejected.push(file.name);
        }
      });

      if (rejected.length) {
        toast.error(`Unsupported format: ${rejected.join(", ")}`);
      }
      if (!valid.length) return;

      const items = valid.map((file) => ({
        id: ++uid,
        file,
        status: "pending",
        progress: 0,
        result: null,
        error: null,
      }));

      setQueue((prev) => [...items, ...prev]);
      items.forEach(processItem);
    },
    [processItem, toast]
  );

  const clearItem = useCallback((id) => {
    setQueue((prev) => prev.filter((it) => it.id !== id));
  }, []);

  const inFlightCount = queue.filter((q) => q.status === "uploading" || q.status === "pending").length;

  return (
    <UploadQueueContext.Provider value={{ queue, addFiles, clearItem, inFlightCount }}>
      {children}
    </UploadQueueContext.Provider>
  );
}

export function useUploadQueue() {
  const ctx = useContext(UploadQueueContext);
  if (!ctx) throw new Error("useUploadQueue must be used within UploadQueueProvider");
  return ctx;
}