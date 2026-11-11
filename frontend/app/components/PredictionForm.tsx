"use client";

import React, { useState } from "react";
import {HouseFeatures} from "@/app/interfaces/HouseFeatures";
import {PredictionFormProps} from "@/app/interfaces/PredictionFormProps";
import {KITCHEN_QUALITIES, NEIGHBORHOODS, ZONING_OPTIONS} from "@/app/lib/options";
import {CARD_CLASS, CARD_TITLE_CLASS, SECTION_TITLE_CLASS} from "@/app/lib/styles";
import {NumberField, SelectField} from "@/app/components/FormFields";

export default function PredictionForm({ onPredict, isLoading }: PredictionFormProps) {
  const [formData, setFormData] = useState<HouseFeatures>({
    first_floor_sf: 1200,
    second_floor_sf: 800,
    total_bsmt_sf: 1000,
    bsmt_fin_sf1: 600,
    overall_quality: 7,
    overall_condition: 5,
    kitchen_quality: "Gd",
    year_built: 2005,
    year_remod_add: 2005,
    neighborhood: "CollgCr",
    ms_zoning: "RL",
    lot_area: 9500,
    garage_cars: 2,
    full_bath: 2,
    half_bath: 1,
    fireplaces: 1,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onPredict(formData);
  };

  return (
    <form onSubmit={handleSubmit} className={`${CARD_CLASS} space-y-6`}>
      <h2 className={CARD_TITLE_CLASS}>Property Features</h2>

      {/* One column on phones, two from the "md" breakpoint (768px) up */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 md:gap-8">
        <div className="space-y-4">
          <h3 className={SECTION_TITLE_CLASS}>Areas (sq ft)</h3>
          <NumberField name="first_floor_sf" label="1st floor" value={formData.first_floor_sf} onChange={handleChange} min={1} />
          <NumberField name="second_floor_sf" label="2nd floor (0 if none)" value={formData.second_floor_sf} onChange={handleChange} min={0} />
          <NumberField name="total_bsmt_sf" label="Basement, total (0 if none)" value={formData.total_bsmt_sf} onChange={handleChange} min={0} />
          <NumberField name="bsmt_fin_sf1" label="Basement, finished" value={formData.bsmt_fin_sf1} onChange={handleChange} min={0} />
          <NumberField name="lot_area" label="Lot area" value={formData.lot_area} onChange={handleChange} min={1} />

          <h3 className={`${SECTION_TITLE_CLASS} pt-2`}>Amenities</h3>
          <div className="grid grid-cols-2 gap-4">
            <NumberField name="garage_cars" label="Garage (cars)" value={formData.garage_cars} onChange={handleChange} min={0} max={5} />
            <NumberField name="fireplaces" label="Fireplaces" value={formData.fireplaces} onChange={handleChange} min={0} max={5} />
            <NumberField name="full_bath" label="Full baths" value={formData.full_bath} onChange={handleChange} min={0} max={5} />
            <NumberField name="half_bath" label="Half baths" value={formData.half_bath} onChange={handleChange} min={0} max={4} />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className={SECTION_TITLE_CLASS}>Quality &amp; details</h3>
          <div className="grid grid-cols-2 gap-4">
            <NumberField name="overall_quality" label="Overall quality (1-10)" value={formData.overall_quality} onChange={handleChange} min={1} max={10} />
            <NumberField name="overall_condition" label="Overall condition (1-10)" value={formData.overall_condition} onChange={handleChange} min={1} max={10} />
          </div>
          <SelectField name="kitchen_quality" label="Kitchen quality" value={formData.kitchen_quality} options={KITCHEN_QUALITIES} onChange={handleChange} />
          <div className="grid grid-cols-2 gap-4">
            <NumberField name="year_built" label="Year built" value={formData.year_built} onChange={handleChange} min={1800} />
            <NumberField name="year_remod_add" label="Year remodeled" value={formData.year_remod_add} onChange={handleChange} min={1800} />
          </div>

          <h3 className={`${SECTION_TITLE_CLASS} pt-2`}>Location</h3>
          <SelectField name="neighborhood" label="Neighborhood" value={formData.neighborhood} options={NEIGHBORHOODS} onChange={handleChange} />
          <SelectField name="ms_zoning" label="Zoning" value={formData.ms_zoning} options={ZONING_OPTIONS} onChange={handleChange} />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-lg bg-zinc-900 px-4 py-3 font-medium text-white transition-colors hover:bg-zinc-700 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
      >
        {isLoading ? "Calculating price..." : "Estimate house price"}
      </button>
    </form>
  );
}
