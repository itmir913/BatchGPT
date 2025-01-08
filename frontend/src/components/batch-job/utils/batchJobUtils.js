// batchJobUtils.js
import axios from "@/configs/axios";

const API_BASE_URL = "/api/batch-jobs/";
const API_CONFIG_URL = "/configs/";


export const SUCCESS_MESSAGES = {
    updatedConfigs: "Configuration updated successfully.",
    modifyBatchJob: "Batch Job modified successfully!",
    loadPreviewResult: "The preview has been requested; the result will be available in a moment.",
};
export const ERROR_MESSAGES = {
    fetchBatchJob: "Failed to load Batch Job details. Please try again later.",
    modifyBatchJob: "Error modifying Batch Job: ",
    updatedConfigs: "Error updating configuration. Please try again later.",
    loadPreview: "Failed to load Preview data. Please try again later.",
    noColumn: "Please select at least one column.",
    emptyPrompt: "Prompt cannot be empty.",
    noDataReceived: "No data received from Server.",
    loadResult: "Failed to load Preview data. Please try again later.",
};

const EDIT_DISABLED_STATUSES = ['IN_PROGRESS', 'COMPLETED', 'FAILED'];

export function isEditDisabled(status) {
    return EDIT_DISABLED_STATUSES.includes(status);
}

export function shouldDisableRunButton(batch_job_status) {
    return !["CONFIGS", "COMPLETED", "FAILED"].includes(batch_job_status);
}

export function shouldDisplayResults(batch_job_status) {
    return ["COMPLETED", "FAILED"].includes(batch_job_status);
}

export async function fetchBatchJobTitleAPI(batch_id) {
    const response = await axios.get(`${API_BASE_URL}${batch_id}/`, {withCredentials: true});
    if (!response.data) {
        throw new Error(ERROR_MESSAGES.fetchBatchJob);
    }

    return response.data;
}

export async function modifyBatchJobTitleAPI(batch_id, payload) {
    await axios.patch(`${API_BASE_URL}${batch_id}/`, payload, {withCredentials: true});
}

export async function fetchBatchJobConfigsAPI(batch_id) {
    const response = await axios.get(`${API_BASE_URL}${batch_id}${API_CONFIG_URL}`, {withCredentials: true});
    if (!response.data) {
        throw new Error(ERROR_MESSAGES.fetchBatchJob);
    }

    const config = response.data.config ?? {};
    return {
        batchJob: response.data,
        configs: config,
    };
}

export async function modifyBatchJobConfigsAPI(batch_id, payload) {
    const response = await axios.patch(`${API_BASE_URL}${batch_id}${API_CONFIG_URL}`, payload, {withCredentials: true});

    const config = response.data.config ?? {};
    return {
        batchJob: response.data,
        configs: config,
    };
}
