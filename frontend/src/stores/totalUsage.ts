import { useMainStore } from './main'
import { defineStore } from 'pinia'
import TotalUsageKpiValue from '@/types/TotalUsageKpiValue'
import TotalUsageKpiItem from '@/types/TotalUsageKpiItem'
import { kpiIds } from '../constants'

export const useTotalUsageStore = defineStore('totalUsage', {
  getters: {
    kpiValue() {
      const mainStore = useMainStore()
      return mainStore.getCurrentKpiValue(kpiIds.totalUsage)
        ?.kpiValue as TotalUsageKpiValue
    },
    totalValue(): string {
      const value = this.kpiValue.totalMinutesActivity / 60
      if (value < 10) {
        return value.toFixed(1)
      } else {
        return value.toFixed(0)
      }
    },
    items(): TotalUsageKpiItem[] {
      return this.kpiValue.items
    },
    firstItems(): TotalUsageKpiItem[] {
      return this.kpiValue.items.slice(0, 6)
    },
    itemPercentage(): (item: TotalUsageKpiItem) => number {
      return (item: TotalUsageKpiItem) =>
        (item.minutesActivity / this.kpiValue.totalMinutesActivity) * 100
    },
    itemLabel(): (item: TotalUsageKpiItem) => string {
      return (item: TotalUsageKpiItem) => {
        const value = item.minutesActivity / 60
        if (value < 10) {
          return value.toFixed(1) + 'h'
        } else {
          return value.toFixed(0) + 'h'
        }
      }
    },
    itemColor(): (item: TotalUsageKpiItem) => string {
      const mainStore = useMainStore()
      return (item: TotalUsageKpiItem) =>
        mainStore.getPackageColor(item.package)
    },
  },
})
