import {PredictionRecord} from "@/app/interfaces/PredictionRecord";
import {PredictionResponse} from "@/app/interfaces/PredictionResponse";
import {HouseFeatures} from "@/app/interfaces/HouseFeatures";

interface ValidationIssue {
  loc: (string | number)[];
  msg: string;
}

/**
 * Turns FastAPI's error `detail` into readable text.
 *
 * For a 422, `detail` is a list of issues such as
 * {"loc": ["body", "overall_quality"], "msg": "Input should be less than or equal to 10"}.
 * Cross-field rules have loc ["body"] and a message starting with "Value error, ".
 */
function formatErrorDetail(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return (detail as ValidationIssue[])
      .map((issue) => {
        const field = issue.loc.length > 1 ? String(issue.loc[issue.loc.length - 1]) : null;
        const message = issue.msg.replace(/^Value error, /, "");
        return field ? `${field}: ${message}` : message;
      })
      .join("\n");
  }
  return null;
}

export async function predictPrice(features: HouseFeatures): Promise<PredictionResponse> {
  const response = await fetch("/api/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(features),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(formatErrorDetail(errorData.detail) ?? `HTTP error: ${response.status}`);
  }

  return response.json();
}

export async function getPredictions(limit: number = 10): Promise<PredictionRecord[]> {
  const response = await fetch(`/api/predictions?limit=${limit}`);

  if (!response.ok) {
    throw new Error("Failed to fetch prediction history.");
  }

  return response.json();
}
