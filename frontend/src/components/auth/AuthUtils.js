import axios from "@/configs/axios";

const API_AUTH_CHECK_URL = "/api/auth/check/";
const API_LOGIN_URL = "/api/auth/login/";
const API_LOGOUT_URL = "/api/auth/logout/";
const API_REGISTER_URL = "/api/auth/register/";

export const SUCCESS_MESSAGES = {
    SUCCESS_LOGIN: "Logged in successfully!",
}

export const ERROR_MESSAGES = {
    ERROR_INVALID_EMAIL: "Please enter a valid email address.",
    ERROR_NOT_RESPONSE: "Unable to connect to the server. Please try again later.",
    ERROR_CANNOT_REGISTER: "Registration could not be completed.",
    ERROR_CANNOT_LOGIN: "Failed to log in.",
}

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

export async function registerAPI(username, email, password) {
    return await axios.post(`${API_REGISTER_URL}`, {
        username: username,
        email: email,
        password: password,
    });
}