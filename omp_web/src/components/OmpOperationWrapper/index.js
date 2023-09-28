import styles from "./index.module.less"
const OmpOperationWrapper = (props)=>{
    return (
       <div className={styles.OmpOperationWrapper}>
           {props.children}
       </div>
    )
}

export default OmpOperationWrapper