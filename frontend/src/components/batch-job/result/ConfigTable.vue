<template>
  <div v-if="configs" class="col-lg-6">
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
      <tr v-for="(value, key) in configs" :key="key">
        <th>{{ formatKey(key) }}</th>
        <td>
            <span v-if="Array.isArray(value)" class="badge bg-light text-dark">
              {{ value.join(', ') }}
            </span>
          <span v-else>
              {{ value }}
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
      default: "Configurations",
    },
    configs: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatKey(key) {
      return key
          .replace(/_/g, ' ')  // 언더스코어(_)를 공백으로 변경
          .replace(/\b\w/g, char => char.toUpperCase());  // 첫 글자 대문자로 변환
    },
  }
};
</script>
