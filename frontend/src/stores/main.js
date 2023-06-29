import { defineStore } from 'pinia'
import axios from "axios"
export const useMainStore = defineStore('main', {
  state: () => ({
    count: 0,
    users: [],
  }),
  getters: {
    doubleCount: (state) => state.count * 2,
    getUsers: (state) => state.users,
  },
  actions: {
    increment() {
      this.count++
    },
    async fetchUsers() {
      try {
        const data = await axios.get('https://jsonplaceholder.typicode.com/users')
        this.users = data.data
      }
      catch (error) {
        alert(error)
        console.log(error)
      }
    }
  },
})