import {ERROR_MESSAGES} from "@/components/batch-job/utils/BatchJobUtils";

export function getErrorMessage(error, message) {
    if (error.response) {
        // Server responded with an error
        return `${message} ${error.response?.data?.error || error.response?.data?.detail || ERROR_MESSAGES.unableConnectServer}`;
    } else if (error.request) {
        // Request was made but no response received
        return `${ERROR_MESSAGES.unableConnectServer}`;
    } else if (error.message) {
        // Network error or General error
        return `Error: ${error.message}`;
    } else {
        // Unknown error
        return "An unknown error occurred.";
    }
}
