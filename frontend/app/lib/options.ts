// The 25 neighborhoods of Ames present in the training data, sorted by label.
export const NEIGHBORHOODS: { value: string; label: string }[] = [
  { value: "Blmngtn", label: "Bloomington Heights" },
  { value: "Blueste", label: "Bluestem" },
  { value: "BrDale", label: "Briardale" },
  { value: "BrkSide", label: "Brookside" },
  { value: "ClearCr", label: "Clear Creek" },
  { value: "CollgCr", label: "College Creek" },
  { value: "Crawfor", label: "Crawford" },
  { value: "Edwards", label: "Edwards" },
  { value: "Gilbert", label: "Gilbert" },
  { value: "IDOTRR", label: "Iowa DOT and Rail Road" },
  { value: "MeadowV", label: "Meadow Village" },
  { value: "Mitchel", label: "Mitchell" },
  { value: "NAmes", label: "North Ames" },
  { value: "NPkVill", label: "Northpark Villa" },
  { value: "NoRidge", label: "Northridge" },
  { value: "NridgHt", label: "Northridge Heights" },
  { value: "NWAmes", label: "Northwest Ames" },
  { value: "OldTown", label: "Old Town" },
  { value: "Sawyer", label: "Sawyer" },
  { value: "SawyerW", label: "Sawyer West" },
  { value: "Somerst", label: "Somerset" },
  { value: "SWISU", label: "South & West of Iowa State University" },
  { value: "StoneBr", label: "Stone Brook" },
  { value: "Timber", label: "Timberland" },
  { value: "Veenker", label: "Veenker" },
];

export const ZONING_OPTIONS: { value: string; label: string }[] = [
  { value: "RL", label: "Residential Low Density" },
  { value: "RM", label: "Residential Medium Density" },
  { value: "FV", label: "Floating Village Residential" },
  { value: "RH", label: "Residential High Density" },
  { value: "C (all)", label: "Commercial" },
];

export const KITCHEN_QUALITIES: { value: string; label: string }[] = [
  { value: "Ex", label: "Excellent (Ex)" },
  { value: "Gd", label: "Good (Gd)" },
  { value: "TA", label: "Typical/Average (TA)" },
  { value: "Fa", label: "Fair (Fa)" },
  { value: "Po", label: "Poor (Po)" },
];
