"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Wand2, Play, Loader2, Download, RefreshCw, Copy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import api from "@/lib/api";
import { formatDateTime, getStatusColor } from "@/lib/utils";

export default function GeneratePage() {
  const searchParams = useSearchParams();
  const initialCreator = searchParams.get("creator") || "";

  const [selectedCreator, setSelectedCreator] = useState(initialCreator);
  const [selectedAudio, setSelectedAudio] = useState("");
  const [currentGeneration, setCurrentGeneration] = useState<string | null>(null);
  const [captionOptions, setCaptionOptions] = useState<
    Array<{ caption: string; hook_type: string; length: number }>
  >([]);
  const [captionDialogOpen, setCaptionDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: creators } = useQuery({
    queryKey: ["creators"],
    queryFn: () => api.listCreators(),
  });

  const { data: audioTracks } = useQuery({
    queryKey: ["audio"],
    queryFn: () => api.listAudioTracks({ is_active: true }),
  });

  const { data: generations, refetch: refetchGenerations } = useQuery({
    queryKey: ["generations", selectedCreator],
    queryFn: () =>
      api.listGenerations({
        creator_id: selectedCreator || undefined,
        limit: 10,
      }),
    refetchInterval: currentGeneration ? 3000 : false,
  });

  const { data: generationDetail } = useQuery({
    queryKey: ["generation", currentGeneration],
    queryFn: () => (currentGeneration ? api.getGeneration(currentGeneration) : null),
    enabled: !!currentGeneration,
    refetchInterval: (query) =>
      query.state.data?.status === "pending" || query.state.data?.status === "processing" ? 2000 : false,
  });

  const generateMutation = useMutation({
    mutationFn: () =>
      api.createGeneration({
        creator_id: selectedCreator,
        audio_id: selectedAudio,
      }),
    onSuccess: (data) => {
      setCurrentGeneration(data.id);
      queryClient.invalidateQueries({ queryKey: ["generations"] });
    },
  });

  const regenerateCaptionMutation = useMutation({
    mutationFn: (id: string) => api.regenerateCaption(id),
    onSuccess: (data) => {
      setCaptionOptions(data.caption_options);
      setCaptionDialogOpen(true);
    },
  });

  const updateCaptionMutation = useMutation({
    mutationFn: ({ id, caption }: { id: string; caption: string }) =>
      api.updateGenerationCaption(id, caption),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation", currentGeneration] });
      setCaptionDialogOpen(false);
    },
  });

  // Auto-select creator from URL param
  useEffect(() => {
    if (initialCreator) {
      setSelectedCreator(initialCreator);
    }
  }, [initialCreator]);

  const selectedCreatorData = creators?.creators.find(
    (c) => c.id === selectedCreator
  );
  const selectedAudioData = audioTracks?.audio_tracks.find(
    (a) => a.id === selectedAudio
  );

  const canGenerate =
    selectedCreator && selectedAudio && !generateMutation.isPending;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Generate Video</h1>
        <p className="mt-2 text-gray-600">
          Select a creator and audio track to generate a new video.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Generation Form */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>New Generation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Creator Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Creator</label>
                <Select value={selectedCreator} onValueChange={setSelectedCreator}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a creator" />
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
                {selectedCreatorData && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {selectedCreatorData.brand_profile.lifestyle_themes
                      ?.slice(0, 4)
                      .map((theme) => (
                        <Badge key={theme} variant="secondary" className="text-xs">
                          {theme}
                        </Badge>
                      ))}
                  </div>
                )}
              </div>

              {/* Audio Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Audio Track</label>
                <Select value={selectedAudio} onValueChange={setSelectedAudio}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select an audio track" />
                  </SelectTrigger>
                  <SelectContent>
                    {audioTracks?.audio_tracks.map((audio) => (
                      <SelectItem key={audio.id} value={audio.id}>
                        {audio.name}
                        <span className="text-gray-500 ml-2">
                          ({audio.beat_timestamps.length} beats)
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedAudioData && selectedAudioData.beat_timestamps.length === 0 && (
                  <p className="text-sm text-yellow-600">
                    Warning: This audio has no beat timestamps marked. Results may
                    vary.
                  </p>
                )}
              </div>

              {/* Generate Button */}
              <Button
                className="w-full"
                size="lg"
                onClick={() => generateMutation.mutate()}
                disabled={!canGenerate}
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Starting Generation...
                  </>
                ) : (
                  <>
                    <Wand2 className="mr-2 h-5 w-5" />
                    Generate Video
                  </>
                )}
              </Button>

              {generateMutation.isError && (
                <p className="text-red-500 text-sm">
                  Error starting generation. Please try again.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Current Generation Status */}
          {generationDetail && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Current Generation</CardTitle>
                  <Badge className={getStatusColor(generationDetail.status)}>
                    {generationDetail.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {(generationDetail.status === "pending" ||
                  generationDetail.status === "processing") && (
                  <div className="space-y-2">
                    <Progress
                      value={
                        generationDetail.status === "pending"
                          ? 25
                          : generationDetail.status === "processing"
                          ? 60
                          : 100
                      }
                    />
                    <p className="text-sm text-gray-500">
                      {generationDetail.status === "pending"
                        ? "Queued, waiting to start..."
                        : "AI is selecting clips and generating caption..."}
                    </p>
                  </div>
                )}

                {generationDetail.status === "completed" && (
                  <>
                    {/* Caption */}
                    {generationDetail.caption && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <label className="text-sm font-medium">
                            Generated Caption
                          </label>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                navigator.clipboard.writeText(
                                  generationDetail.caption || ""
                                )
                              }
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                regenerateCaptionMutation.mutate(generationDetail.id)
                              }
                              disabled={regenerateCaptionMutation.isPending}
                            >
                              <RefreshCw
                                className={`h-4 w-4 ${
                                  regenerateCaptionMutation.isPending
                                    ? "animate-spin"
                                    : ""
                                }`}
                              />
                            </Button>
                          </div>
                        </div>
                        <Textarea
                          value={generationDetail.caption}
                          readOnly
                          className="min-h-24"
                        />
                      </div>
                    )}

                    {/* Download */}
                    {generationDetail.output_path && (
                      <div className="flex gap-2">
                        <a
                          href={`/storage${generationDetail.output_path.replace(
                            "/storage",
                            ""
                          )}`}
                          download
                          className="flex-1"
                        >
                          <Button className="w-full">
                            <Download className="mr-2 h-4 w-4" />
                            Download Video
                          </Button>
                        </a>
                      </div>
                    )}

                    {/* Clip Sequence */}
                    {generationDetail.clip_sequence.length > 0 && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Clip Sequence</label>
                        <div className="space-y-1">
                          {generationDetail.clip_sequence.map((seq, i) => (
                            <div
                              key={i}
                              className="text-xs bg-gray-50 p-2 rounded flex justify-between"
                            >
                              <span className="font-medium">
                                {seq.beat_segment}
                              </span>
                              <span className="text-gray-500">
                                {seq.start_ms}ms - {seq.end_ms}ms
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {generationDetail.status === "failed" && (
                  <div className="text-red-500">
                    <p className="font-medium">Generation Failed</p>
                    <p className="text-sm">{generationDetail.error_message}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Recent Generations */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Recent Generations</CardTitle>
            </CardHeader>
            <CardContent>
              {generations?.generations && generations.generations.length > 0 ? (
                <div className="space-y-3">
                  {generations.generations.map((gen) => (
                    <div
                      key={gen.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        currentGeneration === gen.id
                          ? "border-blue-500 bg-blue-50"
                          : "hover:bg-gray-50"
                      }`}
                      onClick={() => setCurrentGeneration(gen.id)}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">
                          {gen.id.slice(0, 8)}
                        </span>
                        <Badge
                          variant="outline"
                          className={getStatusColor(gen.status)}
                        >
                          {gen.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-500">
                        {formatDateTime(gen.created_at)}
                      </p>
                      {gen.caption && (
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {gen.caption}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm text-center py-4">
                  No generations yet
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Caption Options Dialog */}
      <Dialog open={captionDialogOpen} onOpenChange={setCaptionDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Choose Caption</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {captionOptions.map((option, i) => (
              <div
                key={i}
                className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                onClick={() => {
                  if (currentGeneration) {
                    updateCaptionMutation.mutate({
                      id: currentGeneration,
                      caption: option.caption,
                    });
                  }
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="secondary">{option.hook_type}</Badge>
                  <span className="text-sm text-gray-500">
                    {option.length} chars
                  </span>
                </div>
                <p className="text-sm">{option.caption}</p>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCaptionDialogOpen(false)}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
