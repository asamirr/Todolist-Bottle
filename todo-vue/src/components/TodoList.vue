<template>
    <div>
        <h1>Todooooo</h1>
        <table border='3px'> 
            <tr>
                <td>Description</td>
                <td>Summary</td>  
                <td>Modified date</td>

                <td>Due date</td>              
            </tr>
            <tr v-for='item in list' v-bind:key="item.id">
                <td> {{item.description}} </td>
                <td> {{item.summary}} </td>
                <td> {{item.modified}} </td>
                <td> {{item.duedate}} </td>
                
            </tr> 
        </table>
    </div>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';

Vue.use(VueAxios, axios)

export default {
    name: "TodoList",
    data(){
        return {list:undefined}
    },

    mounted(){
        Vue.axios.get(process.env.VUE_APP_BASE_URL)
        .then((resp)=>{
            this.list=resp.data.data;
            console.warn(resp.data.data)
        })
    }
}
</script>