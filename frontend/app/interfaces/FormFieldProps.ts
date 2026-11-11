import React from "react";
import {HouseFeatures} from "@/app/interfaces/HouseFeatures";

type FieldChangeHandler = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;

export interface NumberFieldProps {
  name: keyof HouseFeatures;
  label: string;
  value: number;
  onChange: FieldChangeHandler;
  min?: number;
  max?: number;
}

export interface SelectFieldProps {
  name: keyof HouseFeatures;
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: FieldChangeHandler;
}
