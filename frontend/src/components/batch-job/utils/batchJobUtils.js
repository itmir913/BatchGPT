// batchJobUtils.js
export const EDIT_DISABLED_STATUSES = ['In Progress', 'Completed', 'Failed'];

export function isEditDisabled(status) {
    return EDIT_DISABLED_STATUSES.includes(status);
}
