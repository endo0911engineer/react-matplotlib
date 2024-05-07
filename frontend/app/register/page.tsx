'use client';

import styles from '../page.module.css'
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordMatchError, setPasswordMatchError] = useState(false);
    const router = useRouter();

    //ユーザー登録ボタンを押したときの処理
    const handleRegister = async (e:any) => {
        e.preventDefault();

        // 確認用パスワードとパスワードの一致を確認
        if (password !== confirmPassword) {
            setPasswordMatchError(true);
            return; // パスワードが一致しない場合は処理を中断
        } else {
            setPasswordMatchError(false);
        }

        try {
            const response = await axios.post('http://13.211.73.90:5000/register',{
                username: username,
                password: password
            });
            //ログイン成功時の処理
            console.log('Register successful:', response.data);
            router.push('../login');
        } catch (error:any) {
            //ログイン失敗時の処理
            console.error('Register failed:', error.response.data);
        }
    };

    return (
        <div className={styles.register}>
        <h1>ユーザー登録</h1>
        <form onSubmit={handleRegister}>
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
            <div className={styles.form_group}>
                    <label>パスワード（確認）</label>
                    <input 
                        className={`${styles.password} ${passwordMatchError ? styles.password_error : ''}`} 
                        type="password" 
                        placeholder="確認用 Password" 
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                    {passwordMatchError && <span className={styles.error_message}>パスワードが一致しません</span>}
            </div>
            <button type="submit">登録する</button>
        </form>
    </div>
    );

};

export default Register;