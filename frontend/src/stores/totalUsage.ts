import { useMainStore } from './main'
import { defineStore } from 'pinia'
import TotalUsageKpiValue from '@/types/TotalUsageKpiValue'
import TotalUsageKpiItem from '@/types/TotalUsageKpiItem'
import { kpiIds } from '../constants'

export const useTotalUsageStore = defineStore('totalUsage', {
  getters: {
    kpiValue() {
      return useMainStore().getCurrentKpiValue(kpiIds.totalUsage)
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
    valueInHours(): (minutes: number) => number {
      return (minutes: number) => {
        const value = minutes / 60
        if (value < 10) {
          return parseFloat(value.toFixed(1))
        } else {
          return parseFloat(value.toFixed(0))
        }
      }
    },
    itemLabel(): (item: TotalUsageKpiItem) => string {
      return (item: TotalUsageKpiItem) => {
        return `${this.valueInHours(item.minutesActivity)}h`
      }
    },
    itemColor(): (item: TotalUsageKpiItem) => string {
      return (item: TotalUsageKpiItem) =>
        useMainStore().getPackageColor(item.package)
    },
    packageColor(): (packageName: string) => string {
      return (packageName: string) =>
        useMainStore().getPackageColor(packageName)
    },
  },
})
