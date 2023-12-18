import { useMainStore } from './main'
import { defineStore } from 'pinia'
import PackagePopularityKpiValue from '@/types/PackagePopularityKpiValue'
import PackagePopularityKpiItem from '@/types/PackagePopularityKpiItem'
import { kpiIds } from '../constants'

export const usePackagePopularityStore = defineStore('packagePopularity', {
  getters: {
    kpiValue() {
      return useMainStore().getCurrentKpiValue(kpiIds.packagePopularity)
        ?.kpiValue as PackagePopularityKpiValue
    },
    items(): PackagePopularityKpiItem[] {
      return this.kpiValue.items
    },
    firstItems(): PackagePopularityKpiItem[] {
      return this.kpiValue.items.slice(0, 6)
    },
    itemPercentage(): (item: PackagePopularityKpiItem) => number {
      return (item: PackagePopularityKpiItem) =>
        (item.visits / this.kpiValue.totalVisits) * 100
    },
    itemPercentageLabel(): (item: PackagePopularityKpiItem) => string {
      return (item: PackagePopularityKpiItem) => {
        const value = this.itemPercentage(item)
        if (value < 10) {
          return value.toFixed(1) + '%'
        } else {
          return value.toFixed(0) + '%'
        }
      }
    },
    itemLabel(): (item: PackagePopularityKpiItem) => string {
      return (item: PackagePopularityKpiItem) => '' + item.visits
    },
    itemColor(): (item: PackagePopularityKpiItem) => string {
      return (item: PackagePopularityKpiItem) =>
        useMainStore().getPackageColor(item.package)
    },
  },
})
