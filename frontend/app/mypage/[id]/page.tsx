'use client'

import styles from '../../page.module.css';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const Mypage = ({params}:any) => {
  const [weight, setWeight] = useState('');
  const [sleepHours, setSleepHours] = useState('');
  const [averageWeight, setAverageWeight] = useState('');
  const [averageSleepHours, setAverageSleepHours] = useState('');
  const [imageSrc, setImageSrc] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchAverageData = async () => {
      try {
        const response = await axios.get('http://13.211.73.90:5000/average_data', { params: { user_id: params.id }});
        const { average_weight, average_sleep_hours } = response.data;
        setAverageWeight(average_weight);
        setAverageSleepHours(average_sleep_hours);
      } catch (error) {
        console.error('Error fetching average data:', error);
      }
    };
    fetchAverageData();
  }, [params.id]);

  const handleSaveData = async () => {
    try {
      await axios.post('http://13.211.73.90:5000/save_data', { weight: weight, sleep_hours: sleepHours, user_id: params.id });
      console.log('Data saved successfully');
      setErrorMessage('');
    } catch (error:any) {
      console.error('Error saving data:', error.response.data.message);
      setErrorMessage(error.response.data.message);
    }
  };

  const handleVisualize = async () => {
    try {
      const response = await axios.get('http://13.211.73.90:5000/visualize', {params: { user_id: params.id }});
      const imageUrl = response.data.image;
      console.log('Visualization received:', imageUrl);
      setImageSrc(`data:image/png;base64,${imageUrl}`);
    } catch (error) {
      console.error('Error fetching visualization:', error);
    }
  };

  const handleLogout = async () => {
    try {
        await axios.get('http://13.211.73.90/logout');
        console.log('Logged out successfully');
        router.push('../../')
    } catch(error) {
        console.error('Error logging out', error);
    }
  }

  return (
    <div>
    <div className={styles.mypage}>
      <div className={styles.input_group}>
        <label>体重</label>
        <input
        className={styles.weight} 
        type="number"
        value={weight}
        onChange={(e) => setWeight(e.target.value)}
        placeholder="Weight" 
        />
      </div>
      <div className={styles.input_group}>
        <label>睡眠時間</label>
        <input className={styles.sleepHours}
        type="number"
        value={sleepHours}
        onChange={(e) => setSleepHours(e.target.value)}
        placeholder="Sleep Hours" 
        />
      </div>
      <div className={styles.button_panel}>
        <button onClick={handleSaveData}>今日のデータを保存する</button>
        <button onClick={handleVisualize}>グラフを描画する</button>
        <button onClick={handleLogout}>Logout</button>
      </div>
      {errorMessage && <p className={styles.error_message}>{errorMessage}</p>}
    </div>
    <div className={styles.average_data}>
      <p>過去一か月の平均体重：{averageWeight} kg</p>
      <p>過去一か月の平均睡眠時間：{averageSleepHours} 時間</p>
    </div>
    {imageSrc && <img className={styles.visualization} src={imageSrc} alt="Visualization"/>}
    </div>
  );
};

export default Mypage;