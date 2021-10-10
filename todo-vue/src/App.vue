<template>
  <div id="app">
    <TodoList />
    <PostNote />
  </div>
</template>

<script>
import TodoList from './components/TodoList.vue'
import PostNote from './components/PostNote.vue'
export default {
  name: 'App',
  components: {
    TodoList,
    PostNote
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
