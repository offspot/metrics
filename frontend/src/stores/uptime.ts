import UptimeKpiValue from '@/types/UptimeKpiValue'
import { useMainStore } from './main'
import { defineStore } from 'pinia'
import { kpiIds } from '../constants'

// Hard-coded for now, to be reworked once we will need this also for the slider
const monthText = (monthDigit: string): string => {
  switch (monthDigit) {
    case '01':
      return 'January'
    case '02':
      return 'February'
    case '03':
      return 'March'
    case '04':
      return 'April'
    case '05':
      return 'May'
    case '06':
      return 'June'
    case '07':
      return 'July'
    case '08':
      return 'August'
    case '09':
      return 'September'
    case '10':
      return 'October'
    case '11':
      return 'November'
    case '12':
      return 'December'
    default:
      return ''
  }
}

export const useUptimeStore = defineStore('uptime', {
  getters: {
    aggregationKind() {
      const mainStore = useMainStore()
      return mainStore.aggregationKind
    },
    aggregationValue() {
      const mainStore = useMainStore()
      return mainStore.aggregationValue || ''
    },
    kpiValue() {
      const mainStore = useMainStore()
      return mainStore.getCurrentKpiValue(kpiIds.uptime)
        ?.kpiValue as UptimeKpiValue
    },
    series(): number[] {
      switch (this.aggregationKind) {
        case 'D':
          return [this.kpiValue.nbMinutesOn / 14.4]
        case 'W':
          return [this.kpiValue.nbMinutesOn / 100.8]
        case 'M':
          return [this.kpiValue.nbMinutesOn / 438]
        case 'Y':
          return [this.kpiValue.nbMinutesOn / 5256]
        default:
          return []
      }
    },
    legend(): string {
      const hours = this.kpiValue.nbMinutesOn / 60
      if (hours < 10) {
        return (this.kpiValue.nbMinutesOn / 60).toFixed(1) + 'h'
      } else {
        return (this.kpiValue.nbMinutesOn / 60).toFixed(0) + 'h'
      }
    },
    date_part_1(): string {
      switch (this.aggregationKind) {
        case 'D':
          return ''
        case 'W':
          return 'Week '
        case 'M':
          return ''
        case 'Y':
          return 'Year '
        default:
          return ''
      }
    },
    date_part_2(): string {
      switch (this.aggregationKind) {
        case 'D':
          return this.aggregationValue.split('-')[2] + ' '
        case 'W':
          if (this.aggregationValue.indexOf(' ') < 0) {
            return '' // Race condition where space is not yet available
          }
          return this.aggregationValue.split(' ')[1].substring(1) + ' '
        case 'M':
          return monthText(this.aggregationValue.split('-')[1]) + ' '
        case 'Y':
          return this.aggregationValue
        default:
          return ''
      }
    },
    date_part_3(): string {
      switch (this.aggregationKind) {
        case 'D':
          return (
            monthText(this.aggregationValue.split('-')[1]) +
            ' ' +
            this.aggregationValue.split('-')[0]
          )
        case 'W':
          return this.aggregationValue.split(' ')[0]
        case 'M':
          return this.aggregationValue.split('-')[0]
        case 'Y':
          return ''
        default:
          return ''
      }
    },
  },
})
