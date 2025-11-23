// src/components/Navbar.tsx
import { Link, useNavigate } from "react-router-dom";

// src/components/Navbar.tsx
export default function Navbar(){
  const nav = useNavigate();
  function logout(){ localStorage.removeItem("access_token"); nav("/login"); }
  return (
    <nav className="bg-white shadow-sm p-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <Link to="/dashboard" className="font-bold text-lg text-sky-700">SmartDues</Link>
        <Link to="/bills" className="text-sm text-gray-600 hover:underline">Bills</Link>
      </div>
      <div>
        <button onClick={logout} className="px-3 py-1 border rounded text-sm">Logout</button>
      </div>
    </nav>
  );
}
