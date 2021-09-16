/*
 * @Author: your name
 * @Date: 2021-06-13 15:11:41
 * @LastEditTime: 2021-06-13 15:41:38
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp_fontend/src/stores/reduxStore.js
 */

import { createStore } from "redux";
import reducer from "./reducer";
const store = createStore(reducer);

export default store;