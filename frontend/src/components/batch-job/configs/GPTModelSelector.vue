<template>
  <div class="p-2 mb-3">
    <h2 class="mb-3">Select GPT Model</h2>
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
      <div v-for="(model, key) in available_models" :key="'model-' + key" class="col-md-4">
        <div :class="{'border-primary': localGptModel === key}"
             class="card shadow-sm clickable-card"
             @click="selectModel(key)">
          <div class="card-body d-flex flex-column justify-content-center text-center">
            <input id="model" v-model="localGptModel"
                   :disabled="disabled"
                   :value="key"
                   class="form-check-input"
                   style="display: none;"
                   type="radio"/>
            <label :for="key" class="form-check-label">{{ model }}</label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    available_models: {
      type: Object,
      required: true,
    },
    gpt_model: {
      type: String,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      localGptModel: this.gpt_model, // Local copy of the model
    };
  },
  watch: {
    // Watch localGptModel and emit changes to parent
    localGptModel(newVal) {
      this.$emit('update:gpt_model', newVal);
    },
  },
  methods: {
    selectModel(model) {
      if (!this.disabled) {
        this.localGptModel = model; // Set local model
      }
    },
  },
};
</script>

<!-- GPT 모델 선택 카드 -->
<style scoped>
.card {
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
  font-size: 0.9rem;
}

.card:hover {
  transform: scale(1.05);
}

.card-body {
  padding: 1.25rem;
}
</style>
