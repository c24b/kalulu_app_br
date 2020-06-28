<template>
<div>
{{title}}

{{message}}
    
</div>
</template>

<script>
export default {
    
    props: [
    'title',
    'message',
    
  ]
}
//     computed: {
//         trim_msg: function() {
//             return this.message.split('.')[0]
//         }
//     },
//     props: [
//         'title',
//         'message'
//     ]
// }
</script>

<style>
</style>