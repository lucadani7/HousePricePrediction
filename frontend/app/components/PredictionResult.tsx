import {PredictionResultProps} from "@/app/interfaces/PredictionResultProps";
import {roundToHundreds} from "@/app/lib/format";

export default function PredictionResult({ price, error }: PredictionResultProps) {
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 shadow-sm dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
        <h3 className="font-semibold">Please check the form</h3>
        <p className="mt-1 whitespace-pre-line text-sm">{error}</p>
      </div>
    );
  }

  if (price === null) {
    return null;
  }

  return (
    <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-center shadow-sm sm:p-6 dark:border-emerald-900 dark:bg-emerald-950/40">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-700 sm:text-sm dark:text-emerald-400">
        Estimated house price
      </h3>
      <p className="mt-2 text-3xl font-extrabold text-emerald-950 sm:text-4xl dark:text-emerald-100">
        ≈ ${roundToHundreds(price).toLocaleString("en-US")}
      </p>
      <p className="mt-2 text-sm text-emerald-800 dark:text-emerald-300">
        For a normal sale, estimates are typically within ±7% of the actual price.
      </p>
    </div>
  );
}
