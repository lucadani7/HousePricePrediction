"use client";

import {PredictionRecord} from "@/app/interfaces/PredictionRecord";
import {useEffect, useState} from "react";
import {getPredictions, predictPrice} from "@/app/lib/api";
import {HouseFeatures} from "@/app/interfaces/HouseFeatures";
import PredictionResult from "@/app/components/PredictionResult";
import PredictionForm from "@/app/components/PredictionForm";
import RecentPredictions from "@/app/components/RecentPredictions";
import ThemeToggle from "@/app/components/ThemeToggle";

// After this delay a request is probably waiting for the free backend to wake up.
const SLOW_REQUEST_MS = 4000;

export default function Home() {
  const [price, setPrice] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSlow, setIsSlow] = useState<boolean>(false);
  const [predictionHistory, setPredictionHistory] = useState<PredictionRecord[]>([]);

  const fetchHistory = async () => {
    try {
      const data = await getPredictions(5);
      setPredictionHistory(data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  // Loading the history on page open also wakes up the free backend (it sleeps after
  // 15 minutes without traffic), so it is usually ready by the time the form is submitted.
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        await fetchHistory();
      } catch (err) {
        console.error("Failed to fetch initial history:", err);
      }
    };

    void loadInitialData();
  }, []);

  const handlePredict = async (features: HouseFeatures) => {
    setIsLoading(true);
    setError(null);
    setPrice(null);
    const slowTimer = setTimeout(() => setIsSlow(true), SLOW_REQUEST_MS);

    try {
      const result = await predictPrice(features);
      setPrice(result.predicted_price);
      await fetchHistory();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred.");
    } finally {
      clearTimeout(slowTimer);
      setIsSlow(false);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 sm:py-12 lg:px-8">
      <main className="mx-auto max-w-4xl space-y-6 sm:space-y-8">
        <header className="space-y-4">
          <div className="flex justify-end">
            <ThemeToggle />
          </div>
          <div className="space-y-2 text-center">
            <h1 className="text-2xl font-extrabold text-zinc-900 sm:text-3xl dark:text-zinc-50">
              House Price Prediction
            </h1>
            <p className="text-sm text-zinc-600 sm:text-base dark:text-zinc-400">
              Fill in the form to get an estimated price from the machine learning model.
            </p>
          </div>
        </header>

        {isLoading && isSlow && (
          <p
            role="status"
            className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-center text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300"
          >
            The free server is waking up after a period of inactivity. This can take up to a minute.
          </p>
        )}

        <PredictionResult price={price} error={error} />

        <PredictionForm onPredict={handlePredict} isLoading={isLoading} />

        <RecentPredictions predictions={predictionHistory} />

        <footer className="space-y-1 border-t border-zinc-200 pt-6 text-center text-xs text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
          <p>
            Data source: Ames Housing dataset (Dean De Cock, 2011), via Kaggle. Educational machine
            learning model.
          </p>
          <p>
            Valid only for houses in Ames, Iowa, sold in 2006–2010, with up to 4,000 sq ft of living
            area. Not meant for other cities, countries or time periods.
          </p>
        </footer>
      </main>
    </div>
  );
}
