// BatchJobUtils.js
import axios from "@/configs/axios";

export const API_BASE_URL = "/api/batch-jobs/";
const API_CREATE_URL = `${API_BASE_URL}create/`;
const API_FILE_TYPES_URL = `${API_BASE_URL}supported-file-types/`;
const API_PDF_MODE_URL = `${API_BASE_URL}supported-pdf-modes/`;
const API_UPLOAD = `/upload/`;
const API_CONFIG_URL = "/configs/";
const API_PREVIEW_POSTFIX = "/preview/";
export const API_TASK_UNITS_URL = "/task-units/";
const API_BATCH_JOB_RUN_URL = "/run/";


export const SUCCESS_MESSAGES = {
    updatedConfigs: "Configuration updated successfully.",
    modifyBatchJob: "Batch job modified successfully!",
    deleteBatchJob: "Batch job deleted successfully!",
    pendingTasks: "The batch job will start soon.",
    runTasks: "Batch job started successfully!",
    uploadFile: "File uploaded successfully!",
    loadPreviewResult: "Preview requested successfully. The result will be available shortly.",
}

export const ERROR_MESSAGES = {
    unableConnectServer: "Failed to connect to the server.",
    fetchBatchJobList: "Failed to fetch batch jobs.",
    fetchBatchJobDetail: "Failed to load batch job details.",
    modifyBatchJob: "Error modifying batch job.",
    deleteBatchJob: "Error deleting batch job.",
    fileTypes: "Failed to retrieve supported file types from the server.",
    uploadFile: "Error uploading the file.",
    unsupportedFileType: "Unsupported file type. Allowed types:",
    missingFile: "No file selected. Please choose a file to upload.",
    compressFiles: "Failed to compress the file.",
    updatedConfigs: "Error updating configuration.",
    loadPreview: "Failed to load preview data.",
    noColumn: "Please select at least one column.",
    emptyPrompt: "Prompt cannot be empty.",
    noWorkUnit: "Work unit must be at least 1.",
    noDataReceived: "No data received from the server.",
    loadResult: "Failed to load preview data.",
    fetchTasks: "Error fetching tasks.",
    pendingTasks: "Error starting tasks.",
}

export const CONFIRM_MESSAGE = {
    loadingMessage: "Loading data, please wait...",
    deleteBatchJob: "Are you sure you want to delete this batch job?",
}


export const BATCH_JOB_STATUS = {
    CREATED: 'Created',
    UPLOADED: 'Uploaded',
    CONFIGS: 'Standby',
    PENDING: 'Pending',
    IN_PROGRESS: 'In Progress',
    COMPLETED: 'Completed',
    FAILED: 'Failed',
}


export function getStepLink(index, batch_id) {
    const stepLinks = [
        `/batch-jobs/create`,
        `/batch-jobs/${batch_id}`,
        `/batch-jobs/${batch_id}/configs`,
        `/batch-jobs/${batch_id}/preview`,
        `/batch-jobs/${batch_id}/run`,
    ];
    return stepLinks[index] || '/';
}

export function getEditLink(batch_id) {
    return `/batch-jobs/${batch_id}/edit`;
}

export function getJobLink(job) {
    switch (job.batch_job_status) {
        case BATCH_JOB_STATUS.PENDING:
        case BATCH_JOB_STATUS.IN_PROGRESS:
        case BATCH_JOB_STATUS.COMPLETED:
        case BATCH_JOB_STATUS.FAILED:
            return getStepLink(4, job.id);
        case BATCH_JOB_STATUS.UPLOADED:
            return getStepLink(2, job.id);
        case BATCH_JOB_STATUS.CONFIGS:
            return getStepLink(3, job.id);
        case BATCH_JOB_STATUS.CREATED:
        default:
            return getStepLink(1, job.id);
    }
}

export function shouldEditDisabled(status) {
    return [BATCH_JOB_STATUS.PENDING, BATCH_JOB_STATUS.IN_PROGRESS].includes(status);
}

export function shouldDisableRunButton(batch_job_status) {
    return ![BATCH_JOB_STATUS.PENDING, BATCH_JOB_STATUS.IN_PROGRESS].includes(batch_job_status);
}

export function shouldDisplayResults(batch_job_status) {
    return [BATCH_JOB_STATUS.IN_PROGRESS, BATCH_JOB_STATUS.COMPLETED, BATCH_JOB_STATUS.FAILED].includes(batch_job_status);
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
        throw new Error(ERROR_MESSAGES.fetchBatchJobDetail);
    }

    return response.data;
}

export async function fetchBatchJobTitleAPI(batch_id) {
    const response = await axios.get(`${API_BASE_URL}${batch_id}/`, {withCredentials: true});
    if (!response.data) {
        throw new Error(ERROR_MESSAGES.fetchBatchJobDetail);
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

export async function fetchPDFSupportedModeAPI() {
    const response = await axios.get(`${API_PDF_MODE_URL}`, {withCredentials: true});
    return Object.values(response.data.modes)
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
        throw new Error(ERROR_MESSAGES.fetchBatchJobDetail);
    }

    const configs = response.data.configs ?? {};
    return {
        batchJob: response.data,
        configs: configs,
    };
}

export async function modifyBatchJobConfigsAPI(batch_id, payload) {
    const response = await axios.patch(`${API_BASE_URL}${batch_id}${API_CONFIG_URL}`, payload, {withCredentials: true});

    const configs = response.data.configs ?? {};
    return {
        batchJob: response.data,
        configs: configs,
    };
}

export async function fetchPreviewAPI(batch_id) {
    const response = await axios.get(`${API_BASE_URL}${batch_id}${API_PREVIEW_POSTFIX}`, {withCredentials: true});
    return response.data;
}

export async function checkTaskUnitStatus(batchJobId, taskUnitId) {
    return await axios.get(`${API_BASE_URL}${batchJobId}${API_TASK_UNITS_URL}${taskUnitId}/`);
}


export function getPageFromUrl(url) {
    const urlParams = new URLSearchParams(new URL(url).search);
    return urlParams.get('page') || null;
}

export function fetchTaskAPIUrl(batch_id, page) {
    if (page === null || page === 1) {
        return `${API_BASE_URL}${batch_id}${API_TASK_UNITS_URL}`;
    } else {
        return `${API_BASE_URL}${batch_id}${API_TASK_UNITS_URL}?page=${page}`;
    }
}

export async function fetchTasksAPI(nextPage) {
    const response = await axios.get(nextPage, {withCredentials: true});
    const data = response.data;

    return {
        tasks: data.results,
        nextPage: data.next !== null ? getPageFromUrl(data.next) : null,
        totalPages: Math.ceil(data.count / 100),
        hasMore: !!data.next,
    };
}

export async function runBatchJobProcess(batch_id) {
    const response = await axios.post(`${API_BASE_URL}${batch_id}${API_BATCH_JOB_RUN_URL}`, {withCredentials: true});
    return response.data
}

export async function fetchBatchJobProcessStatus(batch_id) {
    return await axios.get(`${API_BASE_URL}${batch_id}${API_BATCH_JOB_RUN_URL}`, {withCredentials: true});
}