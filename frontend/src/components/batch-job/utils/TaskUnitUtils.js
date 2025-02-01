export const TASK_UNIT_STATUS = {
    PENDING: 'Pending',
    IN_PROGRESS: 'In Progress',
    COMPLETED: 'Completed',
    FAILED: 'Failed',
}

export function completedTaskUnit(status) {
    return [TASK_UNIT_STATUS.COMPLETED, TASK_UNIT_STATUS.FAILED].includes(status);
}
