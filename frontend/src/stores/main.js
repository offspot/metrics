import { defineStore } from 'pinia'
import axios from "axios"
export const useMainStore = defineStore('main', {
  state: () => ({
    aggregations: [],
    selected_agg_kind: null,
    agg_values_for_selected_agg_kind: [],
    selected_agg_value: null,
    selected_kpi_id: null,
    value_for_selected_kpi_id: null,
    is_loading: false,
    error: null,
  }),
  getters: {},
  actions: {
    handle_agg_kind_updated() {
      this.agg_values_for_selected_agg_kind = this.aggregations.filter(aggregation => aggregation.kind === this.selected_agg_kind).map(agg => agg.value)
      this.selected_agg_value = this.agg_values_for_selected_agg_kind[this.agg_values_for_selected_agg_kind.length - 1]
      this.fetchKpi()
    },
    update_kpi(value) {
      switch (value) {
        case 'Top contents':
          this.selected_kpi_id = 2001
          break;
        case 'Top 50 resources':
          this.selected_kpi_id = 2002
          break;
        default:
          this.selected_kpi_id = null
          this.error = `Unsupported KPI: '${value}'.`
          return
      }
      this.fetchKpi()
    },
    update_agg_kind(kind) {
      switch (kind) {
        case 'Daily':
          this.selected_agg_kind = 'D'
          break;
        case 'Weekly':
          this.selected_agg_kind = 'W'
          break;
        case 'Monthly':
          this.selected_agg_kind = 'M'
          break;
        case 'Yearly':
          this.selected_agg_kind = 'Y'
          break;
        default:
          this.selected_agg_kind = null
          this.error = `Unsupported aggregation kind: '${kind}'.`
          return
      }
      this.handle_agg_kind_updated()
    },
    update_agg_value(value) {
      this.selected_agg_value = value
      this.fetchKpi()
    },
    async fetchAggregations() {
      this.is_loading = true
      this.error = null
      try {
        const data = await axios.get(import.meta.env.VITE_BACKEND_ROOT_API + '/aggregations')
        this.aggregations = data.data.aggregations
        this.handle_agg_kind_updated()
      }
      catch (error) {
        this.error = "Failed to load aggregations"
        this.aggregations = []
        console.log(error)
      }
      this.is_loading = false
    },
    async fetchKpi() {
      this.is_loading = true
      this.error = null
      if (!this.selected_kpi_id || !this.selected_agg_kind || !this.selected_agg_value) {
        return
      }
      try {
        const data = await axios.get(import.meta.env.VITE_BACKEND_ROOT_API + '/kpis/' + this.selected_kpi_id + '/values?agg_kind=' + this.selected_agg_kind + '&agg_value=' + this.selected_agg_value )
        this.value_for_selected_kpi_id = data.data.value
      }
      catch (error) {
        this.error = "Failed to load KPI value"
        this.value_for_selected_kpi_id = null
        console.log(error)
      }
      this.is_loading = false
    },
  },
})