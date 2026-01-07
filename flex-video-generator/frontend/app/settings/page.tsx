"use client";

import { useQuery } from "@tanstack/react-query";
import { Settings, CheckCircle, XCircle, Database, FolderOpen } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";

export default function SettingsPage() {
  const { data: settings, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: () => api.getSettings(),
  });

  const { data: captionProfiles } = useQuery({
    queryKey: ["caption-profiles"],
    queryFn: () => api.listCaptionProfiles(),
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          View application configuration and API status.
        </p>
      </div>

      <div className="space-y-6 max-w-3xl">
        {/* API Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              API Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-full ${
                    settings?.api_configured.anthropic
                      ? "bg-green-100"
                      : "bg-red-100"
                  }`}
                >
                  {settings?.api_configured.anthropic ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
                <div>
                  <p className="font-medium">Anthropic Claude API</p>
                  <p className="text-sm text-gray-500">
                    Used for clip selection and caption generation
                  </p>
                </div>
              </div>
              <Badge
                variant={settings?.api_configured.anthropic ? "success" : "destructive"}
              >
                {settings?.api_configured.anthropic ? "Configured" : "Not Configured"}
              </Badge>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-full ${
                    settings?.api_configured.twelve_labs
                      ? "bg-green-100"
                      : "bg-red-100"
                  }`}
                >
                  {settings?.api_configured.twelve_labs ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
                <div>
                  <p className="font-medium">Twelve Labs API</p>
                  <p className="text-sm text-gray-500">
                    Used for automatic clip analysis
                  </p>
                </div>
              </div>
              <Badge
                variant={
                  settings?.api_configured.twelve_labs ? "success" : "destructive"
                }
              >
                {settings?.api_configured.twelve_labs
                  ? "Configured"
                  : "Not Configured"}
              </Badge>
            </div>

            <div className="text-sm text-gray-500 p-3 bg-yellow-50 rounded-lg">
              To configure API keys, set the following environment variables:
              <ul className="list-disc list-inside mt-2">
                <li>
                  <code className="bg-gray-100 px-1 rounded">ANTHROPIC_API_KEY</code>
                </li>
                <li>
                  <code className="bg-gray-100 px-1 rounded">TWELVE_LABS_API_KEY</code>
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Storage Paths */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FolderOpen className="h-5 w-5" />
              Storage Configuration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Audio Path</span>
                <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                  {settings?.audio_path}
                </code>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Clips Path</span>
                <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                  {settings?.clips_path}
                </code>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Exports Path</span>
                <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                  {settings?.exports_path}
                </code>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Claude Model */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              AI Model Configuration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Claude Model</span>
              <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                {settings?.claude_model}
              </code>
            </div>
          </CardContent>
        </Card>

        {/* Caption Profiles */}
        <Card>
          <CardHeader>
            <CardTitle>Caption Optimization Profiles</CardTitle>
          </CardHeader>
          <CardContent>
            {captionProfiles?.profiles && captionProfiles.profiles.length > 0 ? (
              <div className="space-y-3">
                {captionProfiles.profiles.map((profile) => (
                  <div
                    key={profile.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{profile.name}</p>
                      <p className="text-sm text-gray-500">
                        {profile.rules.hook_patterns?.length || 0} hook patterns
                      </p>
                    </div>
                    {profile.is_default && (
                      <Badge variant="secondary">Default</Badge>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No caption profiles configured. A default profile will be created
                automatically.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Version Info */}
        <Card>
          <CardContent className="py-4">
            <div className="text-center text-gray-500 text-sm">
              <p>Flex Video Generator v1.0.0</p>
              <p>Built with Next.js, FastAPI, and Claude AI</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
