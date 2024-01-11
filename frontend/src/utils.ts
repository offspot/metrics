/*
 * Get a random Hex color in our color scheme, to be used in CSS
 */
export const getRandomColor = (): string => {
  /*
    Color scheme is from https://sashamaps.net/docs/resources/20-colors/
    We selected colors which are differentiable for 99% of the population and just didn't used
    the white which was hard to see in our design.
  */
  const colorScheme = [
    '#e6194B',
    '#3cb44b',
    '#ffe119',
    '#4363d8',
    '#f58231',
    '#42d4f4',
    '#f032e6',
    '#fabed4',
    '#469990',
    '#dcbeff',
    '#9A6324',
    '#fffac8',
    '#800000',
    '#aaffc3',
    '#000075',
    '#a9a9a9',
    '#000000',
  ]
  return colorScheme[Math.floor(Math.random() * colorScheme.length)]
}
