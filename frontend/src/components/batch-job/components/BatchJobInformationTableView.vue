<template>
  <div class="col-lg-6 mb-4 mb-lg-0">
    <table class="table table-bordered table-hover align-middle" style="table-layout: fixed;">
      <colgroup>
        <col style="width: 30%;"/>
        <col style="width: 70%;"/>
      </colgroup>
      <thead class="table-light">
      <tr>
        <th class="text-center text-primary" colspan="2">{{ title }}</th>
      </tr>
      </thead>
      <tbody>
      <tr>
        <th>Title</th>
        <td>{{ batchJob.title }}</td>
      </tr>
      <tr>
        <th>Desc</th>
        <td>{{ batchJob.description }}</td>
      </tr>
      <tr>
        <th>File</th>
        <td>{{ batchJob.file_name }}</td>
      </tr>
      <tr>
        <th>Total Size</th>
        <td>{{ batchJob.total_size }}</td>
      </tr>
      <tr>
        <th>Status</th>
        <td>
            <span :class="{
              'badge bg-success': batchJob.batch_job_status === 'Completed',
              'badge bg-warning text-dark': batchJob.batch_job_status === 'In Progress',
              'badge bg-danger': batchJob.batch_job_status === 'Failed',
              'badge bg-secondary': !['Completed', 'In Progress', 'Failed'].includes(batchJob.batch_job_status)
            }">
              {{ batchJob.batch_job_status }}
            </span>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: "General Information",
    },
    batchJob: Object,
  },
};
</script>
