import AggregationKpi from './AggregationKpi'

/**
 * Details about a given kind of aggregation with its values and Kpis for each of them
 */
export default interface AggregationDetails {
  aggKind: string
  valuesAvailable: string[]
  valuesAll: string[]
  kpis: AggregationKpi[]
}
