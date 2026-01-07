"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  Users,
  Music,
  Film,
  PlayCircle,
  TrendingUp,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { formatDateTime, getStatusColor } from "@/lib/utils";

export default function DashboardPage() {
  const { data: creators } = useQuery({
    queryKey: ["creators"],
    queryFn: () => api.listCreators({ limit: 5 }),
  });

  const { data: audioTracks } = useQuery({
    queryKey: ["audio"],
    queryFn: () => api.listAudioTracks({ limit: 5 }),
  });

  const { data: generations } = useQuery({
    queryKey: ["generations"],
    queryFn: () => api.listGenerations({ limit: 5 }),
  });

  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: () => api.getSettings(),
  });

  const stats = [
    {
      name: "Total Creators",
      value: creators?.total || 0,
      icon: Users,
      href: "/creators",
      color: "text-blue-600",
    },
    {
      name: "Audio Tracks",
      value: audioTracks?.total || 0,
      icon: Music,
      href: "/audio",
      color: "text-purple-600",
    },
    {
      name: "Generated Videos",
      value: generations?.total || 0,
      icon: PlayCircle,
      href: "/generate",
      color: "text-green-600",
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to Flex Video Generator. Manage your creators, audio, and generate videos.
        </p>
      </div>

      {/* API Status */}
      {settings && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-lg">API Configuration Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Badge variant={settings.api_configured.anthropic ? "success" : "destructive"}>
                Anthropic: {settings.api_configured.anthropic ? "Configured" : "Not Configured"}
              </Badge>
              <Badge variant={settings.api_configured.twelve_labs ? "success" : "destructive"}>
                Twelve Labs: {settings.api_configured.twelve_labs ? "Configured" : "Not Configured"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        {stats.map((stat) => (
          <Link key={stat.name} href={stat.href}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className={`rounded-lg p-3 ${stat.color} bg-opacity-10`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/creators/new">
              <Button className="w-full justify-start" variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Create New Creator
              </Button>
            </Link>
            <Link href="/audio">
              <Button className="w-full justify-start" variant="outline">
                <Music className="mr-2 h-4 w-4" />
                Upload Audio Track
              </Button>
            </Link>
            <Link href="/clips/upload">
              <Button className="w-full justify-start" variant="outline">
                <Film className="mr-2 h-4 w-4" />
                Upload Clips
              </Button>
            </Link>
            <Link href="/generate">
              <Button className="w-full justify-start">
                <PlayCircle className="mr-2 h-4 w-4" />
                Generate Video
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Generations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Recent Generations</span>
              <Link href="/generate">
                <Button variant="ghost" size="sm">View All</Button>
              </Link>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {generations?.generations && generations.generations.length > 0 ? (
              <div className="space-y-4">
                {generations.generations.slice(0, 5).map((gen) => (
                  <div
                    key={gen.id}
                    className="flex items-center justify-between border-b pb-3 last:border-0"
                  >
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          Generation {gen.id.slice(0, 8)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDateTime(gen.created_at)}
                        </p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(gen.status)}>
                      {gen.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No generations yet. Create your first video!
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Creators List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Your Creators</span>
            <Link href="/creators">
              <Button variant="ghost" size="sm">View All</Button>
            </Link>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {creators?.creators && creators.creators.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {creators.creators.map((creator) => (
                <Link key={creator.id} href={`/creators/${creator.id}`}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-gray-900">{creator.name}</h3>
                      {creator.handle && (
                        <p className="text-sm text-gray-500">@{creator.handle}</p>
                      )}
                      <div className="mt-2 flex flex-wrap gap-1">
                        {creator.brand_profile.lifestyle_themes?.slice(0, 3).map((theme) => (
                          <Badge key={theme} variant="secondary" className="text-xs">
                            {theme}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">
              No creators yet. Create your first creator profile!
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
