// src/pages/Login.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client.ts";

export default function Login() {
  const [email, setEmail] = useState("you@example.com");
  const [password, setPassword] = useState("Pass1234");
  const [error, setError] = useState("");
  const nav = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const body = new URLSearchParams();
      body.append("grant_type", "password");
      body.append("username", email);
      body.append("password", password);

      const resp = await api.post("/auth/login", body.toString(), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      localStorage.setItem("access_token", resp.data.access_token);
      nav("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="w-full max-w-md bg-white p-6 rounded shadow">
        <h1 className="text-2xl mb-4">SmartDues — Login</h1>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <label className="block mb-2">
          <span className="text-sm">Email</span>
          <input value={email} onChange={e => setEmail(e.target.value)} className="mt-1 block w-full p-2 border rounded" />
        </label>
        <label className="block mb-4">
          <span className="text-sm">Password</span>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1 block w-full p-2 border rounded" />
        </label>
        <button type="submit" className="w-full py-2 bg-blue-600 text-white rounded">Login</button>
      </form>
    </div>
  );
}
