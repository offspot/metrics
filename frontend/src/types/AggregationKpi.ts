import AggregationKpiValue from './AggregationKpiValue'

/**
 * Details about all aggregations for a given Kpi
 */
export default interface AggregationKpi {
  kpiId: number
  values: AggregationKpiValue[]
}
