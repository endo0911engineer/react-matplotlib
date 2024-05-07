import Link from "next/link";
import styles from './page.module.css';

const home  = () => {
  return (
    <div className={styles.home}>
      <h1>My Healthcare</h1>
      <Link href="./register">
        Register
      </Link>
      <Link href="./login">
        Login
      </Link>
    </div>
  )
};

export default home;
