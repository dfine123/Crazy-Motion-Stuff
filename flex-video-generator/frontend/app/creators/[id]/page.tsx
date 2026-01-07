"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Film, PlayCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function CreatorDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { data: creator, isLoading } = useQuery({
    queryKey: ["creator", params.id],
    queryFn: () => api.getCreator(params.id),
  });

  const { data: stats } = useQuery({
    queryKey: ["creator-stats", params.id],
    queryFn: () => api.getCreatorStats(params.id),
  });

  const { data: clips } = useQuery({
    queryKey: ["clips", params.id],
    queryFn: () => api.listClips({ creator_id: params.id, limit: 10 }),
  });

  const { data: generations } = useQuery({
    queryKey: ["generations", params.id],
    queryFn: () => api.listGenerations({ creator_id: params.id, limit: 10 }),
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (!creator) {
    return (
      <div className="p-8">
        <p>Creator not found</p>
        <Link href="/creators">
          <Button className="mt-4">Back to Creators</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link
          href="/creators"
          className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Creators
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{creator.name}</h1>
            {creator.handle && (
              <p className="text-lg text-gray-500">@{creator.handle}</p>
            )}
            <p className="text-sm text-gray-400 mt-1">
              Created {formatDate(creator.created_at)}
            </p>
          </div>
          <div className="flex gap-2">
            <Link href={`/clips/upload?creator=${params.id}`}>
              <Button variant="outline">
                <Film className="mr-2 h-4 w-4" />
                Upload Clips
              </Button>
            </Link>
            <Link href={`/generate?creator=${params.id}`}>
              <Button>
                <PlayCircle className="mr-2 h-4 w-4" />
                Generate Video
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{stats.clip_count}</p>
              <p className="text-sm text-gray-500">Clips</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{stats.generation_count}</p>
              <p className="text-sm text-gray-500">Generations</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{stats.completed_generations}</p>
              <p className="text-sm text-gray-500">Completed</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="clips">Clips ({clips?.total || 0})</TabsTrigger>
          <TabsTrigger value="generations">
            Generations ({generations?.total || 0})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <div className="grid grid-cols-2 gap-6">
            {/* Brand Profile */}
            <Card>
              <CardHeader>
                <CardTitle>Brand Profile</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {creator.brand_profile.niche && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Niche</p>
                    <p className="capitalize">{creator.brand_profile.niche}</p>
                  </div>
                )}

                {creator.brand_profile.flex_style && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Flex Style</p>
                    <Badge variant="outline" className="capitalize">
                      {creator.brand_profile.flex_style}
                    </Badge>
                  </div>
                )}

                {creator.brand_profile.tone?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Tone</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {creator.brand_profile.tone.map((t) => (
                        <Badge key={t} variant="secondary">
                          {t}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {creator.brand_profile.lifestyle_themes?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Lifestyle Themes
                    </p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {creator.brand_profile.lifestyle_themes.map((theme) => (
                        <Badge key={theme} variant="secondary">
                          {theme}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {creator.brand_profile.signature_phrases?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Signature Phrases
                    </p>
                    <ul className="list-disc list-inside mt-1 text-sm">
                      {creator.brand_profile.signature_phrases.map((phrase, i) => (
                        <li key={i}>{phrase}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {creator.brand_profile.avoid?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Avoid</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {creator.brand_profile.avoid.map((item) => (
                        <Badge key={item} variant="destructive" className="text-xs">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Caption Rules */}
            <Card>
              <CardHeader>
                <CardTitle>Caption Rules</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Length</p>
                    <p>
                      {creator.caption_rules.min_length} -{" "}
                      {creator.caption_rules.max_length} chars
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Voice</p>
                    <p className="capitalize">
                      {creator.caption_rules.voice.replace("_", " ")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">
                      Hashtag Strategy
                    </p>
                    <p className="capitalize">
                      {creator.caption_rules.hashtag_strategy} (
                      {creator.caption_rules.hashtag_count})
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Emoji Usage</p>
                    <p className="capitalize">{creator.caption_rules.emoji_usage}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">CTA Style</p>
                    <p className="capitalize">{creator.caption_rules.cta_style}</p>
                  </div>
                </div>

                {creator.caption_rules.banned_words?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Banned Words</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {creator.caption_rules.banned_words.map((word) => (
                        <Badge key={word} variant="destructive" className="text-xs">
                          {word}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="clips">
          {clips?.clips && clips.clips.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {clips.clips.map((clip) => (
                <Card key={clip.id} className="overflow-hidden">
                  <div className="aspect-[9/16] bg-gray-200 relative">
                    {clip.thumbnail_path ? (
                      <img
                        src={`/storage${clip.thumbnail_path.replace("/storage", "")}`}
                        alt="Clip thumbnail"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <Film className="h-8 w-8" />
                      </div>
                    )}
                  </div>
                  <CardContent className="p-3">
                    <p className="text-xs text-gray-500">
                      {(clip.duration_ms / 1000).toFixed(1)}s
                    </p>
                    {clip.context.flex_category && (
                      <Badge variant="secondary" className="text-xs mt-1">
                        {clip.context.flex_category}
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-gray-500 mb-4">No clips uploaded yet</p>
                <Link href={`/clips/upload?creator=${params.id}`}>
                  <Button>Upload Clips</Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="generations">
          {generations?.generations && generations.generations.length > 0 ? (
            <div className="space-y-4">
              {generations.generations.map((gen) => (
                <Card key={gen.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Generation {gen.id.slice(0, 8)}</p>
                        <p className="text-sm text-gray-500">
                          {formatDate(gen.created_at)}
                        </p>
                      </div>
                      <Badge
                        variant={
                          gen.status === "completed"
                            ? "success"
                            : gen.status === "failed"
                            ? "destructive"
                            : "secondary"
                        }
                      >
                        {gen.status}
                      </Badge>
                    </div>
                    {gen.caption && (
                      <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                        {gen.caption}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-gray-500 mb-4">No generations yet</p>
                <Link href={`/generate?creator=${params.id}`}>
                  <Button>Generate Video</Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
