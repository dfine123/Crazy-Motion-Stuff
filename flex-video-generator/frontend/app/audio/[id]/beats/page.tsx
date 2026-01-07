"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Play, Pause, Save, Plus, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import api from "@/lib/api";
import type { BeatTimestamp } from "@/lib/types";
import { getBeatTypeColor, formatDuration } from "@/lib/utils";

const BEAT_TYPES = ["intro", "build", "pre_drop", "drop", "sustain", "outro"] as const;

export default function BeatEditorPage({ params }: { params: { id: string } }) {
  const queryClient = useQueryClient();
  const audioRef = useRef<HTMLAudioElement>(null);
  const waveformRef = useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [timestamps, setTimestamps] = useState<BeatTimestamp[]>([]);
  const [selectedType, setSelectedType] = useState<typeof BEAT_TYPES[number]>("intro");
  const [selectedIntensity, setSelectedIntensity] = useState(3);

  const { data: audio, isLoading } = useQuery({
    queryKey: ["audio", params.id],
    queryFn: () => api.getAudioTrack(params.id),
  });

  useEffect(() => {
    if (audio?.beat_timestamps) {
      setTimestamps(audio.beat_timestamps);
    }
  }, [audio]);

  const saveMutation = useMutation({
    mutationFn: (timestamps: BeatTimestamp[]) =>
      api.updateBeatTimestamps(params.id, timestamps),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audio", params.id] });
    },
  });

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime * 1000);
    }
  };

  const seekTo = (ms: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = ms / 1000;
      setCurrentTime(ms);
    }
  };

  const addTimestamp = () => {
    const ms = Math.round(currentTime);

    // Check if a timestamp already exists at this position (within 100ms)
    const existing = timestamps.find(t => Math.abs(t.ms - ms) < 100);
    if (existing) return;

    const newTimestamp: BeatTimestamp = {
      ms,
      type: selectedType,
      intensity: selectedIntensity,
      duration_ms: 3000,
      notes: "",
      recommended_clip_type: "lifestyle",
    };

    setTimestamps(prev => [...prev, newTimestamp].sort((a, b) => a.ms - b.ms));
  };

  const removeTimestamp = (index: number) => {
    setTimestamps(prev => prev.filter((_, i) => i !== index));
  };

  const updateTimestamp = (index: number, updates: Partial<BeatTimestamp>) => {
    setTimestamps(prev =>
      prev.map((ts, i) => (i === index ? { ...ts, ...updates } : ts))
    );
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (!audio) {
    return (
      <div className="p-8">
        <p>Audio track not found</p>
        <Link href="/audio">
          <Button className="mt-4">Back to Audio</Button>
        </Link>
      </div>
    );
  }

  const audioUrl = `/storage${audio.file_path.replace("/storage", "")}`;

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link
          href="/audio"
          className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Audio
        </Link>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{audio.name}</h1>
            <p className="text-gray-500">{formatDuration(audio.duration_ms)}</p>
          </div>
          <Button
            onClick={() => saveMutation.mutate(timestamps)}
            disabled={saveMutation.isPending}
          >
            <Save className="mr-2 h-4 w-4" />
            {saveMutation.isPending ? "Saving..." : "Save Timestamps"}
          </Button>
        </div>
      </div>

      {/* Audio Player */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <audio
            ref={audioRef}
            src={audioUrl}
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIsPlaying(false)}
          />

          {/* Waveform / Timeline */}
          <div
            ref={waveformRef}
            className="relative h-32 bg-gray-900 rounded-lg overflow-hidden mb-4 cursor-pointer"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const x = e.clientX - rect.left;
              const percentage = x / rect.width;
              seekTo(percentage * audio.duration_ms);
            }}
          >
            {/* Progress bar */}
            <div
              className="absolute top-0 left-0 h-full bg-blue-500/30"
              style={{ width: `${(currentTime / audio.duration_ms) * 100}%` }}
            />

            {/* Playhead */}
            <div
              className="absolute top-0 w-0.5 h-full bg-red-500"
              style={{ left: `${(currentTime / audio.duration_ms) * 100}%` }}
            />

            {/* Beat markers */}
            {timestamps.map((ts, i) => (
              <div
                key={i}
                className="absolute top-0 h-full cursor-pointer group"
                style={{
                  left: `${(ts.ms / audio.duration_ms) * 100}%`,
                  width: `${(ts.duration_ms / audio.duration_ms) * 100}%`,
                  backgroundColor: `${getBeatTypeColor(ts.type)}40`,
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  seekTo(ts.ms);
                }}
              >
                <div
                  className="absolute top-0 w-1 h-full"
                  style={{ backgroundColor: getBeatTypeColor(ts.type) }}
                />
                <div className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 text-white text-xs px-2 py-1 rounded">
                  {ts.type} ({ts.intensity})
                </div>
              </div>
            ))}

            {/* Placeholder text */}
            <div className="absolute inset-0 flex items-center justify-center text-gray-400">
              Click to seek, add timestamps at current position
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" onClick={togglePlayPause}>
              {isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </Button>

            <span className="font-mono text-sm">
              {formatDuration(currentTime)} / {formatDuration(audio.duration_ms)}
            </span>

            <div className="flex-1" />

            <Select
              value={selectedType}
              onValueChange={(v) => setSelectedType(v as typeof BEAT_TYPES[number])}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {BEAT_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    <span className="flex items-center gap-2">
                      <span
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getBeatTypeColor(type) }}
                      />
                      {type}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex items-center gap-1">
              <span className="text-sm text-gray-500">Intensity:</span>
              {[1, 2, 3, 4, 5].map((i) => (
                <Button
                  key={i}
                  variant={selectedIntensity === i ? "default" : "outline"}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setSelectedIntensity(i)}
                >
                  {i}
                </Button>
              ))}
            </div>

            <Button onClick={addTimestamp}>
              <Plus className="mr-2 h-4 w-4" />
              Add Marker
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Timestamp List */}
      <Card>
        <CardHeader>
          <CardTitle>Beat Timestamps ({timestamps.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {timestamps.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {timestamps.map((ts, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
                >
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-mono"
                    onClick={() => seekTo(ts.ms)}
                  >
                    {formatDuration(ts.ms)}
                  </Button>

                  <Badge
                    style={{
                      backgroundColor: getBeatTypeColor(ts.type),
                      color: "white",
                    }}
                  >
                    {ts.type}
                  </Badge>

                  <span className="text-sm">Intensity: {ts.intensity}</span>

                  <Input
                    value={ts.notes || ""}
                    onChange={(e) =>
                      updateTimestamp(i, { notes: e.target.value })
                    }
                    placeholder="Notes..."
                    className="flex-1"
                  />

                  <Input
                    type="number"
                    value={ts.duration_ms}
                    onChange={(e) =>
                      updateTimestamp(i, { duration_ms: parseInt(e.target.value) })
                    }
                    className="w-24"
                  />
                  <span className="text-xs text-gray-500">ms</span>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeTimestamp(i)}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-4">
              No timestamps marked yet. Play the audio and click "Add Marker" to
              mark beat positions.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
