import {HouseFeatures} from "@/app/interfaces/HouseFeatures";

export interface PredictionFormProps {
  onPredict: (features: HouseFeatures) => void;
  isLoading: boolean;
}