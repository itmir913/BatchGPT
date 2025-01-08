// batchJobUtils.js
import axios from "@/configs/axios";

const API_BASE_URL = "/api/batch-jobs/";
const API_CREATE_URL = `${API_BASE_URL}create/`;
const API_FILE_TYPES_URL = `${API_BASE_URL}supported-file-types/`;
const API_UPLOAD = `/upload/`;
const API_CONFIG_URL = "/configs/";
const API_PREVIEW_POSTFIX = "/preview/";
const API_TASK_UNITS_URL = "/task-units/";


export const SUCCESS_MESSAGES = {
    updatedConfigs: "Configuration updated successfully.",
    modifyBatchJob: "Batch Job modified successfully!",
    deleteBatchJob: "Batch Job deleted successfully!",
    uploadFile: "File uploaded successfully!",
    loadPreviewResult: "The preview has been requested; the result will be available in a moment.",
};
export const ERROR_MESSAGES = {
    fetchBatchJob: "Failed to load Batch Job details. Please try again later.",
    modifyBatchJob: "Error modifying Batch Job: ",
    deleteBatchJob: "Error deleting batch job: ",
    fileTypes: "Failed to retrieve the types of files supported by the server. Please try again later.",
    uploadFile: "Error uploading file: ",
    missingFile: "The uploaded file is missing. Please select a file to upload.",
    updatedConfigs: "Error updating configuration. Please try again later.",
    loadPreview: "Failed to load Preview data. Please try again later.",
    noColumn: "Please select at least one column.",
    emptyPrompt: "Prompt cannot be empty.",
    noDataReceived: "No data received from Server.",
    loadResult: "Failed to load Preview data. Please try again later.",
    fetchTasks: "Error fetching tasks. Please try again later."
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

export async function createBatchJobAPI(payload) {
    const response = await axios.post(API_CREATE_URL, payload);
    const batch_id = response.data.id;

    return {
        batch_id: batch_id,
    };
}

export async function fetchBatchJobListAPI() {
    const response = await axios.get(`${API_BASE_URL}`, {withCredentials: true});
    if (!response.data) {
        throw new Error(ERROR_MESSAGES.fetchBatchJob);
    }

    return response.data;
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

export async function deleteBatchJobTitleAPI(batch_id) {
    await axios.delete(`${API_BASE_URL}${batch_id}/`, {withCredentials: true});
}

export async function fetchFileTypesAPI() {
    const response = await axios.get(`${API_FILE_TYPES_URL}`, {withCredentials: true});
    return Object.values(response.data)
}

export async function uploadFilesAPI(batch_id, selectedFile) {
    const formData = new FormData();
    formData.append("file", selectedFile);
    const response = await axios.patch(
        `${API_BASE_URL}${batch_id}${API_UPLOAD}`,
        formData,
        {headers: {"Content-Type": "multipart/form-data"}, withCredentials: true}
    );

    return response.data;
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

export async function fetchPreviewAPI(batch_id, payload) {
    const response = await axios.post(`${API_BASE_URL}${batch_id}${API_PREVIEW_POSTFIX}`, payload, {withCredentials: true});
    return response.data;
}

export async function fetchPreviewResultsAPI(batch_id) {
    const response = await axios.get(`${API_BASE_URL}${batch_id}${API_PREVIEW_POSTFIX}`, {withCredentials: true});
    return typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
}

export async function fetchTasksAPI(batch_id) {
    const response = await axios.get(`${API_BASE_URL}${batch_id}${API_TASK_UNITS_URL}`, {withCredentials: true});
    const data = response.data;

    return {
        tasks: data.results,
        nextPage: data.next,
        hasMore: !!data.next,
    };
}