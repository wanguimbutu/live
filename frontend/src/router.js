import { createRouter, createWebHistory } from '@ionic/vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'
import Tabs from './components/tabs.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/frontend',
    component: Tabs,
    children:[
      {
        path:'/frontend/homepage',
        redirect:'/homePage'
      },
      {
        path:'/homePage',
        component: () => import('@/pages/HomePage.vue'),
      },
      {
        path:'/salesOrderList',
        component: () => import('@/pages/SalesOrderList.vue'),
      },
      {
        path:'/customerList',
        component: () => import('@/pages/CustomerList.vue'),
      },
      {
        path:'/attendance',
        component: () => import('@/pages/Attendance.vue')
      },
      {
        path: '/add-sales-order',
        //name: 'AddSalesOrder',
        component: () => import('@/pages/AddSalesOrder.vue'),
      },
      {
        path: '/order/:id',
        name: 'OrderDetails',
        component: () => import('@/components/OrderDetails.vue'), // Adjust the path as needed
        props: true,
      },
      {
        path: '/add-customer',
        component: () => import('@/pages/NewCustomer.vue'),
      }
    ]
  }
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
