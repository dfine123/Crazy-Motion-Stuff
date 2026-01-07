"use client";

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import Link from "next/link";
import { Upload, Music, Trash2, Clock, Edit } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import api from "@/lib/api";
import { formatDuration, formatDate } from "@/lib/utils";

export default function AudioPage() {
  const [uploadOpen, setUploadOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [newAudioName, setNewAudioName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  const { data: audioTracks, isLoading } = useQuery({
    queryKey: ["audio"],
    queryFn: () => api.listAudioTracks(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteAudioTrack(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audio"] });
      setDeleteId(null);
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setNewAudioName(acceptedFiles[0].name.replace(/\.[^/.]+$/, ""));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "audio/*": [".mp3", ".wav", ".m4a", ".aac"],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!selectedFile || !newAudioName) return;

    setUploading(true);
    try {
      await api.uploadAudio(selectedFile, newAudioName);
      queryClient.invalidateQueries({ queryKey: ["audio"] });
      setUploadOpen(false);
      setSelectedFile(null);
      setNewAudioName("");
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Audio Library</h1>
          <p className="mt-2 text-gray-600">
            Manage audio tracks with beat timestamps and mood context.
          </p>
        </div>
        <Button onClick={() => setUploadOpen(true)}>
          <Upload className="mr-2 h-4 w-4" />
          Upload Audio
        </Button>
      </div>

      {/* Audio List */}
      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : audioTracks?.audio_tracks && audioTracks.audio_tracks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {audioTracks.audio_tracks.map((audio) => (
            <Card key={audio.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Music className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{audio.name}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="h-3 w-3 text-gray-400" />
                        <span className="text-sm text-gray-500">
                          {formatDuration(audio.duration_ms)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Link href={`/audio/${audio.id}/beats`}>
                      <Button variant="ghost" size="icon">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(audio.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {audio.context.mood && (
                    <Badge variant="secondary">{audio.context.mood}</Badge>
                  )}
                  {audio.context.trend_type && (
                    <Badge variant="outline">{audio.context.trend_type}</Badge>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Beat Timestamps</span>
                    <Badge
                      variant={
                        audio.beat_timestamps.length > 0 ? "success" : "secondary"
                      }
                    >
                      {audio.beat_timestamps.length} marked
                    </Badge>
                  </div>

                  {audio.pacing_guide && (
                    <p className="text-xs text-gray-500 line-clamp-2">
                      {audio.pacing_guide}
                    </p>
                  )}

                  <p className="text-xs text-gray-400">
                    Added {formatDate(audio.created_at)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Music className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No audio tracks uploaded yet</p>
            <Button onClick={() => setUploadOpen(true)}>Upload Your First Track</Button>
          </CardContent>
        </Card>
      )}

      {/* Upload Dialog */}
      <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Audio Track</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400"
              }`}
            >
              <input {...getInputProps()} />
              {selectedFile ? (
                <div>
                  <Music className="h-8 w-8 text-green-500 mx-auto mb-2" />
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p>Drop an audio file here or click to browse</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Supports MP3, WAV, M4A, AAC
                  </p>
                </div>
              )}
            </div>

            {selectedFile && (
              <div className="space-y-2">
                <Label htmlFor="name">Track Name</Label>
                <Input
                  id="name"
                  value={newAudioName}
                  onChange={(e) => setNewAudioName(e.target.value)}
                  placeholder="Enter track name"
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setUploadOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || !newAudioName || uploading}
            >
              {uploading ? "Uploading..." : "Upload"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Audio Track</DialogTitle>
          </DialogHeader>
          <p className="text-gray-600">
            Are you sure you want to delete this audio track? This action cannot be
            undone.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteId && deleteMutation.mutate(deleteId)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
