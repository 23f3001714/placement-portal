import api from './api'
import router from '../router/index'

function logout () {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    delete api.defaults.headers.common.Authorization
    router.push({name: 'login'})
}

export default logout;
