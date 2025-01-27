import axios from "@/configs/axios";

const API_AUTH_CHECK_URL = "/api/auth/check/";
const API_LOGIN_URL = "/api/auth/login/";
const API_LOGOUT_URL = "/api/auth/logout/";


export async function fetchAuthAPI() {
    const response = await axios.get(`${API_AUTH_CHECK_URL}`, {withCredentials: true});
    const data = response.data;

    return {
        isAuthenticated: data.is_authenticated,
        username: data.username,
        email: data.email,
        balance: data.balance,
    };
}

export async function loginAPI(email, password) {
    const response = await axios.post(`${API_LOGIN_URL}`, {
        email: email,
        password: password,
    });
    return response.data;
}

export async function logoutAPI() {
    await axios.post(`${API_LOGOUT_URL}`, {}, {withCredentials: true});
}