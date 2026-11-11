export interface HouseFeatures {
  first_floor_sf: number;
  second_floor_sf: number;
  total_bsmt_sf: number;
  bsmt_fin_sf1: number;
  overall_quality: number;
  overall_condition: number;
  kitchen_quality: "Ex" | "Gd" | "TA" | "Fa" | "Po";
  year_built: number;
  year_remod_add: number;
  neighborhood: string;
  ms_zoning: "C (all)" | "FV" | "RH" | "RL" | "RM";
  lot_area: number;
  garage_cars: number;
  full_bath: number;
  half_bath: number;
  fireplaces: number;
}