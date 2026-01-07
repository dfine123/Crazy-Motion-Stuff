"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Film, Search, Upload, Trash2, Filter } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
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
import { formatDuration, getFlexIntensityLabel } from "@/lib/utils";

export default function ClipsPage() {
  const [selectedCreator, setSelectedCreator] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: creators } = useQuery({
    queryKey: ["creators"],
    queryFn: () => api.listCreators(),
  });

  const { data: clips, isLoading } = useQuery({
    queryKey: ["clips", selectedCreator, selectedCategory],
    queryFn: () =>
      api.listClips({
        creator_id: selectedCreator || undefined,
        flex_category: selectedCategory || undefined,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteClip(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clips"] });
      setDeleteId(null);
    },
  });

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clip Library</h1>
          <p className="mt-2 text-gray-600">
            Browse and manage video clips for all creators.
          </p>
        </div>
        <Link href="/clips/upload">
          <Button>
            <Upload className="mr-2 h-4 w-4" />
            Upload Clips
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <Select value={selectedCreator} onValueChange={setSelectedCreator}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Creators" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Creators</SelectItem>
            {creators?.creators.map((creator) => (
              <SelectItem key={creator.id} value={creator.id}>
                {creator.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Categories</SelectItem>
            <SelectItem value="travel">Travel</SelectItem>
            <SelectItem value="cars">Cars</SelectItem>
            <SelectItem value="watches">Watches</SelectItem>
            <SelectItem value="lifestyle">Lifestyle</SelectItem>
            <SelectItem value="money">Money</SelectItem>
            <SelectItem value="property">Property</SelectItem>
            <SelectItem value="experiences">Experiences</SelectItem>
          </SelectContent>
        </Select>

        {(selectedCreator || selectedCategory) && (
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedCreator("");
              setSelectedCategory("");
            }}
          >
            Clear Filters
          </Button>
        )}
      </div>

      {/* Clips Grid */}
      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : clips?.clips && clips.clips.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {clips.clips.map((clip) => (
            <Card
              key={clip.id}
              className="overflow-hidden group hover:shadow-md transition-shadow"
            >
              <div className="aspect-[9/16] bg-gray-200 relative">
                {clip.thumbnail_path ? (
                  <img
                    src={`/storage${clip.thumbnail_path.replace("/storage", "")}`}
                    alt="Clip thumbnail"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <Film className="h-12 w-12" />
                  </div>
                )}

                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-3">
                  <div className="flex justify-end">
                    <Button
                      variant="destructive"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => setDeleteId(clip.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="text-white text-xs space-y-1">
                    {clip.analysis.visual_content && (
                      <p className="line-clamp-3">{clip.analysis.visual_content}</p>
                    )}
                  </div>
                </div>

                {/* Duration badge */}
                <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                  {formatDuration(clip.duration_ms)}
                </div>
              </div>

              <CardContent className="p-3 space-y-2">
                <div className="flex flex-wrap gap-1">
                  {clip.context.flex_category && (
                    <Badge variant="secondary" className="text-xs">
                      {clip.context.flex_category}
                    </Badge>
                  )}
                  {clip.context.flex_intensity && (
                    <Badge variant="outline" className="text-xs">
                      {getFlexIntensityLabel(clip.context.flex_intensity)}
                    </Badge>
                  )}
                </div>

                {clip.context.best_for && clip.context.best_for.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {clip.context.best_for.slice(0, 2).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                <p className="text-xs text-gray-500">
                  {clip.technical.resolution} • {clip.technical.fps}fps
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Film className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No clips found</p>
            <Link href="/clips/upload">
              <Button>Upload Your First Clips</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Total count */}
      {clips && clips.total > 0 && (
        <p className="text-center text-gray-500 mt-6">
          Showing {clips.clips.length} of {clips.total} clips
        </p>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Clip</DialogTitle>
          </DialogHeader>
          <p className="text-gray-600">
            Are you sure you want to delete this clip? This action cannot be undone.
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
