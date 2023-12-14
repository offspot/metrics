import PackagePopularityKpiItem from './PackagePopularityKpiItem'

/**
 * A value of the package popularity Kpi
 */
export default interface PackagePopularityKpiValue {
  items: PackagePopularityKpiItem[]
  totalVisits: number
}
