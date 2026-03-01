import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux';
import { Provider, useDispatch, useSelector } from 'react-redux';

// Redux logic
const reducer = (state = { tasks: [] }, action) => {
  switch (action.type) {
    case 'SET': return { tasks: action.payload };
    case 'ADD': return { tasks: [...state.tasks, action.payload] };
    case 'DEL': return { tasks: state.tasks.filter(t => t._id !== action.payload) };
    default: return state;
  }
};
const store = createStore(reducer);

const App = () => {
  const [text, setText] = useState('');
  const tasks = useSelector(state => state.tasks);
  const dispatch = useDispatch();

  useEffect(() => {
    fetch('http://localhost:5000/api/tasks')
      .then(res => res.json())
      .then(data => dispatch({ type: 'SET', payload: data }));
  }, []);

  const addTask = async () => {
    if (!text) return;
    const res = await fetch('http://localhost:5000/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, priority: 'Normal' })
    });
    const newTask = await res.json();
    dispatch({ type: 'ADD', payload: newTask });
    setText('');
  };

  const delTask = async (id) => {
    await fetch(`http://localhost:5000/api/tasks/${id}`, { method: 'DELETE' });
    dispatch({ type: 'DEL', payload: id });
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>Список задач ✅</h1>
      <input value={text} onChange={e => setText(e.target.value)} placeholder="Что сделать?" />
      <button onClick={addTask}>Добавить</button>
      <hr />
      <ul>
        {tasks.map(t => (
          <li key={t._id}>
            {t.text} <button onClick={() => delTask(t._id)}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

ReactDOM.render(<Provider store={store}><App /></Provider>, document.getElementById('root'));
