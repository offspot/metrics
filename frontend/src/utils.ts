/*
 * Get a random Hex color in our color scheme, to be used in CSS
 */
export const getRandomColor = (): string => {
  /*
    Color scheme is from https://venngage.com/tools/accessible-color-palette-generator#colorGenerator
    We selected colors mostly randomly
  */
  const colorScheme = [
    '#00bf7d',
    '#00b4c5',
    '#f57600',
    '#8babf1',
    '#e6308a',
    '#89ce00',
    '#e6308a',
    '#9b8bf4',
    '#606ff3',
    '#9b8bf4',
  ]
  return colorScheme[Math.floor(Math.random() * colorScheme.length)]
}
