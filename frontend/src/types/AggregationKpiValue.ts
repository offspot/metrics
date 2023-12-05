import PackagePopularityKpiValue from './PackagePopularityKpiValue'
import SharedFilesKpiValue from './SharedFilesKpiValue'
import TotalUsageKpiValue from './TotalUsageKpiValue'
import UptimeKpiValue from './UptimeKpiValue'

/**
 * An aggregation Kpi Value
 */
export default interface AggregationKpiValue {
  aggValue: string
  kpiValue:
    | PackagePopularityKpiValue
    | TotalUsageKpiValue
    | SharedFilesKpiValue
    | UptimeKpiValue
}
