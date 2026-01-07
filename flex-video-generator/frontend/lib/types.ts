/**
 * TypeScript interfaces for the Flex Video Generator.
 */

// Creator types
export interface BrandProfile {
  niche?: string;
  tone: string[];
  avoid: string[];
  signature_phrases: string[];
  flex_style?: string;
  lifestyle_themes: string[];
}

export interface CaptionRules {
  max_length: number;
  min_length: number;
  hashtag_strategy: "none" | "minimal" | "moderate";
  hashtag_count: number;
  emoji_usage: "none" | "minimal" | "moderate";
  cta_style: "soft" | "hard" | "none";
  voice: "first_person" | "third_person";
  banned_words: string[];
}

export interface Creator {
  id: string;
  name: string;
  handle?: string;
  brand_profile: BrandProfile;
  caption_rules: CaptionRules;
  created_at: string;
  updated_at: string;
}

export interface CreatorCreate {
  name: string;
  handle?: string;
  brand_profile?: BrandProfile;
  caption_rules?: CaptionRules;
}

// Audio types
export interface AudioContext {
  mood?: string;
  trend_type?: string;
  trend_origin?: string;
  typical_use?: string;
  energy_arc?: string;
}

export interface BeatTimestamp {
  ms: number;
  type: "intro" | "build" | "pre_drop" | "drop" | "sustain" | "outro";
  intensity: number;
  duration_ms: number;
  notes?: string;
  recommended_clip_type?: string;
}

export interface AudioTrack {
  id: string;
  name: string;
  file_path: string;
  duration_ms: number;
  context: AudioContext;
  beat_timestamps: BeatTimestamp[];
  pacing_guide?: string;
  is_active: boolean;
  created_at: string;
}

// Clip types
export interface ClipAnalysis {
  visual_content?: string;
  detected_objects: string[];
  detected_actions: string[];
  detected_text: string[];
  scene_type?: string;
  dominant_colors: string[];
  has_faces: boolean;
  face_count: number;
  audio_content?: string;
}

export interface ClipContext {
  flex_category?: string;
  flex_intensity: number;
  mood?: string;
  best_for: string[];
  avoid_pairing_with: string[];
  season: string;
  location_type?: string;
  custom_tags: string[];
}

export interface ClipTechnical {
  orientation: "vertical" | "horizontal" | "square";
  resolution?: string;
  fps: number;
  has_audio: boolean;
  quality_score: number;
}

export interface Clip {
  id: string;
  creator_id: string;
  file_path: string;
  thumbnail_path?: string;
  duration_ms: number;
  analysis: ClipAnalysis;
  context: ClipContext;
  technical: ClipTechnical;
  twelve_labs_video_id?: string;
  twelve_labs_index_id?: string;
  is_active: boolean;
  created_at: string;
}

// Generation types
export type GenerationStatus = "pending" | "processing" | "completed" | "failed";

export interface ClipSequenceItem {
  clip_id: string;
  beat_segment: string;
  start_ms: number;
  end_ms: number;
  reasoning?: string;
}

export interface Generation {
  id: string;
  creator_id: string;
  audio_id: string;
  clip_sequence: ClipSequenceItem[];
  caption?: string;
  caption_metadata: Record<string, unknown>;
  ai_reasoning: Record<string, unknown>;
  output_path?: string;
  status: GenerationStatus;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface GenerationCreate {
  creator_id: string;
  audio_id: string;
  clip_ids?: string[];
}

// Caption Profile types
export interface CaptionProfileRules {
  hook_patterns: string[];
  structure: string;
  length_sweet_spot: {
    min: number;
    max: number;
    ideal: number;
  };
  formatting: {
    line_breaks: "strategic" | "none" | "every_sentence";
    capitalization: "normal" | "strategic_caps" | "all_lower";
  };
  engagement_triggers: string[];
  banned_patterns: string[];
  trending_formats: string[];
}

export interface CaptionProfile {
  id: string;
  name: string;
  is_default: boolean;
  rules: CaptionProfileRules;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ListResponse<T> {
  items: T[];
  total: number;
}

export interface CreatorListResponse {
  creators: Creator[];
  total: number;
}

export interface AudioTrackListResponse {
  audio_tracks: AudioTrack[];
  total: number;
}

export interface ClipListResponse {
  clips: Clip[];
  total: number;
}

export interface GenerationListResponse {
  generations: Generation[];
  total: number;
}

// Settings types
export interface AppSettings {
  storage_root: string;
  audio_path: string;
  clips_path: string;
  exports_path: string;
  claude_model: string;
  api_configured: {
    anthropic: boolean;
    twelve_labs: boolean;
  };
}
