import React, { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import UserPage from './pages/UserPage';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/user/" element={<UserPage/>} />
      </Routes>
    </Router>
  );
}

export default App
