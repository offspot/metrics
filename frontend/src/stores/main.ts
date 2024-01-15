import { defineStore } from 'pinia'
import axios from 'axios'
import AggregationDetails from '@/types/AggregationDetails'
import AggregationKpiValue from '@/types/AggregationKpiValue'
import { getRandomColor } from '../utils'

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

export enum Page {
  Dashboard,
  TotalUsage,
  PackagePopularity,
}
export type RootState = {
  aggregationKind: string
  aggregationValueIndex: number
  aggregationsDetails: AggregationDetails | null
  isLoading: boolean
  errorMessage: string | null
  currentPage: Page
  packagesColors: { [id: string]: string }
  drawerVisible: boolean
}
export const useMainStore = defineStore('main', {
  state: () =>
    ({
      aggregationKind: 'D',
      aggregationValueIndex: 0,
      aggregationsDetails: null,
      isLoading: false,
      errorMessage: null,
      currentPage: Page.Dashboard,
      packagesColors: {},
      drawerVisible: true,
    }) as RootState,
  getters: {
    aggregationValue: (state) =>
      state.aggregationsDetails
        ? state.aggregationsDetails.valuesAvailable[state.aggregationValueIndex]
        : '',
    hasNextAggregationValue: (state) =>
      state.aggregationsDetails
        ? state.aggregationValueIndex <
          state.aggregationsDetails.valuesAvailable.length - 1
        : false,
    hasPrevAggregationValue: (state) => state.aggregationValueIndex > 0,
    getAllAggValues(state) {
      if (!state.aggregationsDetails) {
        return null
      }
      return state.aggregationsDetails.valuesAll
    },
    getAllKpiValues(state) {
      return (kpiId: number): AggregationKpiValue[] | null => {
        if (!state.aggregationsDetails || !this.aggregationValue) {
          return null
        }
        const kpisMatch = state.aggregationsDetails.kpis.filter(
          (kpi) => kpi.kpiId == kpiId,
        )
        if (kpisMatch.length != 1) {
          return null
        }
        return kpisMatch[0].values
      }
    },
    getKpiValue() {
      return (
        kpiId: number,
        aggregationValue: string,
      ): AggregationKpiValue | null => {
        const currentValues = this.getAllKpiValues(kpiId)
        if (!currentValues) {
          return null
        }
        const kpisMatch = currentValues.filter(
          (value) => value.aggValue == aggregationValue,
        )
        if (kpisMatch.length != 1) {
          return null
        }
        return kpisMatch[0]
      }
    },
    getCurrentKpiValue() {
      return (kpiId: number): AggregationKpiValue | null => {
        if (!this.aggregationValue) {
          return null
        }
        return this.getKpiValue(kpiId, this.aggregationValue)
      }
    },
    getPackageColor(state) {
      // for now, package color is purely random ; later, it will be stored in database
      // and customisable (see #56 and #57)
      return (packageName: string): string => {
        if (!(packageName in state.packagesColors)) {
          state.packagesColors[packageName] = getRandomColor()
        }
        return state.packagesColors[packageName]
      }
    },
    /*
      The date displayed on the uptime tile is splitted in 3 parts:
      - date_part_1 which is in normal font weight
      - date_part_2 which is in bold font weight
      - date_part_3 which is in normal font weight
      All three are computed based on current aggregation kind and value,
      based on our internal convention on aggregation values formats.
    */
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
    // See above
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
    // See above
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
    // See above
    date_part_3_short(): string {
      switch (this.aggregationKind) {
        case 'D': {
          let month = monthText(this.aggregationValue.split('-')[1])
          if (month.length > 3) {
            month = month.substring(0, 3) + '.'
          }
          return month + ' ' + this.aggregationValue.split('-')[0]
        }
        case 'W':
          return ''
        case 'M':
          return this.aggregationValue.split('-')[0]
        case 'Y':
          return ''
        default:
          return ''
      }
    },
  },
  actions: {
    setDrawerVisibility(value: boolean) {
      this.drawerVisible = value
    },
    toggleDrawerVisibility() {
      this.drawerVisible = !this.drawerVisible
    },
    toNextAggregationValue() {
      this.aggregationValueIndex++
    },
    toPreviousAggregrationValue() {
      this.aggregationValueIndex--
    },
    setAggregationKind(kind: string) {
      this.aggregationKind = kind
      this.fetchAggregationDetails()
    },
    async fetchAggregationDetails() {
      this.isLoading = true
      this.errorMessage = null
      try {
        const data = await axios.get(
          import.meta.env.VITE_BACKEND_ROOT_API +
            '/aggregations/' +
            this.aggregationKind,
        )
        this.aggregationsDetails = data.data
        this.aggregationValueIndex = this.aggregationsDetails
          ? this.aggregationsDetails.valuesAvailable.length - 1
          : -1
      } catch (error) {
        this.errorMessage = 'Failed to load aggregations details'
        this.aggregationsDetails = null
        // this is temporary until we have implemented proper error display
        // in the UI.
        // eslint-disable-next-line no-console
        console.log(error)
      }
      this.isLoading = false
    },
  },
})
