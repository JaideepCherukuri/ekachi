<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="width"
    :height="height"
    viewBox="0 0 124 38"
    fill="none"
    role="img"
    aria-label="Ekachi"
  >
    <text
      x="0"
      y="26"
      fill="var(--logo-color)"
      font-family="Georgia, 'Times New Roman', serif"
      font-size="26"
      font-weight="700"
      letter-spacing="0.6"
    >
      Ekachi
    </text>
  </svg>
</template>

<script setup lang="ts">
defineProps({
  width: {
    type: [String, Number],
    default: 124
  },
  height: {
    type: [String, Number],
    default: 38
  }
})
</script>
