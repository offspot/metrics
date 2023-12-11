import { defineStore } from 'pinia'
import axios from 'axios'
import AggregationDetails from '@/types/AggregationDetails'
import AggregationKpiValue from '@/types/AggregationKpiValue'
import { getRandomColor } from '../utils'
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
    }) as RootState,
  getters: {
    aggregationValue: (state) =>
      state.aggregationsDetails
        ? state.aggregationsDetails.valuesAvailable[state.aggregationValueIndex]
        : null,
    hasNextAggregationValue: (state) =>
      state.aggregationsDetails
        ? state.aggregationValueIndex <
          state.aggregationsDetails.valuesAvailable.length - 1
        : false,
    hasPrevAggregationValue: (state) => state.aggregationValueIndex > 0,
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
    getCurrentKpiValue() {
      return (kpiId: number): AggregationKpiValue | null => {
        const currentValues = this.getAllKpiValues(kpiId)
        if (!currentValues) {
          return null
        }
        const kpisMatch = currentValues.filter(
          (value) => value.aggValue == this.aggregationValue,
        )
        if (kpisMatch.length != 1) {
          return null
        }
        return kpisMatch[0]
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
  },
  actions: {
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
