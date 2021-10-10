<template>
    <div>
        <form @submit="postData" method="post">
            <input type="text" name="desc" placeholder="Note Description" v-model="tasks.description"> <br>
            <input type="text" name="summary" placeholder="Note Summary" v-model="tasks.summary"> <br>
            <input type="text" name="duedate" placeholder="Due Date" v-model="tasks.duedate"> <br>
            <input type="text" name="status" placeholder="Status" v-model="tasks.status_id"> <br>
            <button type="submit">Post Note</button>
        </form>
    </div>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';

Vue.use(VueAxios, axios)

export default {
    name: "PostNote",
    data(){
        return {
            tasks:{
                description:null,
                summary:null,
                duedate:null,
                status_id:null
            }
        }
    },

    methods:{
        postData(e){
            this.axios.post("http://localhost:8000/task", this.tasks)
            .then((result)=>{
                console.warn(result)
            })
            e.preventDefault();
        }
    },
}
</script>