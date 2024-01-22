import UptimeKpiValue from '@/types/UptimeKpiValue'
import { useMainStore } from './main'
import { defineStore } from 'pinia'
import { kpiIds } from '../constants'

export const useUptimeStore = defineStore('uptime', {
  getters: {
    aggregationKind() {
      return useMainStore().aggregationKind
    },
    kpiValue() {
      return useMainStore().getCurrentKpiValue(kpiIds.uptime)
        ?.kpiValue as UptimeKpiValue
    },
    series(): number[] {
      // return the uptime as percentage of the whole aggregation
      switch (this.aggregationKind) {
        case 'D':
          // whole aggregation is 60 min * 24 hours = 1440 mins
          return [this.kpiValue.nbMinutesOn / 14.4]
        case 'W':
          // whole aggregation is 7 days * 60 min * 24 hours = 10080 mins
          return [this.kpiValue.nbMinutesOn / 100.8]
        case 'M':
          // whole aggregation is 365 days * 60 min * 24 hours / 12 months = 43800 mins
          // nota: this is an average, but we do not mind for now
          return [this.kpiValue.nbMinutesOn / 438]
        case 'Y':
          // whole aggregation is 365 days * 60 min * 24 hours / 12 months = 525600 mins
          // nota: this is an average (some years have 366 days), but we do not mind for now
          return [this.kpiValue.nbMinutesOn / 5256]
        default:
          return []
      }
    },
    legend(): string {
      const hours = this.kpiValue.nbMinutesOn / 60
      if (hours < 10) {
        return `${(this.kpiValue.nbMinutesOn / 60).toFixed(1)}h`
      } else {
        return `${(this.kpiValue.nbMinutesOn / 60).toFixed(0)}h`
      }
    },
  },
})
