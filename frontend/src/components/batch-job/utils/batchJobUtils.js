// batchJobUtils.js
export const EDIT_DISABLED_STATUSES = ['IN_PROGRESS', 'COMPLETED', 'FAILED'];

export function isEditDisabled(status) {
    return EDIT_DISABLED_STATUSES.includes(status);
}

export function shouldDisableRunButton(batch_job_status) {
    return !["CONFIGS", "COMPLETED", "FAILED"].includes(batch_job_status);
}

export function shouldDisplayResults(batch_job_status) {
    return !["COMPLETED", "FAILED"].includes(batch_job_status);
}
