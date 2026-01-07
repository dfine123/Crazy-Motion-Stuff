/**
 * API client for the Flex Video Generator backend.
 */

import axios, { AxiosInstance } from "axios";
import type {
  Creator,
  CreatorCreate,
  CreatorListResponse,
  AudioTrack,
  AudioTrackListResponse,
  BeatTimestamp,
  Clip,
  ClipListResponse,
  Generation,
  GenerationCreate,
  GenerationListResponse,
  CaptionProfile,
  AppSettings,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  // Creator endpoints
  async createCreator(data: CreatorCreate): Promise<Creator> {
    const response = await this.client.post<Creator>("/creators", data);
    return response.data;
  }

  async listCreators(params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }): Promise<CreatorListResponse> {
    const response = await this.client.get<CreatorListResponse>("/creators", {
      params,
    });
    return response.data;
  }

  async getCreator(id: string): Promise<Creator> {
    const response = await this.client.get<Creator>(`/creators/${id}`);
    return response.data;
  }

  async updateCreator(
    id: string,
    data: Partial<CreatorCreate>
  ): Promise<Creator> {
    const response = await this.client.put<Creator>(`/creators/${id}`, data);
    return response.data;
  }

  async deleteCreator(id: string): Promise<void> {
    await this.client.delete(`/creators/${id}`);
  }

  async getCreatorStats(
    id: string
  ): Promise<{
    creator_id: string;
    clip_count: number;
    generation_count: number;
    completed_generations: number;
  }> {
    const response = await this.client.get(`/creators/${id}/stats`);
    return response.data;
  }

  // Audio endpoints
  async uploadAudio(
    file: File,
    name: string,
    context?: Record<string, unknown>,
    pacingGuide?: string
  ): Promise<AudioTrack> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", name);
    if (context) {
      formData.append("context", JSON.stringify(context));
    }
    if (pacingGuide) {
      formData.append("pacing_guide", pacingGuide);
    }

    const response = await this.client.post<AudioTrack>("/audio", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }

  async listAudioTracks(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    is_active?: boolean;
  }): Promise<AudioTrackListResponse> {
    const response = await this.client.get<AudioTrackListResponse>("/audio", {
      params,
    });
    return response.data;
  }

  async getAudioTrack(id: string): Promise<AudioTrack> {
    const response = await this.client.get<AudioTrack>(`/audio/${id}`);
    return response.data;
  }

  async updateAudioTrack(
    id: string,
    data: Partial<AudioTrack>
  ): Promise<AudioTrack> {
    const response = await this.client.put<AudioTrack>(`/audio/${id}`, data);
    return response.data;
  }

  async updateBeatTimestamps(
    id: string,
    timestamps: BeatTimestamp[]
  ): Promise<AudioTrack> {
    const response = await this.client.put<AudioTrack>(
      `/audio/${id}/timestamps`,
      timestamps
    );
    return response.data;
  }

  async deleteAudioTrack(id: string): Promise<void> {
    await this.client.delete(`/audio/${id}`);
  }

  getAudioWaveformUrl(id: string): string {
    return `${API_BASE_URL}/audio/${id}/waveform`;
  }

  // Clip endpoints
  async uploadClip(
    file: File,
    creatorId: string,
    context?: Record<string, unknown>,
    analyze: boolean = true
  ): Promise<{
    clip_id: string;
    file_path: string;
    analysis_status: string;
    analysis?: Record<string, unknown>;
    error?: string;
  }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("creator_id", creatorId);
    if (context) {
      formData.append("context", JSON.stringify(context));
    }
    formData.append("analyze", analyze.toString());

    const response = await this.client.post("/clips/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }

  async importClipsFromSpreadsheet(
    file: File,
    creatorId: string,
    analyze: boolean = false
  ): Promise<{
    imported: number;
    failed: number;
    results: Array<{ file_path: string; status: string; error?: string }>;
  }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("creator_id", creatorId);
    formData.append("analyze", analyze.toString());

    const response = await this.client.post("/clips/import", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }

  async listClips(params?: {
    creator_id?: string;
    skip?: number;
    limit?: number;
    flex_category?: string;
    is_active?: boolean;
  }): Promise<ClipListResponse> {
    const response = await this.client.get<ClipListResponse>("/clips", {
      params,
    });
    return response.data;
  }

  async getClip(id: string): Promise<Clip> {
    const response = await this.client.get<Clip>(`/clips/${id}`);
    return response.data;
  }

  async updateClip(id: string, data: Partial<Clip>): Promise<Clip> {
    const response = await this.client.put<Clip>(`/clips/${id}`, data);
    return response.data;
  }

  async deleteClip(id: string): Promise<void> {
    await this.client.delete(`/clips/${id}`);
  }

  async reanalyzeClip(id: string): Promise<{ status: string; clip_id: string }> {
    const response = await this.client.post(`/clips/${id}/reanalyze`);
    return response.data;
  }

  // Generation endpoints
  async createGeneration(data: GenerationCreate): Promise<Generation> {
    const response = await this.client.post<Generation>("/generate", data);
    return response.data;
  }

  async listGenerations(params?: {
    creator_id?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<GenerationListResponse> {
    const response = await this.client.get<GenerationListResponse>(
      "/generate",
      { params }
    );
    return response.data;
  }

  async getGenerationHistory(params?: {
    creator_id?: string;
    limit?: number;
  }): Promise<{
    generations: Array<{
      id: string;
      creator_id: string;
      audio_id: string;
      caption?: string;
      output_path?: string;
      completed_at?: string;
    }>;
  }> {
    const response = await this.client.get("/generate/history", { params });
    return response.data;
  }

  async getGeneration(id: string): Promise<Generation> {
    const response = await this.client.get<Generation>(`/generate/${id}`);
    return response.data;
  }

  async regenerateCaption(
    id: string,
    keepClips: boolean = true
  ): Promise<{
    caption_options: Array<{
      caption: string;
      hook_type: string;
      length: number;
    }>;
    selected_caption?: string;
  }> {
    const response = await this.client.post(`/generate/${id}/regenerate-caption`, {
      keep_clips: keepClips,
    });
    return response.data;
  }

  async updateGenerationCaption(
    id: string,
    caption: string
  ): Promise<{ status: string; caption: string }> {
    const response = await this.client.put(`/generate/${id}/caption`, null, {
      params: { caption },
    });
    return response.data;
  }

  async deleteGeneration(id: string): Promise<void> {
    await this.client.delete(`/generate/${id}`);
  }

  // Settings endpoints
  async getSettings(): Promise<AppSettings> {
    const response = await this.client.get<AppSettings>("/settings");
    return response.data;
  }

  async listCaptionProfiles(): Promise<{
    profiles: CaptionProfile[];
    total: number;
  }> {
    const response = await this.client.get("/settings/caption-profiles");
    return response.data;
  }

  async getDefaultCaptionProfile(): Promise<CaptionProfile> {
    const response = await this.client.get<CaptionProfile>(
      "/settings/caption-profiles/default"
    );
    return response.data;
  }

  async createCaptionProfile(
    data: Partial<CaptionProfile>
  ): Promise<CaptionProfile> {
    const response = await this.client.post<CaptionProfile>(
      "/settings/caption-profiles",
      data
    );
    return response.data;
  }

  async updateCaptionProfile(
    id: string,
    data: Partial<CaptionProfile>
  ): Promise<CaptionProfile> {
    const response = await this.client.put<CaptionProfile>(
      `/settings/caption-profiles/${id}`,
      data
    );
    return response.data;
  }

  async deleteCaptionProfile(id: string): Promise<void> {
    await this.client.delete(`/settings/caption-profiles/${id}`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get("/settings/health");
    return response.data;
  }
}

export const api = new ApiClient();
export default api;
