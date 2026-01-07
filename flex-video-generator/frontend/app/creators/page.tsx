"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Search, Trash2, Edit } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function CreatorsPage() {
  const [search, setSearch] = useState("");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: creators, isLoading } = useQuery({
    queryKey: ["creators", search],
    queryFn: () => api.listCreators({ search: search || undefined }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteCreator(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["creators"] });
      setDeleteId(null);
    },
  });

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Creators</h1>
          <p className="mt-2 text-gray-600">
            Manage creator profiles with brand voice and style preferences.
          </p>
        </div>
        <Link href="/creators/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Creator
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search creators..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Creators Grid */}
      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : creators?.creators && creators.creators.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {creators.creators.map((creator) => (
            <Card key={creator.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{creator.name}</CardTitle>
                    {creator.handle && (
                      <p className="text-sm text-gray-500">@{creator.handle}</p>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Link href={`/creators/${creator.id}`}>
                      <Button variant="ghost" size="icon">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(creator.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {creator.brand_profile.niche && (
                    <div>
                      <span className="text-xs font-medium text-gray-500">Niche</span>
                      <p className="text-sm">{creator.brand_profile.niche}</p>
                    </div>
                  )}

                  {creator.brand_profile.flex_style && (
                    <Badge variant="outline">{creator.brand_profile.flex_style}</Badge>
                  )}

                  <div className="flex flex-wrap gap-1">
                    {creator.brand_profile.lifestyle_themes?.slice(0, 4).map((theme) => (
                      <Badge key={theme} variant="secondary" className="text-xs">
                        {theme}
                      </Badge>
                    ))}
                    {creator.brand_profile.lifestyle_themes?.length > 4 && (
                      <Badge variant="secondary" className="text-xs">
                        +{creator.brand_profile.lifestyle_themes.length - 4}
                      </Badge>
                    )}
                  </div>

                  <p className="text-xs text-gray-400">
                    Created {formatDate(creator.created_at)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500 mb-4">No creators found</p>
            <Link href="/creators/new">
              <Button>Create Your First Creator</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Creator</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this creator? This will also delete all
              associated clips and generations. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
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
