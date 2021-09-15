/*
 * @Author: your name
 * @Date: 2021-06-25 19:24:10
 * @LastEditTime: 2021-06-25 19:48:03
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp-fontend123/src/components/OmpOperationWrapper/index.js
 */
import styles from "./index.module.less"
const OmpOperationWrapper = (props)=>{
    return (
       <div className={styles.OmpOperationWrapper}>
           {props.children}
       </div>
    )
}

export default OmpOperationWrapper