import {RecentPredictionsProps} from "@/app/interfaces/RecentPredictionsProps";
import {roundToHundreds} from "@/app/lib/format";
import {CARD_CLASS, CARD_TITLE_CLASS} from "@/app/lib/styles";

export default function RecentPredictions({ predictions }: RecentPredictionsProps) {
  if (predictions.length === 0) {
    return null;
  }

  return (
    <section className={`${CARD_CLASS} space-y-4`}>
      <h2 className={CARD_TITLE_CLASS}>Recent predictions</h2>
      <ul className="max-h-80 divide-y divide-zinc-100 overflow-y-auto dark:divide-zinc-800">
        {predictions.map((item) => (
          <li key={item.id} className="flex flex-col gap-1 py-3 text-sm sm:flex-row sm:items-center sm:justify-between">
            <p className="font-semibold text-zinc-900 dark:text-zinc-50">
              ≈ ${roundToHundreds(item.predicted_price).toLocaleString("en-US")}
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              {new Date(item.created_at).toLocaleString()} • Quality {item.features.overall_quality} •{" "}
              {item.features.first_floor_sf + item.features.second_floor_sf} sq ft
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
