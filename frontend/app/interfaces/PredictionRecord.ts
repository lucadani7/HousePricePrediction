import {HouseFeatures} from "@/app/interfaces/HouseFeatures";

export interface PredictionRecord {
  id: number;
  created_at: string;
  // The API stores exactly the 16 fields that were sent to /predict.
  features: HouseFeatures;
  predicted_price: number;
}
