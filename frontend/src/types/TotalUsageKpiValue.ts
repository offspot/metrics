import TotalUsageKpiItem from './TotalUsageKpiItem'

/**
 * A value of the total usage Kpi
 */
export default interface TotalUsageKpiValue {
  items: TotalUsageKpiItem[]
  totalMinutesActivity: number
}
