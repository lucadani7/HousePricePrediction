/**
 * Rounds a price to the nearest 100 dollars.
 * The model's typical error is ~7%, so showing cents would suggest false precision.
 */
export function roundToHundreds(price: number): number {
  return Math.round(price / 100) * 100;
}
