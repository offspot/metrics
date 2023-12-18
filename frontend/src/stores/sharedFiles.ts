import { useMainStore } from './main'
import { defineStore } from 'pinia'
import { kpiIds } from '../constants'
import SharedFilesKpiValue from '@/types/SharedFilesKpiValue'

export const useSharedFilesStore = defineStore('sharedFiles', {
  getters: {
    aggregationValue() {
      return useMainStore().aggregationValue
    },
    labels() {
      return useMainStore().getAllAggValues
    },
    values() {
      const mainStore = useMainStore()
      return mainStore.getAllAggValues?.map(
        (aggValue) =>
          mainStore.getKpiValue(kpiIds.sharedFiles, aggValue)
            ?.kpiValue as SharedFilesKpiValue,
      )
    },
  },
})
