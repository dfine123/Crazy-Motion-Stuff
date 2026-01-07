"use client";

import { useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import Link from "next/link";
import { ArrowLeft, Upload, Film, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import api from "@/lib/api";

interface UploadedFile {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  clipId?: string;
  error?: string;
}

export default function UploadClipsPage() {
  const searchParams = useSearchParams();
  const initialCreator = searchParams.get("creator") || "";

  const [selectedCreator, setSelectedCreator] = useState(initialCreator);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [analyzeWithTwelveLabs, setAnalyzeWithTwelveLabs] = useState(true);
  const queryClient = useQueryClient();

  const { data: creators } = useQuery({
    queryKey: ["creators"],
    queryFn: () => api.listCreators(),
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      status: "pending" as const,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".mov", ".avi", ".webm"],
    },
    multiple: true,
  });

  const uploadFiles = async () => {
    if (!selectedCreator || files.length === 0) return;

    setUploading(true);

    for (let i = 0; i < files.length; i++) {
      const uploadedFile = files[i];
      if (uploadedFile.status !== "pending") continue;

      // Update status to uploading
      setFiles((prev) =>
        prev.map((f, idx) =>
          idx === i ? { ...f, status: "uploading" as const } : f
        )
      );

      try {
        const result = await api.uploadClip(
          uploadedFile.file,
          selectedCreator,
          {},
          analyzeWithTwelveLabs
        );

        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? { ...f, status: "success" as const, clipId: result.clip_id }
              : f
          )
        );
      } catch (error) {
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? {
                  ...f,
                  status: "error" as const,
                  error: error instanceof Error ? error.message : "Upload failed",
                }
              : f
          )
        );
      }
    }

    setUploading(false);
    queryClient.invalidateQueries({ queryKey: ["clips"] });
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearCompleted = () => {
    setFiles((prev) => prev.filter((f) => f.status !== "success"));
  };

  const pendingCount = files.filter((f) => f.status === "pending").length;
  const successCount = files.filter((f) => f.status === "success").length;
  const errorCount = files.filter((f) => f.status === "error").length;

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link
          href="/clips"
          className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Clips
        </Link>

        <h1 className="text-3xl font-bold text-gray-900">Upload Clips</h1>
        <p className="mt-2 text-gray-600">
          Upload video clips to a creator's library. Optionally enable Twelve Labs
          analysis for automatic metadata generation.
        </p>
      </div>

      <div className="max-w-3xl space-y-6">
        {/* Creator Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Select Creator</CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={selectedCreator} onValueChange={setSelectedCreator}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a creator" />
              </SelectTrigger>
              <SelectContent>
                {creators?.creators.map((creator) => (
                  <SelectItem key={creator.id} value={creator.id}>
                    {creator.name}
                    {creator.handle && ` (@${creator.handle})`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {!selectedCreator && (
              <p className="text-sm text-gray-500 mt-2">
                Please select a creator before uploading clips.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Dropzone */}
        <Card>
          <CardContent className="p-6">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400"
              } ${!selectedCreator ? "opacity-50 pointer-events-none" : ""}`}
            >
              <input {...getInputProps()} disabled={!selectedCreator} />
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium">
                Drop video files here or click to browse
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Supports MP4, MOV, AVI, WebM
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Options */}
        {files.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Upload Options</CardTitle>
            </CardHeader>
            <CardContent>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={analyzeWithTwelveLabs}
                  onChange={(e) => setAnalyzeWithTwelveLabs(e.target.checked)}
                  className="rounded"
                />
                <div>
                  <p className="font-medium">Analyze with Twelve Labs</p>
                  <p className="text-sm text-gray-500">
                    Automatically generate metadata using AI video analysis
                  </p>
                </div>
              </label>
            </CardContent>
          </Card>
        )}

        {/* File List */}
        {files.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  Files ({files.length})
                  {successCount > 0 && (
                    <span className="text-green-600 ml-2">
                      {successCount} uploaded
                    </span>
                  )}
                  {errorCount > 0 && (
                    <span className="text-red-600 ml-2">{errorCount} failed</span>
                  )}
                </CardTitle>
                {successCount > 0 && (
                  <Button variant="ghost" size="sm" onClick={clearCompleted}>
                    Clear Completed
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {files.map((uploadedFile, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
                  >
                    <Film className="h-8 w-8 text-gray-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">
                        {uploadedFile.file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      {uploadedFile.error && (
                        <p className="text-sm text-red-500">{uploadedFile.error}</p>
                      )}
                    </div>
                    <div className="flex-shrink-0">
                      {uploadedFile.status === "pending" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                        >
                          Remove
                        </Button>
                      )}
                      {uploadedFile.status === "uploading" && (
                        <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
                      )}
                      {uploadedFile.status === "success" && (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                      {uploadedFile.status === "error" && (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setFiles([])}
                  disabled={uploading}
                >
                  Clear All
                </Button>
                <Button
                  onClick={uploadFiles}
                  disabled={!selectedCreator || pendingCount === 0 || uploading}
                >
                  {uploading
                    ? "Uploading..."
                    : `Upload ${pendingCount} File${pendingCount !== 1 ? "s" : ""}`}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
