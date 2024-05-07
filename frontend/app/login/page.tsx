'use client';

import styles from '../page.module.css';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const router = useRouter();

    //ログインボタンをクリックしたときの処理
    const handleLogin = async (e:any) => {
        e.preventDefault()

        try {
            const response = await axios.post('http://13.211.73.90:5000/login',{
                username: username,
                password: password
            });
            //ログイン成功時の処理
            console.log('Login successful:', response.data);
            const userId = response.data.user_id;
            router.push(`../mypage/${userId}`);
        } catch (error:any) {
            //ログイン失敗時の処理
            console.error('Login failed:', error.response.data);
            setErrorMessage('ユーザー名またはパスワードが正しくありません');
        }
    };

    return (
        <div className={styles.login}>
            <h1>ログイン</h1>
            {errorMessage && <p className={styles.error_message}>{errorMessage}</p>}
            <form onSubmit={handleLogin}>
                <div className={styles.form_group}>
                    <label>ユーザー名</label>
                    <input 
                    className={styles.username} 
                    type="text" placeholder="Username" 
                    value={username} 
                    onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div className={styles.form_group}>
                    <label>パスワード</label>
                    <input 
                    className={styles.password} 
                    type="password" placeholder="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <button type="submit">ログイン</button>
            </form>
        </div>
    );

};

export default Login;