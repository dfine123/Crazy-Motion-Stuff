"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import api from "@/lib/api";
import type { CreatorCreate } from "@/lib/types";

export default function NewCreatorPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<CreatorCreate>({
    name: "",
    handle: "",
    brand_profile: {
      niche: "",
      tone: [],
      avoid: [],
      signature_phrases: [],
      flex_style: "subtle",
      lifestyle_themes: [],
    },
    caption_rules: {
      max_length: 150,
      min_length: 50,
      hashtag_strategy: "minimal",
      hashtag_count: 3,
      emoji_usage: "minimal",
      cta_style: "soft",
      voice: "first_person",
      banned_words: [],
    },
  });

  const [toneInput, setToneInput] = useState("");
  const [avoidInput, setAvoidInput] = useState("");
  const [themesInput, setThemesInput] = useState("");
  const [phrasesInput, setPhrasesInput] = useState("");
  const [bannedInput, setBannedInput] = useState("");

  const createMutation = useMutation({
    mutationFn: (data: CreatorCreate) => api.createCreator(data),
    onSuccess: (creator) => {
      router.push(`/creators/${creator.id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: CreatorCreate = {
      ...formData,
      brand_profile: {
        ...formData.brand_profile!,
        tone: toneInput.split(",").map((s) => s.trim()).filter(Boolean),
        avoid: avoidInput.split(",").map((s) => s.trim()).filter(Boolean),
        lifestyle_themes: themesInput.split(",").map((s) => s.trim()).filter(Boolean),
        signature_phrases: phrasesInput.split(",").map((s) => s.trim()).filter(Boolean),
      },
      caption_rules: {
        ...formData.caption_rules!,
        banned_words: bannedInput.split(",").map((s) => s.trim()).filter(Boolean),
      },
    };
    createMutation.mutate(data);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link href="/creators" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Creators
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">New Creator</h1>
        <p className="mt-2 text-gray-600">
          Create a new creator profile with brand voice and style preferences.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8 max-w-3xl">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Creator name"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="handle">Handle</Label>
                <Input
                  id="handle"
                  value={formData.handle || ""}
                  onChange={(e) => setFormData({ ...formData, handle: e.target.value })}
                  placeholder="@handle"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Brand Profile */}
        <Card>
          <CardHeader>
            <CardTitle>Brand Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="niche">Niche</Label>
                <Select
                  value={formData.brand_profile?.niche || ""}
                  onValueChange={(value) =>
                    setFormData({
                      ...formData,
                      brand_profile: { ...formData.brand_profile!, niche: value },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select niche" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="forex">Forex</SelectItem>
                    <SelectItem value="crypto">Crypto</SelectItem>
                    <SelectItem value="ecom">E-commerce</SelectItem>
                    <SelectItem value="motivation">Motivation</SelectItem>
                    <SelectItem value="lifestyle">Lifestyle</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="flex_style">Flex Style</Label>
                <Select
                  value={formData.brand_profile?.flex_style || ""}
                  onValueChange={(value) =>
                    setFormData({
                      ...formData,
                      brand_profile: { ...formData.brand_profile!, flex_style: value },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="subtle">Subtle</SelectItem>
                    <SelectItem value="overt">Overt</SelectItem>
                    <SelectItem value="educational">Educational</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tone">Tone (comma-separated)</Label>
              <Input
                id="tone"
                value={toneInput}
                onChange={(e) => setToneInput(e.target.value)}
                placeholder="confident, luxurious, aspirational"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="themes">Lifestyle Themes (comma-separated)</Label>
              <Input
                id="themes"
                value={themesInput}
                onChange={(e) => setThemesInput(e.target.value)}
                placeholder="travel, cars, watches, freedom"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phrases">Signature Phrases (comma-separated)</Label>
              <Textarea
                id="phrases"
                value={phrasesInput}
                onChange={(e) => setPhrasesInput(e.target.value)}
                placeholder="Build your empire, Time freedom is real freedom"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="avoid">Words/Phrases to Avoid (comma-separated)</Label>
              <Input
                id="avoid"
                value={avoidInput}
                onChange={(e) => setAvoidInput(e.target.value)}
                placeholder="desperate language, hype words"
              />
            </div>
          </CardContent>
        </Card>

        {/* Caption Rules */}
        <Card>
          <CardHeader>
            <CardTitle>Caption Rules</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="min_length">Min Length</Label>
                <Input
                  id="min_length"
                  type="number"
                  value={formData.caption_rules?.min_length || 50}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      caption_rules: {
                        ...formData.caption_rules!,
                        min_length: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_length">Max Length</Label>
                <Input
                  id="max_length"
                  type="number"
                  value={formData.caption_rules?.max_length || 150}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      caption_rules: {
                        ...formData.caption_rules!,
                        max_length: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="hashtag_count">Hashtag Count</Label>
                <Input
                  id="hashtag_count"
                  type="number"
                  value={formData.caption_rules?.hashtag_count || 3}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      caption_rules: {
                        ...formData.caption_rules!,
                        hashtag_count: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="hashtag_strategy">Hashtag Strategy</Label>
                <Select
                  value={formData.caption_rules?.hashtag_strategy || "minimal"}
                  onValueChange={(value: "none" | "minimal" | "moderate") =>
                    setFormData({
                      ...formData,
                      caption_rules: {
                        ...formData.caption_rules!,
                        hashtag_strategy: value,
                      },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    <SelectItem value="minimal">Minimal</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="emoji_usage">Emoji Usage</Label>
                <Select
                  value={formData.caption_rules?.emoji_usage || "minimal"}
                  onValueChange={(value: "none" | "minimal" | "moderate") =>
                    setFormData({
                      ...formData,
                      caption_rules: {
                        ...formData.caption_rules!,
                        emoji_usage: value,
                      },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    <SelectItem value="minimal">Minimal</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="cta_style">CTA Style</Label>
                <Select
                  value={formData.caption_rules?.cta_style || "soft"}
                  onValueChange={(value: "soft" | "hard" | "none") =>
                    setFormData({
                      ...formData,
                      caption_rules: {
                        ...formData.caption_rules!,
                        cta_style: value,
                      },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    <SelectItem value="soft">Soft</SelectItem>
                    <SelectItem value="hard">Hard</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="banned_words">Banned Words (comma-separated)</Label>
              <Input
                id="banned_words"
                value={bannedInput}
                onChange={(e) => setBannedInput(e.target.value)}
                placeholder="link in bio, dm me"
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Link href="/creators">
            <Button variant="outline">Cancel</Button>
          </Link>
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? "Creating..." : "Create Creator"}
          </Button>
        </div>

        {createMutation.isError && (
          <p className="text-red-500 text-sm">
            Error creating creator. Please try again.
          </p>
        )}
      </form>
    </div>
  );
}
