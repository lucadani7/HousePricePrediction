import {NumberFieldProps, SelectFieldProps} from "@/app/interfaces/FormFieldProps";
import {INPUT_CLASS, LABEL_CLASS} from "@/app/lib/styles";

export function NumberField({ name, label, value, onChange, min, max }: NumberFieldProps) {
  return (
    <div>
      <label htmlFor={name} className={LABEL_CLASS}>{label}</label>
      <input
        id={name}
        name={name}
        type="number"
        inputMode="numeric"
        min={min}
        max={max}
        value={value}
        onChange={onChange}
        className={INPUT_CLASS}
        required
      />
    </div>
  );
}

export function SelectField({ name, label, value, options, onChange }: SelectFieldProps) {
  return (
    <div>
      <label htmlFor={name} className={LABEL_CLASS}>{label}</label>
      <select id={name} name={name} value={value} onChange={onChange} className={INPUT_CLASS}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
    </div>
  );
}
