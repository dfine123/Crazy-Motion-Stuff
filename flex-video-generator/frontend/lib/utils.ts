import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (minutes > 0) {
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  }
  return `0:${remainingSeconds.toString().padStart(2, "0")}`;
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + "...";
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "completed":
      return "text-green-600 bg-green-100";
    case "processing":
      return "text-blue-600 bg-blue-100";
    case "pending":
      return "text-yellow-600 bg-yellow-100";
    case "failed":
      return "text-red-600 bg-red-100";
    default:
      return "text-gray-600 bg-gray-100";
  }
}

export function getFlexIntensityLabel(intensity: number): string {
  switch (intensity) {
    case 1:
      return "Subtle";
    case 2:
      return "Low";
    case 3:
      return "Medium";
    case 4:
      return "High";
    case 5:
      return "Maximum";
    default:
      return "Unknown";
  }
}

export function getBeatTypeColor(type: string): string {
  switch (type) {
    case "intro":
      return "#48bb78"; // green
    case "build":
      return "#ed8936"; // orange
    case "pre_drop":
      return "#ecc94b"; // yellow
    case "drop":
      return "#e53e3e"; // red
    case "sustain":
      return "#805ad5"; // purple
    case "outro":
      return "#718096"; // gray
    default:
      return "#a0aec0";
  }
}
