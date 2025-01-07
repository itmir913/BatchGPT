// batchJobUtils.js
export const EDIT_DISABLED_STATUSES = ['IN_PROGRESS', 'COMPLETED', 'FAILED'];

export function isEditDisabled(status) {
    return EDIT_DISABLED_STATUSES.includes(status);
}
